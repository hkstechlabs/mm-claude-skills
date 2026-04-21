# Mobile Monster Analytics — How to Use

Ask Claude questions about your Shopify stores and Bubble portal. Claude fetches live data and gives you numbers, tables, and charts. All figures are AUD and GST-inclusive by default.

---

## The one thing to remember

**"Orders" is ambiguous.** Always say whether you mean:

- **Sales orders** → retail sales on OzMobiles / FrankMobiles (Shopify)
- **Purchase orders** → buybacks from customers on the portal (Bubble)

If you just say "orders", Claude will ask which one you meant.

---

## Example prompts (copy-paste)

### Sales (Shopify)
- "Total sales orders today for OzMobiles"
- "Revenue yesterday for FrankMobiles"
- "Top selling variants today"
- "Sales of Samsung phones today"
- "Compare this week vs last week for OzMobiles"
- "Stock levels for iPhone 16 Pro Max 256GB"
- "Lookup order #1234"
- "How many orders this month for OzMobiles?"

### Buyback (Bubble portal)
- "Working price for iPhone 16 Pro Max 512GB"
- "How much do we pay for a faulty Galaxy S23 256GB?"
- "Purchase orders today"
- "Show PO M-298952"
- "Buyback volume this week"
- "Pickup POs this month"

### True profit (cross-system)
- "True profit on today's sales for OzMobiles"
- "Gross margin yesterday"
- "What did we pay for the devices we sold this week?"
- "Profit on order 7678142513302"

---

## What Claude will ask before running

When any of these are missing, Claude asks you once before fetching:

- **Which store?** OzMobiles / FrankMobiles / Both
- **What time range?** Today / yesterday / this week / custom
- **Which margin?** Approximate (Shopify unit cost) or true (PO-attributed via Bubble)
- **Which storage / grade?** For buyback price lookups

If your question is specific, Claude skips asking. `"Working price for iPhone 16 Pro Max 512GB"` is complete — no questions needed.

---

## What Claude will always tell you

- **GST treatment** — inclusive by default, ex-GST on request
- **Merchandise revenue vs customer-paid** — shipping kept separate
- **Coverage** — e.g. "85% of revenue has cost data, 15% untracked"
- **Data-quality flags** — zero-cost PO devices, missing variant costs, partial periods
- **Timezone** — all dates are Melbourne (+10:00), never raw UTC

---

## What Claude will NOT show

Customer personal information (names, emails, phones, addresses, IMEIs, barcodes) is never in responses — even if it's in the raw data. Only the one-time exception: when you explicitly ask to look up one specific customer by their email or name.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Authentication failed" on Bubble | Check `.env` `BUBBLE_CSRF_KEY` is correct |
| Shopify returns nothing | Check the date range uses `+10:00` Melbourne offset |
| Numbers differ from Shopify admin | Shopify admin shows GST-inclusive too — mismatch usually means a refund or cancelled order filter |
| Report coverage is low (many "untracked" lines) | Normal for days heavy on accessories. For true-profit reports, the Bubble PO bridge fills this gap for phones |

---

## Two stores, one setup

| Store | URL | Type |
|---|---|---|
| OzMobiles | ozmobiles.com.au | Shopify Plus |
| FrankMobiles | frankmobile.com.au | Shopify Grow |

Both behave the same from Claude's perspective. You can also ask "both stores" and Claude returns a combined + per-store split.

---

## Files you never need to touch

- `.env` — API tokens. Never share publicly.
- `.claude/skills/` — where Claude's behaviour rules live.
- `CLAUDE.md` — Claude's project instructions.

The clone at `/Users/macbook162019/Documents/MM Claude-Skills 1/` is a mirror kept in sync automatically. Don't edit it — edit the original.
