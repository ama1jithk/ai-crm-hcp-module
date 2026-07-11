<<<<<<< HEAD
# AI-First CRM — HCP Module: Log Interaction Screen

A Log Interaction screen for pharma field reps to record Healthcare Professional (HCP)
interactions either through a **structured form** or a **conversational chat interface**
backed by a **LangGraph** agent running on **Groq (`gemma2-9b-it`)**.

## Stack
- **Frontend:** React + Redux Toolkit, Tailwind CSS, Google Inter font
- **Backend:** Python, FastAPI
- **Agent framework:** LangGraph (`langgraph`, `langchain-groq`)
- **LLMs:** Groq `gemma2-9b-it` (primary — extraction/summarization/chat), Groq
  `llama-3.3-70b-versatile` (used for the "suggest next best action" tool)
- **Database:** PostgreSQL or MySQL via SQLAlchemy + Alembic migrations

See [`docs/AGENT_TOOLS.md`](docs/AGENT_TOOLS.md) for a full breakdown of the LangGraph
agent's role and its five tools.

## Project structure
```
ai-crm-hcp-module/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph state, tools, graph, LLM wrapper
│   │   ├── routers/        # hcps, interactions, chat REST endpoints
│   │   ├── main.py
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── database.py
│   │   └── config.py
│   ├── alembic/            # DB migrations
│   ├── seed.py             # demo HCP seed data
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/     # LogInteractionScreen, StructuredForm, ChatInterface, ...
│   │   ├── store/          # Redux slices: hcps, interactions, chat
│   │   ├── api/client.js
│   │   └── App.jsx / main.jsx / index.css
│   ├── package.json
│   └── .env.example
└── docs/
    └── AGENT_TOOLS.md
```

## How the screen works
1. Pick an HCP from the left panel — their profile and interaction history load.
2. Choose **Conversational** (default) or **Structured Form** to log a new interaction.
   - *Conversational*: type a free-text note; the FieldMate LangGraph agent parses it,
     calls `log_interaction`, and can also `edit_interaction`, `schedule_follow_up`,
     `get_hcp_profile`, or `suggest_next_best_action` in the same chat — each tool call
     is shown as an expandable badge under the agent's reply.
   - *Structured Form*: fill discrete fields (type, sentiment, topics, products,
     samples, follow-up) and submit directly.
3. Both paths write to the same `interactions` table and immediately refresh the
   history panel.

## Setup

### 1. Database
Create a Postgres (or MySQL) database and user, e.g.:
```bash
createdb hcp_crm
psql hcp_crm -c "CREATE USER crm_user WITH PASSWORD 'crm_password'; GRANT ALL PRIVILEGES ON DATABASE hcp_crm TO crm_user;"
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in GROQ_API_KEY and DATABASE_URL
alembic upgrade head            # creates tables via migrations
python seed.py                  # optional: adds 3 demo HCPs
uvicorn app.main:app --reload --port 8000
```
Backend runs at `http://localhost:8000`, docs at `http://localhost:8000/docs`.

> `Base.metadata.create_all()` in `app/main.py` also auto-creates tables on first run,
> so `alembic upgrade head` is optional for a quick start but recommended for a real
> migration history.

### 3. Frontend
```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```
Frontend runs at `http://localhost:5173`.

### 4. Get a Groq API key
Create a free key at https://console.groq.com, set `GROQ_API_KEY` in `backend/.env`.

## Environment variables

**backend/.env**
```
DATABASE_URL=postgresql+psycopg2://crm_user:crm_password@localhost:5432/hcp_crm
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=gemma2-9b-it
GROQ_FALLBACK_MODEL=llama-3.3-70b-versatile
BACKEND_CORS_ORIGINS=http://localhost:5173
```

**frontend/.env**
```
VITE_API_BASE_URL=http://localhost:8000
```

## API summary
- `GET /api/hcps/` — list HCPs
- `POST /api/hcps/` — create HCP
- `GET /api/hcps/{id}/interactions` — HCP's interaction history
- `GET/POST /api/interactions/`, `PUT/DELETE /api/interactions/{id}`
- `POST /api/chat/` — send a message to the LangGraph agent (`session_id`, `message`, `hcp_id`)

## Notes
- Both entry paths (form + chat) share the same `Interaction` schema so data never
  diverges between them.
- The chat endpoint persists conversation turns per `session_id` so the agent has
  short-term memory across the visit.
=======
# ai-crm-hcp-module
>>>>>>> 1a68755868659943a591dd6e21e39c6782ead8fc
