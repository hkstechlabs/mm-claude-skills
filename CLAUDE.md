# Mobile Monster Analytics

This project provides Claude with API access to fetch data, show stats, and answer questions about two Shopify stores and a Bubble.io app. All businesses are owned by Tim Duggal, based in Melbourne, Australia.

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
