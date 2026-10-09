# AWS EC2 Deployment Guide — Combined RAG (FAISS + Pinecone)

## 1. Project Overview

This project is a document-based retrieval application built using Python, Sentence Transformers, FAISS, Pinecone, and Streamlit. It was deployed on an Ubuntu server hosted on Amazon EC2.

**GitHub Repository:** https://github.com/Aishwarya-122/RAG-With-faiss-And-Pinecone

### Technologies Used

- Python
- Streamlit
- Sentence Transformers
- FAISS vector index
- Pinecone vector database
- Git and GitHub
- AWS EC2
- Ubuntu Linux

## 2. Deployment Architecture

```text
GitHub Repository
       |
       v
AWS EC2 Instance (Ubuntu)
       |
       v
Python Virtual Environment
       |
       v
Streamlit Application
       |
       +------------------+
       |                  |
       v                  v
     FAISS             Pinecone
  Local Retrieval    Cloud Retrieval
       |                  |
       +--------+---------+
                |
                v
        Retrieved Results
```

## 3. Step 1: Create an AWS EC2 Instance

1. Sign in to the AWS Management Console.
2. Navigate to EC2 → Instances.
3. Click Launch instances.
4. Set the instance name to `RAG-FAISS-Pinecone`.
5. Select Ubuntu Server as the operating system.
6. Select the `t3.small` instance type.
7. Configure a key pair for SSH access and store the private key securely.
8. Configure storage and enable a public IPv4 address.
9. Create a security group.
10. Launch the instance.

The instance was created in the Asia Pacific (Mumbai) region.

## 4. Step 2: Configure the Security Group

The following inbound rules were configured:

| Type | Port | Purpose |
|---|---:|---|
| SSH | 22 | Remote server access |
| Custom TCP | 8501 | Streamlit application access |

SSH access was restricted to the appropriate source. An AWS-managed EC2 Instance Connect prefix list was added to allow browser-based SSH access.

For personal testing, restrict port 8501 to trusted IP addresses. For a public production deployment, use appropriate network restrictions and HTTPS.

## 5. Step 3: Connect to the EC2 Instance

1. Navigate to EC2 → Instances.
2. Select `RAG-FAISS-Pinecone`.
3. Click Connect.
4. Select EC2 Instance Connect.
5. Connect to the Ubuntu terminal.

The terminal displayed an Ubuntu prompt similar to:

```bash
ubuntu@ip-172-31-13-236:~$
```

## 6. Step 4: Update Ubuntu and Install Dependencies

Update the package lists:

```bash
sudo apt update
```

Install Python, pip, virtual environment support, and Git:

```bash
sudo apt install python3 python3-pip python3-venv git -y
```

Verify the installations:

```bash
python3 --version
pip3 --version
git --version
```

## 7. Step 5: Clone the GitHub Repository

Download the project from GitHub:

```bash
git clone https://github.com/Aishwarya-122/RAG-With-faiss-And-Pinecone.git
```

Navigate to the project directory:

```bash
cd RAG-With-faiss-And-Pinecone
```

Verify the project files:

```bash
ls
```

The directory contains files such as `combined_app.py`, `requirements.txt`, `Employee.txt`, and `README.md`.

## 8. Step 6: Create a Python Virtual Environment

Create the virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

The terminal prompt should begin with `(venv)`.

## 9. Step 7: Install Python Requirements

Install the project dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Installation Challenge

During installation, a disk quota error occurred while downloading large machine-learning dependencies, including PyTorch.

The filesystem was inspected using:

```bash
df -h
```

The pip cache was cleared:

```bash
pip cache purge
```

The installation was then retried using a temporary directory on the main filesystem:

```bash
mkdir -p ~/pip-temp
export TMPDIR=$HOME/pip-temp
pip install --no-cache-dir -r requirements.txt
```

The installation completed successfully.

Verify Streamlit:

```bash
streamlit --version
```

## 10. Step 8: Configure Pinecone Credentials

Pinecone credentials must be configured securely and must not be committed to GitHub.

Create the environment file:

```bash
nano .env
```

Add the configuration expected by the application:

```text
PINECONE_API_KEY=YOUR_PINECONE_API_KEY
PINECONE_INDEX_NAME=rag-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

Replace the placeholder privately with the actual API key.

Save the file, then restrict its permissions:

```bash
chmod 600 .env
```

The `.env` file must remain excluded from Git using `.gitignore`.

Never upload API keys or AWS private SSH keys to GitHub.

## 11. Step 9: Run the Streamlit Application

From the project directory, with the virtual environment activated, run:

```bash
streamlit run combined_app.py --server.address 0.0.0.0 --server.port 8501
```

The application starts on port `8501`.

Keep the terminal session running while using the application.

## 12. Step 10: Access the Deployed Application

Open a browser and visit:

```text
http://EC2_PUBLIC_IP:8501
```

Replace `EC2_PUBLIC_IP` with the current public IPv4 address of the EC2 instance.

The application provides three retrieval modes:

- **FAISS:** Local/in-memory vector retrieval.
- **Pinecone:** Cloud vector retrieval.
- **Compare Both:** Compare the results from both retrieval approaches.

Upload the employee dataset and test queries to verify retrieval.

## 13. Challenges Faced and Solutions

### Challenge 1: EC2 Instance Connect Failed

**Problem:** The browser-based SSH connection initially failed.

**Solution:** The EC2 security group was updated to include the regional EC2 Instance Connect prefix list for SSH access.

### Challenge 2: Incorrect Terminal Command

**Problem:** Two commands were accidentally entered together, causing an invalid operation error.

**Solution:** The correct Ubuntu command was run separately.

### Challenge 3: Disk Quota Error During Package Installation

**Problem:** Installing large machine-learning dependencies failed with a disk quota error.

**Solution:** Disk usage was inspected, the pip cache was cleared, and pip was configured to use a temporary directory on the main filesystem. The dependencies were then installed successfully.

### Challenge 4: Secure API Key Management

**Problem:** Pinecone requires an API key for cloud vector database access.

**Solution:** The key was configured privately on the server instead of being hardcoded into the Python source code or committed to GitHub.

## 14. Important Deployment Notes

- The application runs on an AWS EC2 Ubuntu instance.
- The Streamlit server must be running for the website to be accessible.
- The public IP can change after stopping and starting the instance unless a stable address is configured.
- FAISS uses a local/in-memory index in this application.
- Pinecone provides cloud-based vector storage and retrieval.
- This project demonstrates the retrieval component of RAG; it does not currently implement LLM answer generation.
- The current launch method uses an interactive terminal. Automatic service startup and production HTTPS configuration are separate improvements.

## 15. Conclusion

The Combined RAG application was successfully deployed on AWS EC2. The process involved creating the cloud instance, configuring network access, cloning the GitHub repository, setting up the Python environment, installing dependencies, configuring Pinecone credentials, and launching Streamlit on port 8501.

This deployment demonstrates practical experience with Python application deployment, Linux commands, Git, cloud hosting, network security groups, and vector database integration.
