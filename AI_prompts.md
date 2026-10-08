# AI Prompt Log

This file records the student's prompts, instructions, refinements, and relevant assignment context used while developing Homework 4. API credentials are intentionally never recorded here.

## 2026-10-07 — Initial workflow instructions

> I will basically post screenshot of the question for your reference only, but as you will see in the screenshots, there is text in there that tells you to ask me to explain the question myself. I merely want you to use the screenshots of the actual assignment as a guiding beacon, to truly know what the task asks, and to ensure that I don't misguide you with my instructions. I am going to try my best to explain everything in my own words and as best as I can, following the assignment guidelines, but that's the whole point of providing you with the questions: you also know what is asked and don't stray. Let me know if you think I am going off track or anything like that. The screenshot sent before this is the context and scenario for this assignment, and then there will be a couple questions, I think 11, that I will work on one at a time. Also, I want you to create an `AI_prompts.md` file in the folder that contains a log of everything that I say to you, so the professor and grader can see my actual prompts and refinements and instructions to you. We will use the 5.6 Luna model as I've selected, and make sure you see the Portkey API key in the `.env` file to use for the AI calls. Do everything nicely and organized.

### Assignment context from the provided screenshot

- Homework 4 is **Campus Customs Shop + Chatbot**.
- The project is a React + Vite TypeScript frontend with a Python FastAPI backend whose agent uses PydanticAI.
- The shop should support browsing products, account creation, merchandise chat, matching items appearing on the page, and honest price/stock answers based on a local database.
- The supplied database is `campus_customs.db`, containing the product catalogue, inventory by size, and users with hashed passwords.
- Product image paths are stored in the catalogue table.
- The assignment asks for research into `yalebulldogblue.com` for Campus Customs style and information used in the agent prompt.
- AI calls should use `PORTKEY_API_KEY` through Portkey and a model in the 5.6 or 6 series; the selected model is `gpt-5.6-luna`.
- Problems should be handled one at a time and written in the student's own words.
- The finished project is intended for a public GitHub repository; the database and product images must not be committed.

### Working agreement

- Use the screenshots as assignment guidance and requirements context.
- Use the student's written explanation as the immediate task specification.
- Flag apparent conflicts, omissions, or drift from the assignment requirements.
- Work only inside `Homework/HW 4`.
- Append future student prompts and refinements to this log in chronological order.

## Problem 1 — Vibe coder prompts

### Prompt typed

> Here is Problem 1. It is not really a question; it is the setup. I have already asked you to do some of this, so verify that everything is good before I move on to the assignment.

### Requirements verified from the assignment screenshot

- `AI_prompts.md` was created at the start of the assignment.
- The file is being kept updated as work proceeds.
- The log contains a section for each problem.
- Each problem section will include the problem number and title.
- Each problem section will include at least one prompt written by the student in their own words.
- A follow-up prompt and a sentence explaining what was missing after the first prompt will be added when a follow-up is actually needed.
- The running site, database writes, and screenshots will serve as evidence; no extra proof essay is required.

### Follow-up prompt

Not needed for Problem 1. The setup request was sufficiently clear.

### Clarification

> What app?

Here, “app” refers to the Campus Customs Shop + Chatbot web project described in the assignment scenario. At this setup stage, the HW 4 folder contains the supplied data, database, product assets, and prompt log, but no frontend or backend code yet.

### Clarification about “app”

> Where exactly does it say that? I'm confused.

“App” was shorthand for the project described in the scenario screenshot. Problem 1 itself only concerns creating and maintaining this prompt log; it does not ask for the website to be created yet.

## Problem 2 — Analyze the database

### Assignment screenshot context received

The screenshot identifies Problem 2 as “Analyze the database” and shows two panels. It instructs the student to inspect `data/campus_customs.db`, understand at minimum the `catalogue`, `inventory`, and `users` tables, and start `output/harness.md`. The harness should list each table, all of its fields, and one short line explaining why each field matters for the shop or chatbot. The harness will be expanded in later problems.

The screenshot also explicitly says the student must describe the task in their own words before the AI performs it. No implementation or database analysis has been performed yet; awaiting the student's own-worded request.

### Prompt typed by the student

> Look at the database mentioned and understand it all in depth. Then start a file, `output/harness.md`. Write down each table and its fields, and a short line on why each field matters for the chatbot or shop. We'll keep growing this harness file for later problems.

### Work completed

Inspected `data/campus_customs.db` and created `output/harness.md`. The harness documents the application tables (`catalogue`, `inventory`, `users`, and `chat_messages`), every field, field relevance, relationships, constraints, observed data facts, and initial integrity checks. It is structured for expansion in later problems.

## Problem 3 — Build the Campus Customs website

### Assignment screenshot context received

