# Campus Customs Database Harness

## Purpose

This harness documents the database contract that the Campus Customs shop and chatbot can rely on. It records every application table and field, why each field matters, and the relationships that connect the tables. Later problems can extend this file with model, tool, safety, and application specifications.

## Database overview

Database file: `data/campus_customs.db`

| Table | Rows observed | Role |
| --- | ---: | --- |
| `catalogue` | 102 | The product catalogue: descriptions, searchable attributes, images, and prices. |
| `inventory` | 612 | Stock quantities for each catalogue product and size. |
| `users` | 3 | Registered shopper accounts and password hashes. |
| `chat_messages` | 22 | Persisted user/assistant conversation messages and matched-product payloads. |

`sqlite_sequence` is an internal SQLite bookkeeping table created for `AUTOINCREMENT` columns, rather than application data. It is not part of the shop/chatbot data contract.

## `catalogue`

One row represents one product. `product_id` is the stable identifier used to connect a product to its inventory rows.

| Field | SQLite type | Required / key | Why it matters |
| --- | --- | --- | --- |
| `product_id` | `TEXT` | Primary key | Stable product identifier for URLs, product cards, chatbot matches, and the `inventory` relationship. |
| `name` | `TEXT` | Required | Customer-facing product name used in listings, search results, and chatbot recommendations. |
| `garment_type` | `TEXT` | Required | Supports category filtering and helps the chatbot distinguish items such as hoodies, shirts, jackets, and sweatshirts. |
| `description` | `TEXT` | Required | Provides the product details the shop displays and the chatbot can use when explaining or recommending merchandise. |
| `colors` | `TEXT` | Required; stores JSON-array text | Represents available or advertised colors and supports color filtering and natural-language matching. |
| `search_tags` | `TEXT` | Required; stores JSON-array text | Holds searchable concepts such as school, garment style, logo, event, and color for product retrieval. |
| `image_file_path` | `TEXT` | Required | Points the frontend to the product image used on cards and recommendation results. |
| `price` | `REAL` | Required | Source of truth for displayed prices and chatbot answers about cost. |

Observed catalogue facts: prices range from `$32.00` to `$98.00`, with an average of `$58.48`. The stored image paths use the `products/...` pattern. The `colors` and `search_tags` columns are text representations of JSON arrays, so application code should parse them rather than treating the brackets as ordinary search text.

## `inventory`

One row represents the stock for one product-size combination. There are 612 rows: each of the 102 catalogue products has one row for each of six sizes (`S`, `M`, `L`, `XL`, `XS`, and `XXL`).

| Field | SQLite type | Required / key | Why it matters |
| --- | --- | --- | --- |
| `id` | `INTEGER` | Auto-incrementing primary key | Identifies an individual inventory record for database operations and updates. |
| `product_id` | `TEXT` | Required; foreign key to `catalogue.product_id` | Connects a size-specific stock record to the product whose name, image, and price should be shown. |
| `size` | `TEXT` | Required; part of unique key with `product_id` | Tells the shop and chatbot which size is available and lets them answer size-specific stock questions. |
| `quantity` | `INTEGER` | Required | Current units available; this is the source of truth for stock availability and should not be guessed by the chatbot. |

The table declares `UNIQUE (product_id, size)`, so a product-size pair should have at most one stock row. Observed quantities range from 0 to 25, with no negative quantities. A quantity of zero must be treated as out of stock. The foreign key prevents an inventory row from referring to an unknown catalogue product when foreign-key enforcement is enabled.

## `users`

One row represents one shopper account.

