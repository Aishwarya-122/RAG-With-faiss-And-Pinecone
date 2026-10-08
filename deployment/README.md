# AWS EC2 Deployment

This project is deployed as a Streamlit application on an AWS EC2 Ubuntu instance.

## Deployment Architecture

GitHub Repository
        ↓
AWS EC2
        ↓
Python Virtual Environment
        ↓
Streamlit
        ↓
RAG Application
        ↓
FAISS / Pinecone

## AWS Services Used

- Amazon EC2
- Security Groups
- EC2 Instance Connect

## EC2 Configuration

- OS: Ubuntu
- Instance Type: t3.small
- Region: Asia Pacific (Mumbai)
- Application Port: 8501

## Run the Application

```bash
source venv/bin/activate

streamlit run combined_app.py \
  --server.address 0.0.0.0 \
  --server.port 8501
