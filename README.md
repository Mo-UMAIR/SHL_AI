<div align="center">
  <h1>🎯 SHL Assessment Recommender Agent</h1>
  <p><i>An intelligent conversational agent built for the SHL AI Intern Assignment.</i></p>
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
  [![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com/)
  [![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
</div>

---

## 📖 Overview

Hiring managers often struggle to find the exact assessment they need from vast catalogs. This project solves that by providing an **Agentic AI Recommender**. Instead of relying on keyword searches, the agent takes a user from a vague intent (e.g., *"I need a Java developer test"*) to a grounded, highly-relevant shortlist of SHL **Individual Test Solutions** through natural dialogue.

### Core Conversational Behaviors:
- 🔍 **Clarify**: Asks follow-up questions when the query is too vague.
- 🎯 **Recommend**: Provides 1-10 highly relevant assessments using a FAISS Vector Database.
- 🛠️ **Refine**: Dynamically updates the shortlist if the user changes constraints mid-conversation.
- ⚖️ **Compare**: Explains the difference between specific tests using grounded catalog data.
- 🛑 **Refuse**: Politely declines off-topic questions (e.g., legal advice, general hiring advice).

---

## 🏗️ Project Structure

```text
SHL_AI/
├── backend/
│   ├── agents/          # LangGraph state machine & LLM logic
│   ├── api/             # FastAPI endpoint routing (/chat, /health)
│   ├── data/            # Scraped catalog.json and raw data
│   ├── models/          # Pydantic schemas enforcing strict API compliance
│   ├── prompts/         # LLM instructions and intent classification
│   ├── vectorstore/     # FAISS similarity search implementation
│   └── main.py          # FastAPI application entry point
├── frontend/
│   ├── components/      # UI components (Assessment Cards)
│   └── app.py           # Interactive Streamlit interface
├── .env                 # Production container configuration
├── approach.md          # In-depth technical architecture document
├── README.md            # Project documentation
├── list_models.py       # Helper to verify Gemini API access
├── test_api.py          # Script for testing the API programmatically
└── requirements.txt     # Python dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key

### 2. Environment Variables
Update a `.env` file (use own gemini api key):
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Local Development (VS Code / Terminal)
Open your terminal and run the following commands:

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the FastAPI Backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Leave the backend running. Open a **new terminal** window, activate the environment again, and run the frontend:
```bash
# 4. Start the Streamlit Frontend
streamlit run frontend/app.py
```
*The frontend will be available at `http://localhost:8501` and the backend API at `http://localhost:8000`.*

---

## 🔌 API Specification

The core requirement of this assignment is a fully stateless API. 

### `GET /health`
Returns the readiness of the server.
```json
{"status": "ok"}
```

### `POST /chat`
Accepts a full stateless conversation history and returns the agent's reply and recommendations.
**Request Payload:**
```json
{
  "messages": [
    {"role": "user", "content": "Hiring a Java developer who works with stakeholders"},
    {"role": "assistant", "content": "Sure. What is seniority level?"},
    {"role": "user", "content": "Mid-level, around 4 years"}
  ]
}
```
**Response Payload:**
```json
{
  "reply": "Got it. Here are some assessments that fit a mid-level Java dev with stakeholder needs.",
  "recommendations": [
    {"name": "Java 8 (New)", "url": "https://www.shl.com/...", "test_type": "K"}
  ],
  "end_of_conversation": false
}
```

---

## 🐳 Deployment (Docker)

To deploy the backend API to any cloud provider (AWS EC2, Render, Railway, Fly.io):

```bash
# Build the Docker image
docker build -t shl-recommender .

# Run the container
docker run -p 8000:8000 -e GEMINI_API_KEY=your_api_key_here shl-recommender
```

---

## 📊 Evaluation & Architecture

Please refer to the [**approach.md**](./approach.md) file included in this repository for a detailed 2-page breakdown of:
- Design Choices (FastAPI + LangGraph)
- Retrieval Setup (FAISS + SentenceTransformers)
- Prompt Engineering & Intent Routing
- Flowchart of the system architecture
- What didn't work and how improvements were measured (Recall@10).