| Field | SQLite type | Required / key | Why it matters |
| --- | --- | --- | --- |
| `id` | `INTEGER` | Auto-incrementing primary key | Identifies the account and links a shopper to their saved chat messages. |
| `name` | `TEXT` | Required | Existing display name for account-related UI and personalized chatbot responses. |
| `email` | `TEXT` | Required; unique | Login/account identifier and contact identity; uniqueness prevents duplicate accounts for one email address. |
| `password_hash` | `TEXT` | Required | Stores a one-way password hash for authentication. The plaintext password must never be displayed, logged, or sent to the chatbot. |
| `created_at` | `TEXT` | Required; defaults to `datetime('now')` | Records account creation time for account metadata and auditing. |
| `first_name` | `TEXT` | Nullable | Optional first-name value for greetings and personalization when available. |
| `last_name` | `TEXT` | Nullable | Optional last-name value for account display and personalization when available. |

The database contains three users. The presence of both `name` and optional `first_name`/`last_name` means application code should define which value is the canonical display name and handle missing optional values safely.

## `chat_messages`

One row represents one persisted message in a user conversation. The observed data contains 11 `user` messages and 11 `assistant` messages.

| Field | SQLite type | Required / key | Why it matters |
| --- | --- | --- | --- |
| `id` | `INTEGER` | Auto-incrementing primary key | Preserves a stable ordering and identity for messages in conversation history. |
| `user_id` | `INTEGER` | Required; foreign key to `users.id` | Associates the message with the correct shopper and allows authenticated history retrieval. |
| `role` | `TEXT` | Required | Distinguishes the speaker, such as `user` or `assistant`, so the frontend can render the conversation correctly and the agent can reconstruct context. |
| `content` | `TEXT` | Required | Stores the actual user question or assistant response shown in the chat transcript. |
| `products_json` | `TEXT` | Nullable; stores JSON text | Stores product matches associated with a response so the frontend can display recommendation cards alongside the chat. |
| `created_at` | `TEXT` | Required; defaults to `datetime('now')` | Orders messages and records when the conversation event occurred. |

The database currently has 11 messages with a non-null `products_json` value. Application code should parse this JSON defensively and should validate `role` and the referenced `user_id` rather than trusting arbitrary client input.

## Relationships and application implications

```text
catalogue 1 ──── many inventory
   │
   └── product_id joins inventory.product_id

users 1 ──── many chat_messages
   │
   └── id joins chat_messages.user_id
```

- Product cards and chatbot recommendations should join `catalogue` to `inventory` when answering size-specific availability questions.
- Prices come from `catalogue.price`; quantities come from `inventory.quantity`. The agent should not invent either value.
- `chat_messages` belongs to authenticated users through `user_id`; it should not be used to expose one user's history to another user.
- The declared foreign keys are present, but the inspected SQLite connection reported `PRAGMA foreign_keys = 0`. The application should enable foreign-key enforcement on each connection.
- The database has unique indexes for `catalogue.product_id`, `inventory(product_id, size)`, and `users.email`.

## Initial validation notes

- No orphaned inventory rows were found.
- No duplicate product-size inventory pairs were found.
- No negative inventory quantities were found.
- No orphaned chat messages were found.
- All catalogue rows had non-empty values in the required product fields checked.

## Authentication harness

### Account creation

The frontend sends first name, last name, email, password, and password confirmation to `POST /api/auth/register`. The backend validates required fields, validates the email format, requires a password of at least eight characters, confirms that the two password fields match, normalizes the email to lowercase, and rejects duplicate email addresses.

New accounts are stored in `users` as follows:

- `name`: the combined first and last name for the existing required display-name field.
- `first_name` and `last_name`: the separately entered names for personalization.
- `email`: the normalized, unique login identifier.
- `password_hash`: a one-way PBKDF2-SHA-256 hash; the plaintext password is never stored.
- `created_at`: the database default timestamp.

### Password protection

The backend uses PBKDF2-HMAC-SHA-256 with 120,000 iterations, a fresh random URL-safe salt for every new account, and a constant-time digest comparison during login. Stored hashes use the format `pbkdf2_sha256$<salt>$<hex digest>`. The API never returns `password_hash`, and passwords are not logged or sent to the chatbot.

The supplied seed user uses the same `pbkdf2_sha256` format and is verified using the same 120,000-iteration check. An invalid password returns a generic error rather than revealing whether an email exists.

