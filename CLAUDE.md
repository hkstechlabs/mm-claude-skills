# Mobile Monster Analytics

This project provides Claude with API access to fetch data, show stats, and answer questions about two Shopify stores and a Bubble.io app. All businesses are owned by Tim Duggal, based in Melbourne, Australia.

## Rule #1 — Ask whenever ANYTHING is unclear

**If there is any ambiguity in the user's question — no matter how small — ask before fetching.** Use the `AskUserQuestion` tool. Batch multiple unknowns into a single question.

This rule overrides all other defaults. Do not guess, do not assume, do not silently pick the most likely option. The cost of one extra question is tiny; the cost of answering the wrong question is large — the numbers go to business decisions.

Ambiguity includes, but is not limited to:
- Which store (OzMobiles / FrankMobiles / both)
- Sales orders vs purchase orders ("orders" alone is ALWAYS ambiguous)
- Date range, time range, or timezone assumption
- Grade, storage, color, or variant missing on a device
- Whether "margin" means approximate (Shopify unit cost) or true (PO-attributed)
- Order number without a store
- Metric basis (revenue vs customer-paid, units vs revenue, tracked vs all)
- Output format (table, chart, spreadsheet)

The only exception: questions that are fully specified with no missing piece. If the user says "Working grade price for iPhone 15 Pro Max 256GB" — everything's there, answer directly. If they say "price for iPhone 15 Pro Max" — ask for storage and grade.

**Never** phrase an assumption as a statement ("Yesterday = 2026-04-20, Australia time, I assume — let me know if different"). That is an assumption masquerading as clarification. Either it's specified or you ask.

## Two Separate Systems

Mobile Monster runs **two distinct businesses** with separate data:

| System | Business | Skill | Endpoint |
|--------|----------|-------|----------|
| **Shopify** (OzMobiles, FrankMobiles) | MM **SELLS** refurbished devices to retail customers | `/shopify-analytics` | ozmobiles.com.au, frankmobile.com.au |
| **Bubble** (portal.mobilemonster.com.au) | MM **BUYS** used devices from customers (buyback) | `/bubble-analytics` | portal.mobilemonster.com.au |

## CRITICAL: Always disambiguate "orders"

**The word "order" is ambiguous** in this project. It could mean a sales order (Shopify) or a purchase order (Bubble). These come from completely different systems.

**Before answering ANY question that uses the word "order", "orders", "total orders", or similar without a clear qualifier, you MUST ask the user:**

- Do you mean **sales orders** (Shopify — retail sales to customers)?
- Or **purchase orders** (Bubble — buying used devices from customers)?

Use the AskUserQuestion tool. Do not guess. Do not default to Shopify. Do not default to Bubble.

### Terminology mapping (once disambiguated)

| Word in the question | System / Skill |
|----------------------|----------------|
| **sales**, **sale**, **sold**, **sales order**, **revenue**, **AOV**, **inventory**, **stock**, **products** | Shopify (`/shopify-analytics`) |
| **purchase**, **purchase order**, **PO**, **buyback**, **bought**, **trade-in**, **M-XXXXXX**, **PPT** | Bubble (`/bubble-analytics`) |
| **true profit**, **real margin**, **gross margin on sales**, **cost basis**, **margin per SKU**, **PO sell-through**, **"what did we pay for what we sold"** | Bubble → `claude_sale_orders` (cross-system bridge) |
| **order** / **orders** / **total orders** alone | **ASK FIRST** |

If the user says "sales today" or "today's purchase orders" — no ambiguity, go straight to the matching skill. If they just say "orders today" — always ask.

### Cross-system profit bridge

True gross profit per sale requires sale price (Shopify) joined with acquisition cost (Bubble PO devices). The Bubble portal workflow `claude_sale_orders` does this join server-side — each sold line item comes back with `variant_id`, `sku`, `variant_price` (sale price on the store), `quantity`, and `allocated_podevices[].costPrice`. This lives in `/bubble-analytics`. Shopify variant `unitCost` is used only as a fallback for accessories/new-stock with no PO allocation.

**Canonical true-profit formula (Dale, 2026-04-22):**

```
True Profit = Sale Total − Discount − Refund − PO Cost − Payment Fee
```