The screenshot identifies Problem 3 as “Build the Campus Customs website.” It requests a React + Vite + TypeScript frontend with navigation for Home, Products, About Us, Log in, and Create account. Home and About Us should use Campus Customs-style inspiration from `yalebulldogblue.com` while being written in the student's own voice rather than copied.

The Products page should display catalogue images using the database image paths and basic product information. Each product card should open a single-item page showing a large image, full description, price, and sizes/stock when available. A bottom-right chat interface stub should be added, without requiring agent functionality yet. The screenshot also permits starting a simple FastAPI app in `backend/main.py` to serve products and images; the agent backend will be developed later.

The screenshot explicitly requires the student to describe the task in their own words before implementation. No Problem 3 implementation has been performed yet; awaiting the student's own-worded request.

### Prompt typed by the student

> I want to scaffold a React + Vite + TypeScript frontend for Campus Customs. Put a navigation bar at the top that links to the main pages: Home, Products, About Us, Log in, and Create account. Pull Campus Customs-style wording from yalebulldogblue.com for the Home and About Us sections, but write these pages in your own voice and do not copy the original site.
>
> On the Products page, show product images from the catalogue using the image paths and basic product information. Make each product open a single-item page with a large image on one side and the full product text on the right, including the description and price. Clicking a product card should take the shopper to that page.
>
> Add a chat interface in the bottom-right of the site. It does not need to talk to an agent yet; a stub that will call the backend later is enough. I will also soon need a small API to read the database, so start a simple FastAPI app in `backend/main.py` to serve products and images.

### Work completed

Scaffolded the React + Vite + TypeScript frontend and starter FastAPI backend. Added the required navigation pages, original Yale/Campus Customs-inspired Home and About content, database-backed product grid, product detail routes with inventory, bottom-right chat stub, API endpoints, image serving, local Python virtual environment, dependency manifests, run instructions, and a `.gitignore` protecting the supplied database and product images.

## Problem 4 — Create account and login

### Assignment screenshot context received

The screenshot identifies Problem 4 as “Create account and login.” It requests a normal account-creation flow with first name, last name, email, password, and password confirmation, plus a login flow with email and password. New accounts must be stored in the `users` table, and passwords must be protected with secure hashing rather than plaintext storage.

The seed database includes a test user for verification. The finished work should confirm that the test user can log in and that a newly created account can also log in. `output/harness.md` must be updated with how authentication works, what user information is stored, and how passwords are protected. No Problem 4 implementation has been performed yet; awaiting the student's own-worded request.

### Prompt typed by the student

> Now I want you to build a normal create-account/login flow that is typical. Create account and log in, as you know. New users should go into the users table, and make sure to store passwords securely so no hackers get them. Be careful.
>
> The seed database already has a test user you can use while building; the email and password are provided. Also update `output/harness.md` with how the auth works, how the password is protected, and so on.

### Work completed

Implemented secure account registration and login across the FastAPI backend and React frontend. Added validation, password confirmation, PBKDF2-SHA-256 hashing with per-account salts, duplicate-email handling, bearer-session authentication, logout, signed-in navigation state, and user-facing error messages. Updated `output/harness.md` with the authentication design and verification results. No test account was added to the real seed database; new-account testing used a temporary database copy.

## Problem 5 — PydanticAI agent backend

### Assignment screenshot context received

The screenshot identifies Problem 5 as “PydanticAI agent backend.” It requests an agent behind FastAPI and connected to the website chat widget, with the API app remaining in `backend/main.py` and runnable through Uvicorn.

The requested backend organization is:

- `backend/prompts/prompt.md` for Campus Customs voice and safety basics.
- `backend/agent.py` for agent entry and wiring.
- `backend/tools.py` for tools the agent can call.
- `backend/models.py` for Pydantic/PydanticAI structured types.

The chat route should return an agent reply and whatever product/auth functionality is needed. The screenshot also requests that `output/harness.md` document the frontend-to-FastAPI connection and how the agent is loaded from its prompt file and model. The selected AI configuration is Portkey with `PORTKEY_API_KEY` from the root `.env` and model `gpt-5.6-luna`. No Problem 5 implementation has been performed yet; awaiting the student's own-worded request.

### Prompt typed by the student

> I want you to build the shop chatbot as a PydanticAI agent behind FastAPI, plugged into my frontend chat widget. Put the API app in `backend/main.py`, which is the file run with Uvicorn. Keep the agent as the four files next to it: `prompts/prompt.md`, `agent.py`, `tools.py`, and `models.py`.
>
> In `main.py`, expose a chat route so a message from the website returns a reply from the agent and whatever else is needed for products/auth. Use my AI model API key for the agent. Put Campus Customs voice and safety basics into `prompts/prompt.md`, and start or update types in `models.py` for chat replies and product cards. In `harness.md`, note how the frontend talks to FastAPI and how the agent is loaded. Ensure the backend runs with `uvicorn main:app --reload --port 8000`.