### Login and session behavior

The frontend sends email and password to `POST /api/auth/login`. On success, the backend returns a random opaque bearer token and a public user object. The frontend stores the token in browser local storage, sends it as an `Authorization: Bearer ...` header when checking `/api/auth/me`, and updates the navigation to show the signed-in user and a Log out action. `POST /api/auth/logout` invalidates the token in the backend's in-memory session map.

The current session map is intentionally a small assignment-stage implementation; a production deployment should use a durable session or signed-token strategy, HTTPS, rate limiting, and a secrets-managed session key.

### Verification completed

- Seed user login succeeded with the assignment-provided test credentials.
- A newly created user was inserted into a temporary copy of the database during testing.
- The new user's stored password began with `pbkdf2_sha256$`, not plaintext.
- The new user could log in successfully.
- An incorrect password was rejected with HTTP 401.
- The frontend TypeScript production build passed.

## PydanticAI agent harness

### Request flow

```text
React chat widget
        │ POST /api/chat { message }
        ▼
FastAPI app in backend/main.py
        │ await shop_agent.run(message)
        ▼
PydanticAI agent in backend/agent.py
        │ system prompt + Portkey model + catalogue tools
        ▼
ChatReply { reply, products[] }
        │
        ▼
Chat widget renders the reply and clickable product cards
```

The frontend sends JSON to `POST /api/chat`. FastAPI validates it with `ChatRequest`, runs the PydanticAI `shop_agent`, and returns a structured `ChatReply`. Product cards contain catalogue-backed IDs, names, prices, image URLs, colors, available sizes, and aggregate stock; the frontend turns those IDs into links to the existing product pages.

### Agent loading

- `backend/main.py` remains the Uvicorn entry point and exposes chat, product, image, and auth routes.
- `backend/agent.py` loads the root `.env` without printing or embedding the key, creates an OpenAI-compatible client routed through `https://api.portkey.ai/v1`, and selects `gpt-5.6-luna`.
- The agent loads `backend/prompts/prompt.md` as its system prompt and uses the structured `ChatReply` output type from `backend/models.py`.
- `backend/tools.py` exposes read-only catalogue search and product lookup tools. Tool results come from `catalogue` and `inventory`, so prices and stock are not invented by the model.
- `backend/models.py` defines `ProductCard`, `ChatRequest`, and `ChatReply`.
- The prompt defines Campus Customs voice, catalogue truthfulness, privacy boundaries, and read-only behavior.

### Runtime check

From `Homework/HW 4/backend`, run:

```bash
../.venv/bin/uvicorn main:app --reload --port 8000
```

This exact entry point imported successfully. Live smoke tests returned HTTP 200 for `/api/health`, returned all 102 catalogue products from `/api/products`, and returned HTTP 422 for an invalid empty chat payload as expected. A valid chat message invokes the configured AI model.

## Catalogue tools and structured lookup fields

The agent has four read-only tools in `backend/tools.py`. Each reads from `data/campus_customs.db`; none changes products, inventory, users, or chat history.

### `search_catalogue(query, limit=6)`

Searches the `catalogue` table across `name`, `garment_type`, `description`, `colors`, and `search_tags`. It returns up to six `ProductCard` results for recommendations.

The selected `ProductCard` fields are:

- `product_id`: stable ID used to link the recommendation to the frontend product page.
- `name` and `garment_type`: identify the item and garment category.
- `price`: the database-backed price shown in a recommendation.
- `description`: useful product context for the recommendation.
- `image_url`: lets the frontend render the matching product card.
- `colors`: supports color-aware recommendations.
- `available_sizes` and `total_stock`: summarize current inventory without guessing.

### `get_product(product_id)`

Fetches one product from `catalogue` and combines it with its `inventory` rows. It returns the compact `ProductCard` shape when the agent already knows a product ID.

### `lookup_product_info(product_id)`

