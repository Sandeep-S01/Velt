# App Flow — User Journey Documentation
## SmartSearch API — Semantic Search for E-commerce

**Version:** 1.0  
**Date:** 2026-06-22  
**Status:** Draft  
**Author:** UX Team

---

## 1. User Personas & Their Goals

### Persona 1: Sarah — Solo E-commerce Store Owner
- **Store:** Shopify, 500 products, handmade jewelry
- **Tech Skill:** Can copy-paste code, uses Canva, not a developer
- **Goal:** Fix her broken search so customers find products
- **Pain:** "Customers search 'gift for mom' and get zero results"
- **Time Budget:** 15 minutes to set up, then forget about it

### Persona 2: Mike — E-commerce Agency Developer
- **Clients:** 12 Shopify stores, ranging from 200-5,000 products
- **Tech Skill:** Full-stack developer, knows React, Node.js
- **Goal:** Add semantic search to all client stores quickly
- **Pain:** "Building custom search for each client is repetitive and expensive"
- **Time Budget:** 2 hours per client, wants white-label option

### Persona 3: Priya — Marketplace Product Manager
- **Platform:** Multi-vendor fashion marketplace, 50,000 listings
- **Tech Skill:** Technical PM, works with engineering team
- **Goal:** Replace Algolia with cheaper, better semantic search
- **Pain:** "$2,000/month for Algolia, and it still doesn't understand synonyms"
- **Time Budget:** 2-week evaluation, needs analytics and SLA

---

## 2. Primary User Flows

