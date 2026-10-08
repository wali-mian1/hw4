# Campus Customs Shop + Chatbot

Campus Customs is a React + Vite + TypeScript storefront with a FastAPI/PydanticAI shopping assistant. The source is organized for the HW 4 submission layout:

```text
hw4/
├── AI_prompts.md
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── frontend/                 # Vite React TypeScript app
├── backend/                  # FastAPI app and PydanticAI agent
└── output/                   # harness, design, usability, app check, audit trail
```

## Local data pack

The course-provided `campus_customs.db` and `data/products/` images are intentionally excluded from GitHub. Place the local data pack at:

```text
data/campus_customs.db
data/products/<catalogue images>
```

Do not commit the real `.env`, database, or product images. Copy `.env.example` to `.env` and add the course `PORTKEY_API_KEY` locally.

## Run the backend

From `hw4/backend/`:

```bash
../.venv/bin/uvicorn main:app --reload --port 8000
```

The API is available at `http://127.0.0.1:8000`. Health is at `/api/health`; catalogue data is served at `/api/products`; chat is served at `/api/chat`.

## Run the frontend

From `hw4/frontend/`:

```bash
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://127.0.0.1:5173/`. The frontend uses the FastAPI service for products, images, authentication, chat, and saved signed-in chat history.

## Verify the build

```bash
cd frontend
npm run build
```

See `output/harness.md` for the complete architecture, model fields, tools, safety rules, limits, audit trail, and API flow. See `output/app_check.html` for live-site evidence.
