# Mami AI - Advanced Autonomous Personal Assistant

Mami AI is a next-generation personal AI assistant designed with a focus on autonomy, long-term memory (GraphRAG), and a SaaS-ready architecture.

## 🚀 Vision

- **Autonomous:** Capable of executing file operations and commands on the user's machine via a secure Desktop Client.
- **Memory:** Utilizes Neo4j for Knowledge Graph and ChromaDB for Vector Memory to maintain a deep context of the user's life.
- **SaaS-Ready:** Built with multi-tenancy, rate limiting, and subscription management in mind.

## 🏗 Architecture

### Backend (Python/FastAPI)
- **Framework:** FastAPI (Async, High Performance)
- **Database:** PostgreSQL (User Data, Relational)
- **Vector DB:** ChromaDB (Conversation History)
- **Graph DB:** Neo4j (Knowledge Graph - Facts & Relations)
- **Cache/Broker:** Redis (Celery Broker, Caching)
- **AI Models:** Groq (Llama 3), Gemini (Vision/Analysis), OpenAI (Coding) via LangChain/LangGraph.
- **Search:** Serper API

### Frontend (Next.js)
- **Framework:** Next.js + Tailwind CSS
- **Features:** Chat Interface, Artifacts Panel, Dashboard, PWA support.

### Desktop Client (Python)
- **Role:** Secure execution bridge for local commands and file manipulation.
- **Communication:** WebSockets (Securely connected to Backend).

## 🛠 Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.10+ (for local backend/desktop dev)

### Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/warhack811/mami-ai.git
    cd mami-ai
    ```

2.  **Configure Environment:**
    Copy the example environment file and fill in your API keys (Groq, Gemini, Serper).
    ```bash
    cp .env.example .env
    ```

3.  **Start with Docker:**
    ```bash
    docker-compose up -d --build
    ```
    This will start:
    - Backend API at `http://localhost:8000`
    - Frontend at `http://localhost:3000`
    - Neo4j, Postgres, Redis, ChromaDB

4.  **Access Documentation:**
    - API Docs: `http://localhost:8000/docs`

## 🛡 Security
- **API Key Rotation:** Automatically manages API limits.
- **Sandboxed Execution:** Desktop client restricts file access to safe directories.
- **Data Encryption:** Sensitive user data is encrypted at rest.

## 📄 License
MIT
