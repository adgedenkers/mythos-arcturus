# Cross-Stream Requests

> When a stream needs a change in another stream's territory, log it here.
> The owning stream handles it in its own conversation.

## How to Use

1. **Requesting stream** adds a row with status `PENDING`
2. **Owning stream** picks it up, builds the patch, changes status to `DONE` with the patch ID
3. **Requesting stream** can then build against the change

## Active Requests

| # | From | Needs | Description | Status | Resolved By |
|---|------|-------|-------------|--------|-------------|
|   |      |       |             |        |             |

## Completed Requests

| # | From | Needs | Description | Resolved By |
|---|------|-------|-------------|-------------|
|   |      |       |             |             |
