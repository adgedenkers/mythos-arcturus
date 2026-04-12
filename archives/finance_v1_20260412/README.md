# Mythos Finance Manager – README

This directory represents the Version 1 foundational structure of the Mythos System financial manager, located at:

    /opt/mythos/finance

It is designed to support clear visibility, proactive motion, and sovereignty over household and personal finances. Files are split by function for easy use, automation, or future UI extension.

---

## 📁 Directory Structure

```
/opt/mythos/finance/
│
├── finance_recurring_bills.csv       # All monthly recurring bills and subscriptions
├── finance_summary_accounts.csv      # Income, account balances, and monthly overview
├── declarations.md                   # Personal statement of transformation
└── README.md                         # This file
```

---

## 🔢 File Descriptions

### `finance_recurring_bills.csv`

Contains the structured list of monthly recurring payments including:

- Creditor or service name
- Due date
- Amount
- Bank or card used
- Notes (e.g., "CANCELED")
- Last 4 digits of associated card/account if relevant

This should be updated monthly or whenever changes are made.

---

### `finance_summary_accounts.csv`

This file shows:

- Total income
- Total expenses
- Net income
- Savings amounts
- Checking and savings balances across USAA, Sunmark, and SFCU

Use this for monthly snapshots and trend tracking.

---

### `declarations.md`

Your statement of shift — from avoidance to initiation.

Update it over time as your relationship to money, systems, and responsibility evolves.

---

## ✅ Next Steps

- Add `budget/cashflow.csv` or `budget/cashflow.md` to track historical cashflow
- Extend with `bills/one_time.csv` for ad hoc payments (repairs, etc)
- Link with Mythos witness log for financial milestone events