Looks up exact product facts from `catalogue`. It returns `ProductInfo` with `product_id`, `name`, `garment_type`, `description`, `price`, `colors`, and `image_url`. These fields answer description, price, color, and image questions without exposing account or unrelated database fields.

### `lookup_stock(product_id, size=None)`

Looks up `inventory.product_id`, `inventory.size`, and `inventory.quantity`, joined to the catalogue product name. It returns `StockResult` with `product_id`, `product_name`, normalized `requested_size`, a `stock` list, and `total_stock`. Each `StockLine` contains the exact `size`, exact `quantity`, and an `in_stock` boolean.

`StockLine.quantity` is authoritative. A quantity of zero sets `in_stock` to false, and the prompt requires the agent to say that size is “out of stock” clearly. When a size is requested, the tool filters to that size; otherwise it returns size-by-size inventory for an accurate availability answer.

### Agent tool-selection rules

`backend/prompts/prompt.md` tells the agent to call `search_catalogue` for recommendations, `lookup_product_info` for exact descriptions/prices/colors, and `lookup_stock` for every availability question. The agent is explicitly prohibited from answering price or stock questions from memory or inventing values when a tool result is missing.

## Dynamic chat search and page updates

The chat search contract is `POST /api/chat` with `{ "message": "what hoodies do you have?" }`. The PydanticAI agent uses `search_catalogue`, then returns a `ChatReply` whose `products` list contains structured `ProductCard` values. The response includes the stable `product_id`, name, price, short description, image URL, colors, available sizes, and total stock needed by the frontend.

In the React app, `ChatStub` passes returned products to page-level `chatProducts` state. That state renders a “Found for you” product-card section below the current route, while the chat panel also keeps a compact version of the matches. This makes results visible on the website rather than leaving them only in raw chat text.

Both renderers use the same `ProductCard` component and link to `/products/{product_id}`. Therefore a product discovered through chat follows the same single-item route as a catalogue card from Problem 3, preserving the large image, full description, price, and size/stock detail view.

If a later chat search returns no products, the page-level result section is cleared. Product links remain database-backed and do not construct arbitrary URLs from model-generated names.

## Customer memory and context

### Authenticated history

`GET /api/chat/history` requires the existing bearer session. It reads the signed-in user’s rows from `chat_messages`, orders them chronologically, decodes each saved `products_json` payload, and returns the prior roles, message text, matched product cards, and timestamps. The frontend loads this endpoint when a logged-in user is available, so their conversation reappears when they return.

`POST /api/chat` accepts the same optional bearer session. For an authenticated shopper, the backend saves the user message before the agent runs and saves the assistant reply—including structured product cards—afterward. For a guest, the endpoint still runs normally but writes no chat rows, so guest conversations remain temporary. Each database query is scoped by `user_id` to prevent one customer from seeing another customer’s history.

### Agent dependencies

Each chat run receives an `AgentDeps` object containing:

- `user_name` and `user_email` when authenticated; guests receive `None` and are described to the agent as guests.
- `current_product`, resolved from the request’s `current_product_id` using the database. This includes the product ID, name, type, price, description, image URL, colors, available sizes, and aggregate stock.
- `recent_history`, the latest saved conversation items for the authenticated user.

The agent’s dynamic dependency instructions tell it who is chatting, which product detail page is active, and what recent conversation context is relevant. This lets a shopper ask “do you have this in pink?” from a product page and have “this” resolve to the current database-backed product. The context does not contain passwords, password hashes, or session tokens.

### Guest and signed-in behavior

```text
Guest message ───────────────► agent context with guest identity
                              └─ no database history write

Signed-in message + bearer ─► user_id-scoped chat_messages write
                              ├─ AgentDeps(name, email, product, history)
                              └─ history reloads through /api/chat/history
```

## Problem 9 usability additions

The Products page now provides client-side type filtering, text search, sorting, live result counts, and a reset control so shoppers can narrow the 102-item collection quickly. The chat panel provides one-click starter prompts, and page-level chat matches can be cleared without losing the conversation.

