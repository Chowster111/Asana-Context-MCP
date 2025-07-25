# MCP ↔ Asana Context-Linker

A lightweight FastAPI service that lets you push “contexts” from your Model Context Protocol (MCP) server into Asana tasks as comments.  
It handles Asana OAuth, token persistence & refresh, fetching named contexts from MCP, and posting them to Asana via its Stories API.

---

## 🛠 Features

- **OAuth 2.0** flow with Asana  
- **Automatic token persistence & refresh** (no manual re-auth)  
- **`/asana/attach-context`** endpoint to:
  1. Load a valid Asana access token  
  2. Fetch a named context from your MCP server  
  3. Post it to an Asana task as a comment  
- **Health check** endpoint  
- **Graceful error handling** & structured logging  
- **Unit & integration tests** for token refresh, MCP fetch, and Asana post

---

## 📁 Project Layout

mcp-asana-integration/
├── backend/
│ ├── src/
│ │ ├── main.py # FastAPI app & routes
│ │ ├── config.py # Pydantic Settings
│ │ ├── logging.py # Logger setup
│ │ ├── mcp_client.py # MCPClient.fetch_context()
│ │ ├── asana/
│ │ │ ├── oauth.py # code↔token & refresh logic
│ │ │ ├── schemas.py # Pydantic models (AttachContextRequest, etc.)
│ │ │ ├── token_store.py # save/load/refresh tokens
│ │ │ └── init.py
│ ├── .env.example # TEMPLATE env vars
│ ├── Dockerfile # Containerize the service
│ └── requirements.txt
├── tests/
│ ├── test_oauth.py # refresh/token-exchange tests
│ ├── test_token_store.py # expired→refresh tests
│ └── test_attach_context.py # integration tests (MCP & Asana mocks)
├── docs/
│ └── asana-app-setup.md # Asana OAuth & webhook registration
├── .gitignore
├── README.md # ← you are here
└── docker-compose.yml # optional: local Redis/Postgres

yaml
Copy
Edit

---

## 🔧 Prerequisites

- **Python 3.10+**  
- **Asana developer account** (Client ID & Secret)  
- **HTTPS-accessible host** (e.g. via `ngrok` for local dev)  
- **MCP server** exposing `GET /contexts/{name}` → `{ "context_text": "..." }`

---

## 🚀 Getting Started

1. **Clone & install dependencies**

   ```bash
   git clone git@github.com:you/mcp-asana-integration.git
   cd mcp-asana-integration/backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
Configure environment

bash
Copy
Edit
cp .env.example .env
Populate .env with:

ini
Copy
Edit
MCP_SERVER_URL=https://your-mcp.example.com
ASANA_CLIENT_ID=<your-asana-client-id>
ASANA_CLIENT_SECRET=<your-asana-client-secret>
ASANA_REDIRECT_URI=https://your-domain.com/asana/oauth/callback
Run the service

bash
Copy
Edit
uvicorn src.main:app --reload --host 0.0.0.0 --port 3000
Expose to the internet (for Asana) via:

bash
Copy
Edit
ngrok http 3000
Register your Asana App

Follow docs/asana-app-setup.md to:

Register OAuth redirect URI

(Optional) Configure webhooks if you want event-driven behavior

Authorize & test

Visit:

php-template
Copy
Edit
https://app.asana.com/-/oauth_authorize?
  client_id=<YOUR_CLIENT_ID>&
  redirect_uri=<YOUR_REDIRECT_URI>&
  response_type=code
After granting access, Asana redirects to /asana/oauth/callback?code=… and you’ll see your tokens.

Call the attach endpoint:

bash
Copy
Edit
curl -X POST https://your-domain.com/asana/attach-context \
  -H "Content-Type: application/json" \
  -d '{
        "task_gid": "1234567890",
        "context_name": "design_notes"
      }'
A comment with your MCP context should appear on the specified Asana task.

✅ Testing
Unit tests:

bash
Copy
Edit
pytest tests/test_oauth.py tests/test_token_store.py
Integration tests (mocks MCP & Asana):

bash
Copy
Edit
pytest tests/test_attach_context.py
📦 Deployment
Build & run via Docker:

bash
Copy
Edit
docker build -t mcp-asana-integration .
docker run -d \
  -e MCP_SERVER_URL=… \
  -e ASANA_CLIENT_ID=… \
  -e ASANA_CLIENT_SECRET=… \
  -e ASANA_REDIRECT_URI=… \
  -p 3000:3000 \
  mcp-asana-integration
Or use docker-compose up if you need auxiliary services.

📖 Further Improvements
Add Asana webhook receiver to auto-attach contexts on specific task events

Support custom fields (instead of comments) for richer UI

Rate-limit & retry logic for MCP and Asana API calls

Deploy in Kubernetes with health-checks & auto-scaling

Publish as a public Asana Marketplace App