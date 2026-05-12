# SHL Assessment Recommender

This is a complete end-to-end conversational AI agent designed for the SHL AI Intern Assignment. It recommends SHL assessments through dynamic dialogue, rather than simple keyword search.

## Features

- **Agentic Conversation Flow**: Powered by LangGraph to clarify, recommend, refine, compare, and refuse.
- **RAG Pipeline**: Hybrid FAISS retrieval using Sentence Transformers (`all-MiniLM-L6-v2`).
- **Strict API Compliance**: `/chat` endpoint adheres rigidly to the requested JSON schema.
- **Beautiful Frontend**: Streamlit UI with clear assessment cards.
- **Deployment Ready**: Fully containerized with Docker and Nginx reverse proxy.

## Architecture

1. **Frontend**: Streamlit app that connects to the FastAPI backend.
2. **Backend**: FastAPI app (`main.py`) exposing `/health` and `/chat`.
3. **Agent State Machine**: LangGraph (`agents/graph.py`) categorizes intent via LLM (`gemini-1.5-flash`), retrieves FAISS context, and generates schema-compliant responses.
4. **Data Engine**: A custom scraper and processor fetches the exact JSON catalog and transforms it for the vector store.

## Local Setup

### 1. Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
```

### 2. Run with Docker Compose
```bash
docker-compose up --build
```
- Frontend available at: `http://localhost:8501`
- Backend API available at: `http://localhost:8000`

### 3. Run without Docker
**Prerequisites:** Python 3.10+
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Run frontend (in a new terminal)
streamlit run frontend/app.py
```

## AWS EC2 Deployment Guide

1. **Launch an EC2 Instance**: Choose Amazon Linux 2023 or Ubuntu 22.04. Enable HTTP/HTTPS in the Security Group.
2. **Install Docker & Git**:
```bash
sudo yum update -y
sudo yum install docker git -y
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
3. **Clone and Run**:
```bash
git clone <your-repo-url> shl-recommender
cd shl-recommender
echo "GEMINI_API_KEY=your_api_key_here" > .env
docker-compose up --build -d
```
4. Access via your instance's Public IPv4 address. Nginx routes port 80 to the Streamlit app and port 80/api/ to the backend.

## Evaluation
Run standard scripts to measure `Recall@10` against the provided conversational traces. The agent is strictly prompt-engineered to prevent hallucinations and rely solely on the FAISS index.
