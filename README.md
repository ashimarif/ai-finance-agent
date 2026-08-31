# 💸 Autonomous Personal Finance & Bill-Splitting Agent

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-orange?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Google Gemini](https://img.shields.io/badge/Gemini%202.0%20Flash-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

An end-to-end, multi-container AI agent designed to automate personal expense tracking, dynamic group bill calculations, debt tracking (IOUs), and settlements using conversational natural language. 

Built on a cyclical **LangGraph** orchestration graph powered by **Gemini 2.0 Flash**, backed by an ACID-compliant **PostgreSQL** relational database, exposed via high-performance **FastAPI** REST endpoints, and served through an interactive **Streamlit** user interface.

---

## 🌟 Key Features

- 🧠 **Autonomous Financial Intent Parsing:** Understands natural language statements, categorizes spending (Food, Transport, Utilities, etc.), and extracts dynamic multi-person cost breakdowns without rigid forms.
- 👥 **Group Bill-Splitting & Debt Engine:** Automatically calculates individual shares, assigns proportional obligations, and creates linked relational debts in PostgreSQL.
- 📋 **IOU & Balance Tracking:** Queries active debts, groups obligations by debtor, and calculates total outstanding balances across past outings.
- 🤝 **One-Shot Debt Settlement:** Settles outstanding debts per person via conversational command with automatic database row updates.
- 🔄 **Stateful Conversational Memory:** Maintains multi-turn context across queries using thread-isolated session memory.
- 🐳 **Microservices Architecture:** Fully containerized multi-tier stack (Database, API Engine, Frontend UI) orchestrated with Docker Compose and internal container networking.

## 🛠️ Tech Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **LLM & Reasoning** | Google Gemini 2.0 Flash | Natural language reasoning, schema extraction, tool parameter generation |
| **Agent Framework** | LangGraph & LangChain Core | Cyclical state graph execution, memory checkpoints, conditional tool routing |
| **Backend API** | FastAPI, Uvicorn, Pydantic | Asynchronous REST endpoints, strict schema validation, Swagger documentation |
| **Database** | PostgreSQL 16, `psycopg` (v3) | Relational storage for personal expenses, outings, and IOU ledger |
| **Frontend UI** | Streamlit | Chat interface with session-state thread tracking and real-time status monitors |
| **DevOps & Deploy** | Docker, Docker Compose | Isolated multi-container deployment, health check triggers, volume persistence |

---

## 📂 Project Structure

```text
├── app/
│   ├── __init__.py
│   ├── database.py         # PostgreSQL connection pool & schema initialization
│   ├── tools.py            # LangChain tool implementations (Expense, Split, IOU, Settle)
│   ├── schemas.py          # Pydantic validation models for API request/response
│   ├── agent.py            # LangGraph state machine, nodes, and Gemini integration
│   └── main.py             # FastAPI application routes, CORS, and endpoint handlers
├── streamlit_app.py        # Streamlit interactive chat UI
├── Dockerfile.api          # Container definition for FastAPI backend
├── Dockerfile.frontend     # Container definition for Streamlit frontend
├── docker-compose.yml      # Orchestration definition for Database, API, and UI services
├── requirements.txt        # Python dependency manifest
├── .env.example            # Environment variable template
└── README.md               # Project documentation

## 🗄️ Database Schema Design

The relational database enforces financial accuracy with `NUMERIC(10, 2)` types and relational integrity constraints:

```sql
-- 1. Personal Solo Expenses
CREATE TABLE personal_expenses (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Group Outing Receipts
CREATE TABLE group_bills (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    payer VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Individual Debts / IOUs (Linked via Foreign Key)
CREATE TABLE iou_records (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES group_bills(id) ON DELETE CASCADE,
    debtor_name VARCHAR(100) NOT NULL,
    amount_owed NUMERIC(10, 2) NOT NULL,
    is_settled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

```
