import os
import tempfile
from pathlib import Path

import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec


st.set_page_config(
    page_title="Combined RAG - FAISS + Pinecone",
    page_icon="🔎",
    layout="wide",
)


MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-index")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")


@st.cache_resource
def load_model():
    return SentenceTransformer(MODEL_NAME)


def load_documents_from_bytes(file_bytes):
    """Read a two-line Q&A text file and combine each question with its answer."""
    text = file_bytes.decode("utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if len(lines) < 2:
        raise ValueError("The uploaded file must contain at least one question-answer pair.")

    if len(lines) % 2 != 0:
        raise ValueError("The uploaded file must contain an even number of non-empty lines: question, answer, question, answer...")

    return [f"{lines[i]} {lines[i + 1]}" for i in range(0, len(lines), 2)]


def generate_embeddings(documents, model):
    embeddings = model.encode(documents)
    return np.asarray(embeddings, dtype="float32")


def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def retrieve_faiss(query, model, index, documents, top_k=2):
    query_embedding = generate_embeddings([query], model)
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for rank, doc_index in enumerate(indices[0]):
        if doc_index == -1:
            continue
        results.append(
            {
                "rank": rank + 1,
                "text": documents[doc_index],
                "score": float(distances[0][rank]),
            }
        )
    return results


def get_pinecone_index(api_key, index_name, dimension):
    pc = Pinecone(api_key=api_key)

    existing_indexes = pc.list_indexes().names()

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=PINECONE_CLOUD,
                region=PINECONE_REGION,
            ),
        )

    return pc.Index(index_name)


def upload_to_pinecone(index, documents, embeddings):
    vectors = []
    for i, (document, embedding) in enumerate(zip(documents, embeddings)):
        vectors.append(
            {
                "id": str(i),
                "values": embedding.tolist(),
                "metadata": {"text": document},
            }
        )

    index.upsert(vectors=vectors)


def retrieve_pinecone(query, model, index, top_k=2):
    query_embedding = generate_embeddings([query], model)[0].tolist()

    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    results = []
    for rank, match in enumerate(response.get("matches", [])):
        metadata = match.get("metadata", {})
        results.append(
            {
                "rank": rank + 1,
                "text": metadata.get("text", ""),
                "score": float(match.get("score", 0.0)),
            }
        )

    return results


def show_results(title, results, score_label):
    st.subheader(title)

    if not results:
        st.info("No results found.")
        return

    for result in results:
        st.write(f"**Rank {result['rank']} | {score_label}: {result['score']:.4f}**")
        st.write(result["text"])
        st.markdown("---")


def main():
    st.title("🔎 Combined RAG — FAISS + Pinecone")
    st.caption(
        "One Streamlit application demonstrating two vector retrieval approaches "
        "using the same Sentence Transformer embeddings and the same employee-policy dataset."
    )

    with st.sidebar:
        st.header("Vector Database")
        mode = st.radio(
            "Choose retrieval mode",
            ["FAISS", "Pinecone", "Compare Both"],
        )

        st.markdown("### Pinecone configuration")
        pinecone_key = st.text_input(
            "Pinecone API Key",
            value=os.getenv("PINECONE_API_KEY", ""),
            type="password",
            help="Use an environment variable in AWS/GitHub instead of hardcoding the key.",
        )

        index_name = st.text_input(
            "Pinecone Index",
            value=DEFAULT_INDEX_NAME,
        )

        top_k = st.slider("Top K", min_value=1, max_value=5, value=2)

    uploaded_file = st.file_uploader(
        "Upload Employee.txt",
        type=["txt"],
    )

    if uploaded_file is None:
        st.info("Upload a two-line-per-Q&A .txt file to begin.")
        return

    try:
        documents = load_documents_from_bytes(uploaded_file.getvalue())
    except ValueError as exc:
        st.error(str(exc))
        return

    model = load_model()
    embeddings = generate_embeddings(documents, model)

    st.success(f"Loaded {len(documents)} Q&A records. Embedding dimension: {embeddings.shape[1]}")

    # FAISS is local/in-memory for this application run.
    faiss_index = create_faiss_index(embeddings)

    if mode in ["Pinecone", "Compare Both"]:
        if not pinecone_key:
            st.warning("Enter PINECONE_API_KEY in the sidebar to use Pinecone.")
        else:
            try:
                pinecone_index = get_pinecone_index(
                    pinecone_key,
                    index_name,
                    embeddings.shape[1],
                )

                if st.button("Upload Embeddings to Pinecone"):
                    upload_to_pinecone(pinecone_index, documents, embeddings)
                    st.success(f"Uploaded {len(documents)} vectors to Pinecone index '{index_name}'.")

            except Exception as exc:
                st.error(f"Pinecone initialization failed: {exc}")
                pinecone_index = None
    else:
        pinecone_index = None

    query = st.text_input("Ask a question", placeholder="Example: How many paid leaves do we get?")

    if not query:
        return

    if mode in ["FAISS", "Compare Both"]:
        faiss_results = retrieve_faiss(
            query,
            model,
            faiss_index,
            documents,
            top_k=top_k,
        )
        show_results(
            "🧩 FAISS Results",
            faiss_results,
            "L2 distance (lower is closer)",
        )

    if mode in ["Pinecone", "Compare Both"]:
        if pinecone_index is None:
            st.warning("Pinecone is not available. Enter a valid API key and initialize the index first.")
        else:
            try:
                pinecone_results = retrieve_pinecone(
                    query,
                    model,
                    pinecone_index,
                    top_k=top_k,
                )
                show_results(
                    "☁️ Pinecone Results",
                    pinecone_results,
                    "cosine similarity (higher is closer)",
                )
            except Exception as exc:
                st.error(f"Pinecone query failed: {exc}")


if __name__ == "__main__":
    main()
