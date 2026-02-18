# Mythos Knowledge Map
# ====================
# This file tells the message extractor where information lives
# and how to route extracted actions. Updated manually as system grows.
# Last updated: 2026-02-18

## People
- **Adge** (also: Ka'tuar'el, Adriaan, me, I) → the user speaking
- **Rebecca** (also: Seraphe, Becky, Lou, she, wife, partner) → wife/partner
- **Fitz** (also: son, kid, boy, little man) → son

## Financial Accounts
| Reference Names | Account | Type | Abbr |
|----------------|---------|------|------|
| Sunmark, SUN, primary checking | Sunmark Credit Union | checking | SUN |
| USAA, main checking | USAA Federal Savings | checking | USAA |
| Sidney, SID | Sidney Federal Credit Union | checking | SID |
| NBT, estate account | NBT Bank | checking | NBT |
| LLBean, LL Bean, Bean card | L.L.Bean Mastercard | credit | LLBEAN |
| Tractor Supply, TSC | Tractor Supply Card | credit | TSC |
| Old Navy, Barclaycard | Old Navy Barclaycard | credit | OLDNAVY |
| TJX, TJ Maxx, Marshalls | TJX Rewards Mastercard | credit | TJX |
| Amex, American Express | American Express Blue Cash | credit | AMEX |
| USAA loan, personal loan | USAA Personal Loan | loan | USAALOAN |

## Bills & Utilities
| Reference Names | Bill | Expected Amount | Day |
|----------------|------|-----------------|-----|
| NYSEG, electric, power, electricity | NYSEG | ~$750 | 20 |
| AT&T, phone, cell, mobile | AT&T | $257 | 14 |
| Starlink, internet, satellite | Starlink | $120 | 15 |
| Progressive, car insurance, auto insurance | Progressive | $272 | 9 |
| Netflix | Netflix | $27 | 26 |
| Disney, Disney+ | Disney+ | $25 | 3 |
| YouTube, YT Premium | YouTube Premium | $23 | 3 |
| Peacock | Peacock | $17 | 12 |
| Discovery, Discovery+ | Discovery+ | $10 | 30 |
| OpenAI, ChatGPT | OpenAI | $65 | 6 |
| Claude, Anthropic | Claude AI | $45 | 12 |
| Amazon, Prime | Amazon Prime | $20 | 27 |
| Ancestry | Ancestry | $43 | 15 |
| Walmart, Walmart+ | Walmart+ | $14 | 16 |
| Google One, Google storage | Google One | $22 | 15 |
| Rocket Money | Rocket Money | $8 | 16 |
| pharmacy, Bartles, meds | Bartles Pharmacy | $53 | 7 |
| Norwich, family health, doctor | Norwich Family Health | $95 | 23 |
| chiro, chiropractor, Wansor | Wansor Moses Chiro | $50 | 23 |
| USAA loan payment, loan | USAA Loan | $544 | 13 |
| propane, Blueox, heating | Blueox Propane | $455 | as-needed |
| LLBean payment, Bean payment | L.L.Bean MC Payment | $717 | 14 |
| Barclaycard payment, Old Navy payment | Barclaycard Payment | $129 | 14 |
| Amex payment | AMEX Payment | $179 | 16 |
| Sunmark loan, credit union loan | Sunmark Loan TFR | $157 | 17 |
| TSC payment, Tractor payment | Tractor Supply Card | $232 | 18 |
| TJX payment, TJ Maxx payment | TJX Rewards Payment | $56 | 19 |

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