The backend caches bounded catalogue-search ID results for repeated queries while re-reading product inventory when cards are assembled. Chat model calls are limited to 45 seconds and return a safe structured fallback response on timeout or provider failure, keeping the storefront responsive without exposing provider errors.

## Problem 12: audit trail, safety, and final system harness

### Append-only audit trail

Agent activity is recorded in `output/audit_trail.json` as append-only JSON Lines: each line is one JSON object, and a later run opens the file with append mode. The application never deletes, truncates, or rewrites earlier events. A small write lock keeps concurrent requests from interleaving lines. The log records UTC `time`, `event`, optional `tool_name`, bounded `args`, bounded `result`, and `stop_reason`.

The request lifecycle records `agent_loop_started` and then `agent_loop_stopped` with one of `completed`, `timeout_45_seconds`, or `provider_or_runtime_error`. Each catalogue tool records its name, short arguments, and a compact result summary, including product IDs, match counts, prices, and exact stock rows where relevant. Passwords, password hashes, bearer tokens, API keys, and authorization headers are filtered before writing; long values and lists are capped. The file is operational evidence, not a customer-facing endpoint, and is never served by FastAPI.

### Safety rules

The agent safety policy is in `backend/prompts/prompt.md`. It treats shopper text and tool output as untrusted data, rejects prompt-injection attempts to reveal hidden instructions or secrets, and prevents disclosure of credentials, private records, raw database records, internal prompts, or audit contents. The agent is read-only: it cannot claim to place orders, reserve items, edit inventory, edit accounts, issue refunds, or contact people.

The agent must call database tools before answering price, description, color, or stock questions. Missing data is reported plainly instead of guessed. A zero quantity is explicitly described as “out of stock”; availability is never inferred across sizes or colors. Recommendations must use returned catalogue product IDs and URLs. Guest context is kept separate from authenticated user history, and only the minimum user/page context needed for the current answer is passed to the agent.

### Models, tools, limits, and run specifications

- `backend/models.py` contains the API contract: `ChatRequest` caps messages at 2,000 characters; `ChatReply` contains a reply plus structured `ProductCard` matches; `AgentDeps` carries optional identity, current product, and recent history; stock and product lookup results are typed with Pydantic models.
- The four tools in `backend/tools.py` are read-only: `search_catalogue` is capped at 12 results (the agent normally requests 6), `get_product` reads one product plus aggregate stock, `lookup_product_info` reads catalogue facts, and `lookup_stock` reads exact size quantities.
- `backend/agent.py` loads `prompts/prompt.md`, uses PydanticAI structured output, Portkey at `https://api.portkey.ai/v1`, and model `gpt-5.6-luna`. The API allows up to two agent retries and stops a model call after 45 seconds.
- The frontend runs with `npm run dev` and the backend from `Homework/HW 4/backend` with `../.venv/bin/uvicorn main:app --reload --port 8000`. The frontend calls `http://127.0.0.1:8000/api`; images are served from `/images`.
- Health can be checked at `GET /api/health`. Product reads are `GET /api/products` and `GET /api/products/{product_id}`. Chat is `POST /api/chat`; authenticated history is `GET /api/chat/history` with a bearer token.

### End-to-end system map

```text
Shopper browser
  ├─ React/Vite pages, auth, product cards, chat widget
  └─ POST /api/chat + optional bearer token + current_product_id
       ▼
FastAPI backend/main.py
  ├─ validates request and resolves user/product context
  ├─ writes user-scoped chat history when authenticated
  ├─ runs PydanticAI agent with the Portkey-routed Luna model
  ├─ records bounded audit events without exposing secrets
  └─ returns ChatReply { reply, products[] }
       ▼
SQLite data/campus_customs.db
  ├─ catalogue: product facts and image paths
  ├─ inventory: exact size quantities
  ├─ users: public identity plus protected password hash
  └─ chat_messages: authenticated conversation history
```