### Work completed

Implemented the PydanticAI shop agent and connected the chat widget to `POST /api/chat`. Added `backend/prompts/prompt.md`, `backend/agent.py`, `backend/tools.py`, and `backend/models.py`; configured Portkey with `gpt-5.6-luna`; added read-only catalogue search/product tools; returned structured replies with product cards; and documented the request flow in `output/harness.md`. Verified the exact Uvicorn entry point, health endpoint, and product endpoint. A valid chat request invokes the configured model and requires the Portkey key.

## Problem 6 — Tools: product info and stock

### Assignment screenshot context received

The screenshot identifies Problem 6 as “Tools: product info and stock.” It asks the agent tools to look up real information from `campus_customs.db` for product descriptions, prices, and inventory quantities, including stock by size when requested. The agent must use the database rather than inventing prices or quantities and must clearly say when a size is out of stock.

The second panel asks for the Campus Customs prompt to explain when to call these tools, for return types to be added or updated in `models.py`, and for `output/harness.md` to list each tool and explain the selected lookup-result fields. The screenshot explicitly requires the student to describe the task in their own words before implementation. No Problem 6 changes have been made yet; awaiting the student's own-worded request.

### Prompt typed by the student

> I want to give my agent tools that look up real information from `campus_customs.db`, like price, product description, stock, and so on. The agent must use the database and not hallucinate or invent things. If a size is out of stock, say that exactly. Expand `prompts/prompt.md` so the agent knows to call these tools for price and stock questions. Add or update the return types in `models.py`.
>
> In the harness file, list each tool and explain which model fields you chose for lookup and results, and why.

### Work completed

Expanded the database tool layer with explicit product-info and size-aware stock lookups, structured `ProductInfo`, `StockLine`, and `StockResult` models, strict prompt rules for tool use and out-of-stock wording, and a detailed tool/field explanation in `output/harness.md`. Verified tool results against the catalogue and inventory database.

## Problem 7 — Chat search that updates the page

### Assignment screenshot context received

The screenshot identifies Problem 7 as “Chat search that updates the page.” It asks the agent to search the catalogue when a shopper asks about an item type and asks the website to dynamically show matching product cards with an image, name, price, and short information. This is an API contract: the agent returns structured product matches and the frontend renders them.

The second panel requires the returned cards—including cards placed on the page by chat—to preserve the Problem 3 single-item behavior: clicking a card opens the detail view with the large image and full information. It also asks for `prompts/prompt.md` and `output/harness.md` to explain how search results reach the page. The screenshot explicitly requires the student to describe the task in their own words before implementation. No Problem 7 changes have been made yet; awaiting the student's own-worded request.

### Prompt typed by the student

> When a customer asks about a certain type of item, I want the agent to search the catalogue and the website to dynamically show those matching items as product cards. This is an API contract: the agent returns structured product matches and the frontend renders them on the website. After the dynamic product cards are loaded, make sure the single-item page behavior from Problem 3 still works. Each product page, including ones chat puts on the page, should open in that detail view. Update `prompt.md` and the harness so it is clear how search results reach the page.

### Work completed

Added page-level dynamic search results driven by the chat response, while retaining compact matches in the chat panel. Both use the same product-card component and link to the existing `/products/:productId` detail route. Updated the agent prompt and harness to document the structured API contract and search-to-page flow.

## Problem 8 — Customer memory

### Assignment screenshot context received

The screenshot identifies Problem 8 as “Customer memory.” It asks the app to save logged-in shoppers’ chat history in the `chat_messages` table and reload it when they return. The agent should know who is chatting by receiving the user’s name and email through agent dependencies or an equivalent clear context pattern.

The screenshot also asks the frontend to pass enough page context for product-page questions, so that a question such as “do you have this in pink?” can be understood as referring to the product currently being viewed. The screenshot explicitly requires the student to describe the task in their own words before implementation. No Problem 8 changes have been made yet; awaiting the student’s own-worded request.

### Prompt typed by the student

> When a shopper is logged in, I want to save their chat history in the database in an appropriate table and reload it when they return. The agent should know who is chatting, such as their name and email, so put that in agent dependencies or an equivalent clear pattern and/or tools. I also want to pass enough page context so that if someone is on a product page, the agent knows which product they are talking about. Guests can still chat, but their history only needs to persist for logged-in people. Document these changes in the harness.

### Work completed

Implemented user-scoped chat-history persistence and reload through `chat_messages` and `/api/chat/history`. Added guest-versus-authenticated behavior, passed user identity and recent history through `AgentDeps`, passed the active product into chat requests, and documented the full memory/context design in `output/harness.md`.

## Problem 9 — Usability improvements

### Assignment screenshot context received