### Flow 1: First-Time Setup (Sarah — Solo Store Owner)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: LANDING PAGE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  smartsearch.io                                                     │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  HEADLINE: "Your customers can't find your products."       │   │    │
│  │  │  SUB: "Fix your store search in 10 minutes. No code needed."│   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │    │
│  │  │  Shopify    │  │ WooCommerce │  │  Custom API │                │    │
│  │  │  [Connect]  │  │ [Connect]   │  │  [Connect]  │                │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  DEMO WIDGET: Try searching "comfortable shoes for walking"   │   │    │
│  │  │  → Shows semantic results from sample store                   │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (Sarah clicks "Connect with Shopify")
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: SHOPIFY OAUTH                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Shopify Authorization                                                │    │
│  │                                                                     │    │
│  │  "SmartSearch API wants to access your store: sarahs-jewelry.myshopify.com"│    │
│  │                                                                     │    │
│  │  [✓] Read products                                                    │    │
│  │  [✓] Read inventory                                                   │    │
│  │  [✓] Read orders (for analytics)                                      │    │
│  │                                                                     │    │
│  │  [ Install App ]  [ Cancel ]                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (Sarah approves)
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: ONBOARDING — Store Connected                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  🎉 Store Connected!                                                  │    │
│  │                                                                     │    │
│  │  Store: Sarah's Jewelry                                               │    │
│  │  Products Found: 487                                                  │    │
│  │  Platform: Shopify                                                    │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  INDEXING IN PROGRESS...                                      │   │    │
│  │  │  [████████████░░░░░░░░] 60% — 293 of 487 products indexed   │   │    │
│  │  │  Estimated time: 2 minutes                                  │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  While you wait, here's what SmartSearch will do:                   │    │
│  │  ✓ Understand customer intent (not just keywords)                   │    │
│  │  ✓ Handle synonyms ("couch" = "sofa")                               │    │
│  │  ✓ Work with vague queries ("gift for mom")                           │    │
│  │  ✓ Show results in < 200ms                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (Indexing completes)
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: WIDGET SETUP (No-Code)                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Your Search is Ready!                                                │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  OPTION A: COPY-PASTE WIDGET (Recommended)                    │   │    │
│  │  │                                                             │   │    │
│  │  │  1. Go to Shopify Admin → Online Store → Themes → Edit Code │   │    │
│  │  │  2. Find `theme.liquid` or `header.liquid`                  │   │    │
│  │  │  3. Paste this code before </body>:                         │   │    │
│  │  │                                                             │   │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│   │    │
│  │  │  │ <script src="https://cdn.smartsearch.io/widget.js"    ││   │    │
│  │  │  │         data-store-id="ss_abc123"></script>           ││   │    │
│  │  │  └─────────────────────────────────────────────────────────┘│   │    │
│  │  │                                                             │   │    │
│  │  │  [📋 Copy Code]  [📺 Watch Video Tutorial]                  │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  OPTION B: SHOPIFY APP BLOCK (Easier)                       │   │    │
│  │  │                                                             │   │    │
│  │  │  1. Go to Shopify Admin → Online Store → Customize          │   │    │
│  │  │  2. Click "Add Section" → Search "SmartSearch"            │   │    │
│  │  │  3. Drag to header area                                     │   │    │
│  │  │  4. Save                                                    │   │    │
│  │  │                                                             │   │    │
│  │  │  [📺 Watch Video Tutorial]                                  │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (Sarah pastes code, saves)
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: TEST & CONFIRM                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Test Your Search                                                     │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  [Search your store...                    ] [🔍]            │   │    │
│  │  │                                                             │   │    │
│  │  │  Try these example searches from your store:                │   │    │
│  │  │  • "gift for mom" → 12 results (necklaces, bracelets)       │   │    │
│  │  │  • "something blue for wedding" → 8 results               │   │    │
│  │  │  • "hypoallergenic earrings" → 5 results                  │   │    │
│  │  │                                                             │   │    │
│  │  │  [🔄 Re-index Products]  [⚙️ Customize Appearance]         │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  PREVIEW: How it looks on your store                        │   │    │
│  │  │  [Mobile] [Desktop]                                         │   │    │
│  │  │  ┌─────────────────────────────────────────────────────┐   │   │    │
│  │  │  │  [Your Store Logo]  [Search...              ] [Cart]│   │   │    │
│  │  │  │                                                     │   │   │    │
│  │  │  │  Search Results for "gift for mom":                   │   │   │    │
│  │  │  │  ┌─────┐ ┌─────┐ ┌─────┐                            │   │   │    │
│  │  │  │  │ 📿  │ │ 💍  │ │ 🎀  │                            │   │   │    │
│  │  │  │  │Mom  │ │Love │ │Heart│                            │   │   │    │
│  │  │  │  │Neck │ │Ring │ │Brace│                            │   │   │    │
│  │  │  │  │$45  │ │$32  │ │$28  │                            │   │   │    │
│  │  │  │  └─────┘ └─────┘ └─────┘                            │   │   │    │
│  │  │  └─────────────────────────────────────────────────────┘   │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  [✅ Looks Good! Take Me to Dashboard]                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: DASHBOARD — Active Monitoring                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  SmartSearch Dashboard — Sarah's Jewelry                            │    │
│  │                                                                     │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │    │
│  │  │ 1,247    │ │ 384      │ │ 8.2%     │ │ 12.4%    │             │    │
│  │  │ Searches │ │ Unique   │ │ No-Result│ │ Conv.    │             │    │
│  │  │ This Week│ │ Queries  │ │ Rate     │ │ Rate     │             │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘             │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  TOP SEARCHES THIS WEEK                                     │   │    │
│  │  │  1. "gift for mom" — 42 searches, 18 clicks, 5 purchases   │   │    │
│  │  │  2. "hypoallergenic" — 38 searches, 22 clicks, 8 purchases │   │    │
│  │  │  3. "something blue" — 31 searches, 12 clicks, 3 purchases │   │    │
│  │  │  4. "dainty necklace" — 29 searches, 15 clicks, 4 purchases│   │    │
│  │  │  5. "budget under 50" — 27 searches, 8 clicks, 2 purch  │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  ⚠️ INSIGHT: 23 people searched "mens jewelry" this week   │   │    │
│  │  │  but you have no products tagged for men. Consider adding!  │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  [📊 View Full Analytics]  [⚙️ Settings]  [💬 Support]            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Flow 2: API Integration (Mike — Agency Developer)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: API SIGNUP                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Developer Portal — smartsearch.io/dev                                │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  SIGN UP FOR API ACCESS                                       │   │    │
│  │  │                                                             │   │    │
│  │  │  Email: mike@agency.com                                       │   │    │
│  │  │  Company: Mike's E-com Agency                               │   │    │
│  │  │  Use Case: White-label search for client stores               │   │    │
│  │  │                                                             │   │    │
│  │  │  [ Create Account ]                                         │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  Already have an account? [Log in]                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: API DASHBOARD                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Developer Dashboard                                                  │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  API KEYS                                                     │   │    │
│  │  │                                                             │   │    │
│  │  │  Production: ss_live_xxxxxxxxxxxxxxxxxxxxxxxx                 │   │    │
│  │  │  [🔄 Rotate]  [📋 Copy]  [👁️ Show]                          │   │    │
│  │  │                                                             │   │    │
│  │  │  Test: ss_test_xxxxxxxxxxxxxxxxxxxxxxxx                     │   │    │
│  │  │  [📋 Copy]                                                    │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  QUICK START                                                  │   │    │
│  │  │                                                             │   │    │
│  │  │  1. Create Store: POST /api/v1/stores                       │   │    │
│  │  │  2. Ingest Products: POST /api/v1/ingest                  │   │    │
│  │  │  3. Search: POST /api/v1/search                             │   │    │
│  │  │                                                             │   │    │
│  │  │  [📖 Full API Docs]  [📦 Postman Collection]  [💻 SDKs]    │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  CLIENT STORES (12)                                           │   │    │
│  │  │  ┌─────────────┬──────────┬────────────┬────────────┐       │   │    │
│  │  │  │ Store       │ Products │ Searches/W │ Status     │       │   │    │
│  │  │  │ Fashion Co  │ 2,400    │ 8,420    │ ✅ Active  │       │   │    │
│  │  │  │ Gear Shop   │ 890      │ 3,100    │ ✅ Active  │       │   │    │
│  │  │  │ Home Decor  │ 1,200    │ 2,800    │ ⚠️ Syncing │       │   │    │
│  │  │  │ ...         │ ...      │ ...      │ ...        │       │   │    │
│  │  │  └─────────────┴──────────┴────────────┴────────────┘       │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (Mike clicks on "Fashion Co")
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: STORE MANAGEMENT                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Fashion Co — Store Details                                           │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  INGESTION                                                    │   │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │   │    │
│  │  │  │ Upload CSV  │  │ Shopify API │  │ WooCommerce │         │   │    │
│  │  │  │ [📁]        │  │ [🔗 Connect]│  │ [🔗 Connect]│         │   │    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘         │   │    │
│  │  │                                                             │   │    │
│  │  │  Last Sync: 2 hours ago  │  Products: 2,400  │  Status: ✅   │   │    │
│  │  │                                                             │   │    │
│  │  │  [🔄 Sync Now]  [⏰ Schedule: Daily]  [⚙️ Field Mapping]      │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  API INTEGRATION CODE (React Example)                         │   │    │
│  │  │                                                             │   │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐│   │    │
│  │  │  │ import { SmartSearch } from '@smartsearch/sdk';       ││   │    │
│  │  │  │                                                       ││   │    │
│  │  │  │ const search = new SmartSearch({                       ││   │    │
│  │  │  │   apiKey: 'ss_live_xxx',                              ││   │    │
│  │  │  │   storeId: 'store_fashion_123'                        ││   │    │
│  │  │  │ });                                                   ││   │    │
│  │  │  │                                                       ││   │    │
│  │  │  │ const results = await search.query({                  ││   │    │
│  │  │  │   query: 'comfortable summer dress',                  ││   │    │
│  │  │  │   filters: { price_max: 100, category: 'dresses' }  ││   │    │
│  │  │  │ });                                                   ││   │    │
│  │  │  └─────────────────────────────────────────────────────────┘│   │    │
│  │  │                                                             │   │    │
│  │  │  [📋 Copy]  [📖 Full Docs]  [🎨 Customize Widget]          │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  ANALYTICS — Last 30 Days                                     │   │    │
│  │  │  [📊 Search Volume] [🎯 Conversion] [🔍 Top Queries]         │   │    │
│  │  │  [📈 Trending] [⚠️ No Results] [💰 Revenue Impact]           │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Flow 3: Customer Search Experience (End User on Merchant Store)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CUSTOMER SEARCH JOURNEY (On Merchant's Store)                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [Store Logo]  [Search...              🔍]  [Cart 2]  [Account]   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼ (Customer types)                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [Search: "comfy chair for long work hours"                    🔍]   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  AUTOCOMPLETE SUGGESTIONS (Semantic, not just prefix)        │   │    │
│  │  │  • "comfortable office chair for back pain"                 │   │    │
│  │  │  • "ergonomic desk chair lumbar support"                    │   │    │
│  │  │  • "chair for long hours at computer"                       │   │    │
│  │  │  • "best chair for home office 2026"                      │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼ (Customer presses Enter)             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Search Results — "comfy chair for long work hours"                   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  FILTERS                                                    │   │    │
│  │  │  Price: [$0]———[$500]  Category: [Office ▾]  Brand: [All ▾]│   │    │
│  │  │  Rating: [4+ ⭐]  In Stock: [✓]  Free Shipping: [ ]        │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  WHY THESE RESULTS? (Hover to see)                          │   │    │
│  │  │  "We found these because they match: ergonomic, lumbar,      │   │    │
│  │  │   breathable, adjustable, long hours, desk work"            │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  1. ⭐ 4.8  Ergonomic Office Chair Pro — $199.99            │   │    │
│  │  │     "Lumbar support and breathable mesh back perfect for    │   │    │
│  │  │      long work sessions..."                                 │   │    │
│  │  │     [🖼️ Image]  [❤️ Save]  [🛒 Add to Cart]               │   │    │
│  │  │                                                             │   │    │
│  │  │  2. ⭐ 4.6  Standing Desk Converter — $149.99              │   │    │
│  │  │     "Switch between sitting and standing throughout the     │   │    │
│  │  │      day. Reduces back strain from prolonged sitting..."    │   │    │
│  │  │     [🖼️ Image]  [❤️ Save]  [🛒 Add to Cart]               │   │    │
│  │  │                                                             │   │    │
│  │  │  3. ⭐ 4.5  Memory Foam Seat Cushion — $34.99              │   │    │
│  │  │     "Adds comfort to any chair. Ideal for long hours at      │   │    │
│  │  │      desk. Pressure relief for hips and lower back..."    │   │    │
│  │  │     [🖼️ Image]  [❤️ Save]  [🛒 Add to Cart]               │   │    │
│  │  │                                                             │   │    │
│  │  │  4. ⭐ 4.7  Adjustable Foot Rest — $29.99                  │   │    │
│  │  │     "Improves circulation during sedentary work. Pairs      │   │    │
│  │  │      perfectly with ergonomic setups..."                  │   │    │
│  │  │     [🖼️ Image]  [❤️ Save]  [🛒 Add to Cart]               │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  [Load More Results]  [📊 Didn't find what you need?]              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Secondary Flows

### Flow 4: No-Results Handling
```
Customer searches "purple dragon statue"
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  No exact semantic matches found (score < 0.30)               │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Hmm, we couldn't find "purple dragon statue"            │ │
│  │                                                           │ │
│  │  Did you mean:                                           │ │
│  │  • "dragon figurine" (3 results)                         │ │
│  │  • "purple home decor" (12 results)                      │ │
│  │  • "fantasy statue" (8 results)                          │ │
│  │                                                           │ │
│  │  Or try:                                                 │ │
│  │  [🔍 Browse All Statues]  [🔍 Browse Purple Items]       │ │
│  │                                                           │ │
│  │  💡 We're telling the store owner about this search!       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Flow 5: Analytics Deep-Dive (Merchant)
```
Merchant clicks "View Full Analytics" in Dashboard
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Analytics Dashboard — Sarah's Jewelry                        │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  DATE RANGE: [Last 7 Days ▾]  [📥 Export CSV]          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  SEARCH FUNNEL                                          │ │
│  │                                                         │ │
│  │  1,247 searches ──► 892 clicked result (71.5%) ──►    │ │
│  │  334 added to cart (26.8%) ──► 127 purchased (10.2%)  │ │
│  │                                                         │ │
│  │  [Compare to Previous Period]  [📊 Benchmark vs Industry]│ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  TOP QUERIES WITH NO RESULTS                            │ │
│  │  1. "mens jewelry" — 23 searches → 0 results ⚠️        │ │
│  │     [✏️ Add Product Tag]  [📧 Email Me When Available]   │ │
│  │  2. "gold anklet" — 18 searches → 0 results ⚠️          │ │
│  │  3. "custom engraving" — 15 searches → 2 results ⚠️      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  SEARCH TRENDS (Line Chart)                             │ │
│  │  "gift for mom" ↑ 45% this week                         │ │
│  │  "wedding jewelry" ↓ 12% this week                      │ │
│  │  "birthstone" → Flat                                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  REVENUE ATTRIBUTION                                    │ │
│  │  $3,420 revenue directly from SmartSearch this month    │ │
│  │  ROI: 117x (you paid $29, earned $3,420)                │ │
│  │  [📈 View Full Report]                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Flow 6: Subscription Upgrade
```
Merchant hits free tier limit (1,000 products or 1,000 searches)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ You've reached your free tier limit!                      │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Current Usage: 1,247 products (limit: 1,000)            │ │
│  │  Searches this month: 1,089 (limit: 1,000)               │ │
│  │                                                           │ │
│  │  Upgrade to keep your search running:                    │ │
│  │                                                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │  STARTER    │  │    PRO      │  │ ENTERPRISE  │     │ │
│  │  │   $29/mo    │  │   $79/mo    │  │  Custom     │     │ │
│  │  │             │  │             │  │             │     │ │
│  │  │ 5,000 prods │  │ 50,000 prods│  │ Unlimited   │     │ │
│  │  │ 10K searches│  │ 100K searches│  │ Unlimited   │     │ │
│  │  │ Auto-sync   │  │ Visual Search│  │ SLA 99.99%  │     │ │
│  │  │ Email supp  │  │ A/B Testing │  │ Dedicated   │     │ │
│  │  │             │  │ Multi-lang  │  │ Support     │     │ │
│  │  │ [Upgrade]   │  │ [Upgrade]   │  │ [Contact]   │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  │                                                           │ │
│  │  💡 Based on your usage, Pro would cost $79/mo and handle │ │
│  │     your growth for the next 12 months.                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Edge Cases & Error Flows

### Error 1: Indexing Failure
```
Merchant sees: "⚠️ 3 products failed to index"
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Indexing Issues                                              │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Failed Products (3):                                     │ │
│  │  • Product #4821: "Image URL invalid" → [Fix] [Skip]    │ │
│  │  • Product #4902: "Description too short (12 chars)"      │ │
│  │    → [Add Description] [Use AI Generate] [Skip]          │ │
│  │  • Product #5023: "Duplicate external ID" → [Merge] [Skip]│ │
│  │                                                           │ │
│  │  [🔧 Bulk Fix All]  [🔄 Retry Failed]  [⏭️ Skip & Continue]│ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Error 2: API Rate Limit Hit
```
Developer gets 429 response
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  HTTP 429 Too Many Requests                                   │
│                                                               │
│  {                                                            │
│    "error": "rate_limit_exceeded",                            │
│    "message": "You've exceeded 100 requests/minute",          │
│    "retry_after": 45,                                         │
│    "upgrade_url": "https://smartsearch.io/upgrade",          │
│    "current_tier": "starter",                                 │
│    "suggested_tier": "pro"                                   │
│  }                                                            │
└─────────────────────────────────────────────────────────────┘
```

### Error 3: Store Disconnected
```
Shopify token expires or store uninstalls app
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ Store Connection Lost                                     │
│                                                               │
│  Your Shopify store "sarahs-jewelry.myshopify.com" is no     │
│  longer connected. Search widget is showing fallback mode.   │
│                                                               │
│  [🔌 Reconnect Store]  [📧 Contact Support]  [📖 Troubleshoot] │
│                                                               │
│  Last successful sync: 3 days ago                            │
│  Products in index: 487 (stale)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Notification Flows

### Email 1: Welcome & Setup Complete
```
Subject: 🎉 Your SmartSearch is live on Sarah's Jewelry!

Hi Sarah,

Your store search is now powered by AI! Here's what happened:

✅ 487 products indexed
✅ Search widget installed
✅ Average response time: 142ms

Try searching your store: [Search Now]

View your dashboard: [Dashboard Link]

Questions? Reply to this email or check our docs.

— The SmartSearch Team
```

### Email 2: Weekly Insights
```
Subject: 📊 This week: 1,247 searches, 12.4% conversion rate

Hi Sarah,

Your SmartSearch performance this week:

🔍 1,247 searches (+23% vs last week)
🎯 12.4% conversion rate (+1.2% vs last week)
💰 $847 revenue attributed to search

💡 Insight: 23 people searched "mens jewelry" but found nothing.
   Consider adding mens products or updating tags.

[View Full Dashboard]
```

### Email 3: Usage Alert (Approaching Limit)
```
Subject: ⚠️ You're at 85% of your monthly search limit

Hi Sarah,

You've used 8,501 of your 10,000 monthly searches (85%).

At current pace, you'll hit your limit in 4 days.

Upgrade to Pro ($79/mo) for 100,000 searches/month:
[Upgrade Now]

Or stay on Starter and search will pause until next month.
```

---

## 6. Mobile Flows

### Mobile Widget
```
┌─────────────────────────────┐
│  [Logo]  [Search 🔍]  [Cart]│
│                             │
│  ┌─────────────────────────┐│
│  │ Search store...       🔍││
│  └─────────────────────────┘│
│                             │
│  (Customer types "comfy")   │
│                             │
│  ┌─────────────────────────┐│
│  │ • comfortable chair     ││
│  │ • comfy office chair    ││
│  │ • comfort for long hrs  ││
│  └─────────────────────────┘│
│                             │
│  (Customer selects)         │
│                             │
│  ┌─────────────────────────┐│
│  │ 🖼️ Ergonomic Chair    ││
│  │    $199.99 ⭐ 4.8      ││
│  │    "Lumbar support..."  ││
│  │    [🛒 Add to Cart]    ││
│  ├─────────────────────────┤│
│  │ 🖼️ Standing Desk      ││
│  │    $149.99 ⭐ 4.6      ││
│  │    "Switch between..."  ││
│  │    [🛒 Add to Cart]    ││
│  └─────────────────────────┘│
│                             │
│  [Load More]  [Filters ▾]   │
└─────────────────────────────┘
```

---

*End of App Flow Documentation*