- **Sale Total** = `total_order_value` (GST-incl, shipping-incl, discount already deducted)
- **Refund** = sum of Shopify `totalRefundedSet` — partial refund subtracted; fully refunded or `cancelledAt` → order excluded from profit totals AND listed separately for reconciliation
- **PO Cost** = `sum(allocated_podevices[].costPrice)` across the order. **PO-devices ONLY.** Lines with no allocated PO (accessories, warranty, shipping, cables) contribute $0 to cost and flow through as margin — Dale's business rule, confirmed against #319761 live data.
- **Payment Fee** = gateway rate applied to original `total_order_value`. Primary gateway only on split-pay. Fee is NOT refunded on partial refunds.
- **GST** is inclusive on both sides — never stripped. Margin denominator = `total_order_value`.

**Golden test cases** (must reconcile to the cent on any change to the profit calc):
- Order #319761 (OzMobiles, Shopify Payments, no refund): $1,284.70 − $976.00 − $11.86 = **$296.84**
- Order #318871 (OzMobiles, PayPal, $10 partial refund): $448.00 − $10.00 − $326.09 − $5.48 = **$106.43**

Gateway rates, refund handling, enrichment GraphQL, and the full worked implementation live in `bubble-analytics` SKILL.md under "True-profit calculation" and "Payment fees — gateway rate table".

## Stores (Shopify)

- **OzMobiles** (ozmobiles.com.au) — Shopify Plus
- **FrankMobiles** (frankmobile.com.au) — Shopify Grow

## Key Rules

- All prices are **AUD**. All dates are **Australia/Melbourne (UTC+10)** calendar days — never raw UTC.
- **Never hardcode API tokens** — always load from `.env` file.
- **Always ask which store** before making any Shopify API call.
- **Never expose customer PII** (names, emails, phones, addresses, IMEIs, barcodes).
- **Fetch live data** — never guess or use cached data.
- Use the lightest API call possible.

## Skills

- **`/shopify-analytics`** — Shopify sales, revenue, orders, inventory, products, refunds, top sellers, approximate margin (variant unitCost). `.claude/skills/shopify-analytics/SKILL.md`
- **`/bubble-analytics`** — Bubble portal: PPT (buyback prices per grade), purchase orders (what MM buys), and `claude_sale_orders` (sales joined with PO-device cost — the authoritative true-profit source). `.claude/skills/bubble-analytics/SKILL.md`

## Credentials

**Preflight rule (applies to every session, every skill):** Before invoking any analytics skill or making any API call, run the preflight bash snippet documented in each skill's SKILL.md. The skill detects the project root automatically (via `git rev-parse --show-toplevel`, falling back to `$PWD`) — do NOT hardcode absolute paths, because the repo can be cloned anywhere.

The preflight has three states:

| Preflight result | Action |
|---|---|
| `OK` | Continue — proceed with the API call |
| `CREATED_ENV_TEMPLATE` | `.env` was missing. The skill auto-copied `.env.example` → `.env` and opened it in the default editor. Show the message below and stop. |
| `EMPTY_KEYS` | `.env` exists but required keys are blank. Open the file and show the message below. Stop. |
| `MISSING_ENV` | Neither `.env` nor `.env.example` present (shouldn't happen on a fresh clone). Show the message and stop. |

**Standard message (use verbatim) when the preflight is not `OK`:**

> ⚠️ **Credentials required**
>
> I've opened your `.env` file. Please add the API credential values and save it.
>
> **If you don't have the values, ask Faisal (Team Lead).**
>
> Once the file is filled in, ask your question again.

This fires automatically after a fresh clone, after rotating tokens, or on any new machine. Each skill's SKILL.md has a dedicated preflight-check snippet — run it first.

All API credentials are in `.env` at the project root. Load with:

```bash
# Shopify
TOKEN=$(grep OZMOBILES_SHOPIFY_TOKEN .env | cut -d= -f2)
STORE=$(grep OZMOBILES_SHOPIFY_STORE .env | cut -d= -f2)

# Bubble (CSRF must be URL-encoded)
CSRF=$(grep BUBBLE_CSRF_KEY .env | cut -d= -f2-)
BASE=$(grep BUBBLE_API_BASE .env | cut -d= -f2-)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OZMOBILES_SHOPIFY_TOKEN` | OzMobiles API access token |
| `OZMOBILES_SHOPIFY_STORE` | OzMobiles Shopify domain |
| `FRANKMOBILES_SHOPIFY_TOKEN` | FrankMobiles API access token |
| `FRANKMOBILES_SHOPIFY_STORE` | FrankMobiles Shopify domain |
| `SHOPIFY_API_VERSION` | API version (2025-01) |
| `BUBBLE_CSRF_KEY` | Bubble.io CSRF private key |
| `BUBBLE_API_BASE` | Bubble.io API base URL (live: `.../version-live/api/1.1`) |
