# core/morning_briefing.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 213

---

### Documentation for `core/morning_briefing.py`

#### Purpose
The `MorningBriefing` class is responsible for scheduling and sending morning and evening briefings via Telegram. It integrates with a Telegram bot to run scheduled analyses and deliver the results to specified chat IDs.

#### Architecture
The `MorningBriefing` class contains methods for initializing the scheduler, running analyses, and sending messages. It uses lazy loading for the analyst to avoid circular imports and employs asynchronous methods for handling tasks.

- **Classes**: 
  - `MorningBriefing`: Manages scheduling and sending of morning and evening briefings.
  
- **Methods**:
  - `__init__`: Initializes the `MorningBriefing` instance with the Telegram application.
  - `_get_analyst`: Lazy loads the `BacklogAnalyst` to avoid circular imports.
  - `send_morning_briefing`: Runs the morning analysis and sends the briefing to Telegram.
  - `send_evening_review`: Runs the evening analysis and sends a message if there are urgent items.
  - `run_on_demand`: Runs analysis on demand and returns the briefing text.
  - `run_post_patch`: Runs analysis after a patch installation, updating the database without sending Telegram messages.
  - `_schedule_loop`: The main scheduling loop that runs indefinitely, triggering at configured times.
  - `start`: Starts the scheduling loop as a background task.
  - `stop`: Stops the scheduling loop.

#### Patterns
- **Lazy Loading**: Used in `_get_analyst` to avoid circular imports.
- **Singleton**: The `MorningBriefing` instance is typically a singleton, as it is initialized once and reused.

#### Dependencies
- **Imports**: `logging`, `asyncio`, `datetime`, `telegram.ext.Application`
- **Internal Dependencies**: `core.backlog_analyst.BacklogAnalyst`

#### Interfaces
- **Exposed Methods**:
  - `start`: Starts the scheduling loop.
  - `stop`: Stops the scheduling loop.
  - `send_morning_briefing`: Sends the morning briefing.
  - `send_evening_review`: Sends the evening review.
  - `run_on_demand`: Runs analysis on demand.
  - `run_post_patch`: Runs analysis after a patch installation.

#### Database
- **PostgreSQL Tables**:
  - `only`
  - `core`
  - `datetime`
  - `telegram`
  - `urgent`

#### Configuration
- **Environment Variables**: None
- **Constants**: 
  - `ADGE_CHAT_ID`, `SERAPHE_CHAT_ID`: Telegram chat IDs.
  - `BRIEFING_HOUR`, `BRIEFING_MINUTE`: Morning briefing time.
  - `EVENING_HOUR`, `EVENING_MINUTE`: Evening review time.
  - `QUIET_START`, `QUIET_END`: Quiet hours.

#### Key Logic
- **Morning Briefing**:
  - Runs the morning analysis using `BacklogAnalyst`.
  - Constructs a message with briefing details, urgent flags, transfer recommendations, and today's priorities.
  - Sends the message to the specified Telegram chat ID.
  
- **Evening Review**:
  - Runs the evening analysis.
  - Sends a message only if there are urgent items.
  
- **On-Demand Analysis**:
  - Runs analysis on demand and returns the briefing text.
  
- **Post-Patch Analysis**:
  - Runs analysis after a patch installation, updating the database without sending Telegram messages.

- **Scheduling Loop**:
  - Calculates the next scheduled time for morning and evening briefings.
  - Waits until the next scheduled time and triggers the appropriate method.

#### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot to send messages.
- **Backlog Analyst**: Uses `BacklogAnalyst` for running analyses.
- **Iris Chat Handler**: Integrates with the Iris chat handler for on-demand analysis.
- **Patch Monitor**: Triggered by the patch monitor for post-patch analysis.

This file is a critical component of the Mythos system, ensuring that scheduled analyses are performed and the results are communicated effectively via Telegram.
