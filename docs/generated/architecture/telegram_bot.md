## telegram_bot
The `telegram_bot` component serves as the primary user-facing interface for Mythos, enabling users to interact with system features via Telegram. It processes incoming messages, routes requests to domain-specific handlers, and delivers responses through Telegram's API.

Key files are organized by functional domain: core handlers (`analyst_handler.py`, `astrology_handler.py`, `finance_handler.py`, `forecast_handler.py`, `calendar_handler.py`, `checkin_handler.py`, `diag_handler.py`, `inspect_handler.py`, `integrity_handler.py`, `iris_handler.py`), core infrastructure (`chat_mode.py`, `help_handler.py`, `__init__.py`), and utilities (`export_handler.py`, `export_fb.py`). Handlers implement domain logic, while `chat_mode.py` manages user state transitions.

Data flows as: Telegram message → `telegram_bot` router → domain handler → internal Mythos service call → response formatting → Telegram reply. Handlers depend on services like `finance_service` or `astrology_service` via internal APIs.

Dependencies include the `python-telegram-bot` library and internal Mythos services (e.g., `finance_service`, `calendar_service`). Integration points are defined in handler interfaces, with responses serialized via `export_handler.py`.

No significant technical debt or known issues documented in current architecture.
