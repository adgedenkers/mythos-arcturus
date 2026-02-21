# Mythos Knowledge Map
# ====================
# This file is AUTO-GENERATED from the database.
# Static sections (People, Locations, Notes, Data Routing) are preserved.
# Dynamic sections (Accounts, Bills, Routines) are rebuilt on DB changes.
# Last rebuilt: 2026-02-20 16:53:36

## People
- **Adge** (also: Ka'tuar'el, Adriaan, me, I) → the user speaking
- **Rebecca** (also: Seraphe, Becky, Lou, she, wife, partner) → wife/partner
- **Fitz** (also: son, kid, boy, little man) → son

## Financial Accounts
| Abbreviation | Account Name | Type |
|-------------|-------------|------|
| SID | Checking | checking |
| NBT | Estate | checking |
| SUN | Primary Checking | checking |
| USAA | Simple Checking | checking |
| OLDNAVY | Barclaycard | credit |
| AMEX | Blue Cash | credit |
| TSC | Credit Card | credit |
| LLBEAN | Mastercard | credit |
| TJX | Mastercard | credit |
| USAALOAN | Personal Loan | loan |

## Bills & Utilities
| Merchant | Expected Amount | Due Day | Category |
|----------|----------------|---------|----------|
| Disney+ | $25 | Day 3 | Entertainment |
| Hugging Face | $8 | Day 3 | Subscriptions |
| YouTube Premium | $23 | Day 3 | Subscriptions |
| OpenAI | $65 | Day 6 | Subscriptions |
| Bartles Pharmacy | $53 | Day 7 | Healthcare |
| Progressive | $272 | Day 9 | Insurance |
| Claude AI | $45 | Day 12 | Subscriptions |
| Peacock | $17 | Day 12 | Entertainment |
| USAA Loan | $544 | Day 13 | Loan |
| AT&T | $257 | Day 14 | Utilities |
| Barclaycard Payment | $129 | Day 14 | Transfer |
| L.L.Bean MC Payment | $717 | Day 14 | Transfer |
| Ancestry | $43 | Day 15 | Subscriptions |
| Google One | $22 | Day 15 | Subscriptions |
| Starlink | $120 | Day 15 | Internet |
| AMEX Payment | $179 | Day 16 | Transfer |
| Rocket Money | $8 | Day 16 | Subscriptions |
| Walmart+ | $14 | Day 16 | Subscriptions |
| Sunmark Loan TFR | $157 | Day 17 | Transfer |
| Tractor Supply Card | $232 | Day 18 | Transfer |
| TJX Rewards Payment | $56 | Day 19 | Transfer |
| NYSEG | $750 | Day 20 | Utilities |
| Norwich YMCA Membership | $95 | Day 23 | Healthcare |
| Wansor Moses Chiro | $50 | Day 23 | Healthcare |
| Netflix | $27 | Day 26 | Entertainment |
| Amazon Prime | $20 | Day 27 | Subscriptions |
| Discovery+ | $10 | Day 30 | Entertainment |
| Blueox Propane | $455 | as-needed | Utilities |

## Active Routines
| Routine | Frequency | Domain |
|---------|-----------|--------|
| Check calendar | daily | personal |
| Import Bank Transactions | daily | finance |
| Review transactions | daily | finance |
| Full monthly financial review | monthly | finance |
| Subscription audit | monthly | finance |
| Credit card strategy | monthly | finance |
| Set monthly targets | monthly | finance |
| Import credit card transactions | monthly (day 1) | finance |
| Weekly financial review | weekly (Mon) | finance |
| Finance conversation with Rebecca | weekly (Mon) | finance |

## Data Routing
| Domain | Target | Action |
|--------|--------|--------|
| Bill payment | `bill_overrides` table | INSERT/UPDATE with is_paid=true |
| Money spent / purchase | `life_events` table | Log event, amount, merchant |
| Appointment / event | `calendar_events` table | INSERT new event |
| Task completed | `idea_backlog` table | UPDATE status='done' |
| New task / to-do | `idea_backlog` table | INSERT new task |
| Routine done | `routine_completions` table | UPDATE status='done' |
| Mood / emotional state | `life_events` table | Log with domain='mood' |
| Health update | `life_events` table | Log with domain='health' |
| Fitz/Rebecca update | `life_events` table | Log with person field |
| Financial observation | `life_events` table | Log with domain='finance' |

## Locations (common)
- Home: Oxford, NY
- VA office: work
- Price Chopper: grocery store
- Tractor Supply: farm/hardware store
- Walmart: general shopping
- Norwich: nearby town (pharmacy, doctor, etc.)

## Notes
- All financial amounts are in USD
- Rebecca handles some bill payments herself (LLBean, TSC logins are hers)
- NBT account is estate money (Jennie Joy Ryan) — temporary, not regular spending
- DVA/Advantage FCU is pass-through only for OneMain loan — excluded from reports
- Propane (Blueox) is as-needed, not monthly
