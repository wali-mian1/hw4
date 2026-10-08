# Usability Improvements

Problem 9 adds two frontend improvements and two agent/backend improvements to make Campus Customs easier to use, more efficient, and more resilient.

## Frontend improvements

### 1. Product filtering and sorting

What I added: The Products page now lets shoppers filter by garment type and sort the catalogue by featured order, name, lowest price, or highest price. The result count updates as controls change, and a clear button resets the browse state.

Why it helps: A catalogue with 102 products is difficult to scan linearly. These controls reduce the time needed to find a relevant item and make price-conscious browsing easier. They also give the business a clearer merchandising experience without requiring an additional page or database query.

### 2. Chat quick starts and result controls

What I added: The chat panel now offers one-click starter prompts for common shopping intents, and the page-level “Found for you” results include a clear-results control. The existing loading state and product links remain visible so shoppers can understand what the agent is doing and move directly to product details.

Why it helps: Shoppers do not need to invent the perfect first prompt. Quick starts demonstrate what the assistant can do, while a clear-results control prevents old recommendations from cluttering the page after the shopper changes direction.

## Agent/backend improvements

### 3. Cached catalogue search index

What I added: The backend caches the catalogue’s matching product IDs for repeated search terms, while still reading current inventory when product cards are assembled. The cache is bounded to 128 distinct searches.

Why it helps: Repeated requests such as “hoodies” or “Yale gifts” no longer rescan the full catalogue each time. This reduces database work and response latency while keeping stock information fresh because inventory is not cached in the search index.

### 4. Chat timeout and graceful fallback

What I added: Chat model calls now have a bounded timeout. If the model service is temporarily unavailable or takes too long, FastAPI returns a friendly structured `ChatReply` instead of an unhandled server error or a raw provider exception.

Why it helps: The storefront remains usable during a transient AI/network problem, and customers receive a clear next step instead of a broken widget. The fallback also avoids leaking provider details or implementation errors to shoppers.

## Verification

- The frontend production build passes with the new controls.
- The catalogue search cache is bounded and product stock continues to come from the database.
- The chat fallback keeps the API response in the same structured `ChatReply` shape.
- Existing product links, login, chat memory, and database-backed product/stock tools remain intact.
