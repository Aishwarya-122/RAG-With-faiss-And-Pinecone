# Combined RAG — FAISS + Pinecone

This is one Streamlit RAG application that demonstrates both FAISS and Pinecone retrieval using the same Sentence Transformer model and the same employee-policy Q&A dataset.

## Modes
- FAISS: local/in-memory vector retrieval with FAISS IndexFlatL2.
- Pinecone: cloud vector retrieval using a Pinecone index.
- Compare Both: runs the same query against both vector stores and displays their results.

## Run locally

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
# source venv/bin/activate

pip install -r requirements.txt
streamlit run combined_app.py
```

## Pinecone
Set `PINECONE_API_KEY` as an environment variable or enter it in the Streamlit sidebar.
Never hardcode or commit the API key.

## AWS
The application can be hosted on an EC2 instance. FAISS runs in the application process; Pinecone remains a cloud-hosted vector database.
