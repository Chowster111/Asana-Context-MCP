# MCP ↔ Asana Context-Linker

A lightweight service and UI to let Asana tasks “attach” AI contexts from your MCP server as comments or custom fields.

## 🎯 Project Focus

- **OAuth 2.0** flows with Asana  
- **Webhooks** (optional) to react on task events  
- **Task-action UI** that lists MCP contexts for users to pick  
- **Comments API** to post selected context back into Asana

---

## 🔧 Prerequisites

- Node.js ≥ 16  
- An Asana developer account (Client ID & Secret)  
- HTTPS-accessible host (ngrok for local dev)

---

## 🚀 Quick Start

1. **Clone & install**  
   ```bash
   git clone git@github.com:you/mcp-asana-integration.git
   cd mcp-asana-integration
   npm install
````

2. **Configure env vars**

   ```bash
   cp .env.example .env
   # Fill in:
   # ASANA_CLIENT_ID=
   # ASANA_CLIENT_SECRET=
   # ASANA_REDIRECT_URI=
   # MCP_SERVER_URL=
   ```

3. **Run locally**

   ```bash
   npm start
   ```

   Expose via ngrok (if testing webhooks/UI):

   ```bash
   ngrok http 3000
   ```

4. **Register Asana App**
   See `docs/asana-app-setup.md` for OAuth callback URL and webhook setup.

5. **Install & test**

   * In Asana, add your App via “My Apps” → “Add to workspace”
   * Open any task, click “Apps” → your integration → pick a context

---

## 🗂️ File Structure

*(As shown above)*

---

## 📦 Deployment

* Build Docker image: `docker build -t mcp-asana .`
* Run with env vars or via `docker-compose up`

---

## 🔍 Testing

* **Unit tests**: `npm test`
* **Integration**: point at a mock Asana/MCP server and run `npm run test:integration`

---

## 📝 Contributing

PRs welcome! Please follow the existing code style and include tests for new features.

```
mcp-asana-integration/
├── backend/
│   ├── src/
│   │   ├── index.js               # Entry point: sets up Express server
│   │   ├── config.js              # Loads env vars (ASANA_CLIENT_ID, etc.)
│   │   ├── mcpClient.js           # gRPC/REST client to your MCP server
│   │   ├── asana/
│   │   │   ├── oauth.js           # Asana OAuth flow handlers
│   │   │   ├── routes.js          # /asana/* endpoints (app-launch, webhooks)
│   │   │   └── controller.js      # Business logic for posting stories/comments
│   │   └── utils/                 # Shared helpers (error handling, logging)
│   ├── package.json
│   ├── .env.example               # TEMPLATE for ASANA_CLIENT_ID, ASANA_CLIENT_SECRET, MCP_URL…
│   └── Dockerfile                 # Containerize your backend
│
├── frontend/
│   └── asana-ui/
│       ├── index.html             # Asana task-action UI
│       ├── script.js              # Calls backend to list contexts & attach
│       └── style.css
│
├── docs/
│   └── asana-app-setup.md         # How to register your Asana app & webhooks
│
├── tests/
│   ├── backend/                   # Jest/Mocha tests for controllers, utils
│   └── integration/               # Tests against a mock Asana + MCP
│
├── .gitignore
├── README.md                      # ← new: project overview, setup, deploy
└── docker-compose.yml             # Optional: local Redis/Postgres for tokens, etc.
```