The screenshot identifies Problem 9 as “Usability improvements.” It requires two frontend usability improvements and two agent/backend usability improvements. Frontend improvements should make the site look better or easier to use; agent/backend improvements should improve output quality, accuracy, safety, speed, or cost.

The second panel requires `output/usability.md`, written before or during the build, with what was added and why it helps a Campus Customs shopper or the business. The improvements must actually appear in the running app because graders will inspect both the write-up and the features. The screenshot explicitly requires the student to describe the task in their own words before implementation. No Problem 9 changes have been made yet; awaiting the student’s own-worded request.

### Prompt typed by the student

> I want to improve the core shop. Choose and implement two frontend usability improvements and two agent or backend improvements—something to make it better, faster, more efficient, safer, look better, or feel smoother. Write `output/usability.md` before or as you build. For each improvement, explain what you added and why it helps a shopper or the business. Make sure all the improvements are actually present because graders will check them, and the running app should function properly.

### Work completed

Selected and implemented product filtering/sorting, chat quick starts and clear-results controls, bounded catalogue-search caching, and timeout-safe chat fallback handling. Created `output/usability.md` before implementation, documented the changes in the harness, and verified the frontend build plus backend behavior.

## Problem 10 — Style the website

### Assignment screenshot context received

The screenshot identifies Problem 10 as “Style the website.” It asks for creative design work so the site feels like a real Campus Customs storefront, including fonts, color, hierarchy, motion, product presentation, and chat feel. The second panel requires a concise `output/design.md` explaining what changed and why the changes should help customers stay engaged and buy.

The screenshot explicitly requires the student to describe the task in their own words before implementation. No Problem 10 changes have been made yet; awaiting the student’s own-worded request.

### Prompt typed by the student

> I want to add imaginative design so it seems like a real storefront. Let’s use Yale blue, with hints of maroon and blue. The chat should feel cool and relaxed, like a friend is talking. Motion should be smooth and not jumpy. Colors should be vibrant and pop. Be imaginative and creative. In `design.md`, write what you changed and why it will help customers stick around and buy. Keep it short and precise.

### Work completed

Applied the requested Yale-blue, maroon, coral, sky-blue, and cream storefront palette; strengthened type hierarchy and product presentation; added smooth card, button, chat, and collection motion; made the chat copy more relaxed; and added reduced-motion support. Created `output/design.md` with a concise rationale. The frontend production build passed.

## Problem 11 — Site testing (app check)

### Assignment screenshot context received

The screenshot identifies Problem 11 as “Site testing (app check).” It requires testing the live site and documenting the checks in `output/app_check.html` with clear headings, screenshots, and short captions. The required evidence covers: chat checking an item’s inventory and price from the database, dynamic search-result cards appearing after a category question, and one usability feature from Problem 9.

The screenshot’s second panel requires screenshot image files in `output/app_check_images/` and relative links from `app_check.html`, making the HTML easy to grade. The screenshot explicitly requires the student to describe the task in their own words before implementation. No Problem 11 changes have been made yet; awaiting the student’s own-worded request.

## Problem 12 — Audit trail, safety, and finish harness

### Prompt typed by the student

> Keep an append-only audit trail of agent loop activity but do not wipe it between runs. I also want you to think of some safety rules and put them in `prompt.md` for the agent. I want to finish the harness file so it is clear how the whole system works, including safety rules, specs, and everything.

### Work completed

Added `backend/audit.py` to append bounded JSONL events to `output/audit_trail.json` without deleting prior runs. The API records agent start/stop reasons and the catalogue tools record short arguments and results, with sensitive fields filtered. Expanded `backend/prompts/prompt.md` with prompt-injection, privacy, read-only, truthfulness, stock, and secret-handling rules. Finished `output/harness.md` with the audit format, safety policy, model/tool limits, run commands, endpoints, and an end-to-end system map.

## Problem 13 — Push to GitHub and submit the URL

### Prompt typed by the student

> The last question is mostly formatting and how to submit the assignment. Follow the screenshots as written.

### Work completed

Aligned the submission root with the required layout by moving the Vite app into `frontend/`, keeping the FastAPI app in `backend/`, and retaining the required `output/` documentation. Added `.env.example` with a placeholder only, strengthened `.gitignore` so the real `.env`, database, product images, archives, dependencies, and build output are excluded, and updated `README.md` with local data-pack placement and frontend/backend run commands. The frontend production build passed. A GitHub push was not performed because no repository URL or GitHub destination was provided.

### Work completed

Tested the running frontend and FastAPI-backed chat with Playwright. Captured evidence for database-backed inventory and price lookup, dynamic category-search cards, and the Problem 9 catalogue filtering/sorting feature. Created `output/app_check.html` with clear headings, captions, and relative links to the screenshots in `output/app_check_images/`.
