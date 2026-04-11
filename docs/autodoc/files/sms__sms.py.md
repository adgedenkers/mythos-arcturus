# sms/sms.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 71

---

### Documentation for `sms/sms.py`

#### Purpose
The `sms.py` file is designed to send SMS messages via the AT&T email-to-SMS gateway using SMTP. It supports sending to predefined contacts and can log the results of the message sending process.

#### Architecture
The file consists of two main functions:
1. `send_sms`: This function handles the logic for sending SMS messages to specified contacts.
2. `main`: This function parses command-line arguments and calls `send_sms` with the provided parameters.

The file also uses environment variables for configuration and logs the results of message sending to a file.

#### Patterns
- **Singleton Pattern**: The logging setup is done once using `logging.basicConfig`.
- **Factory Pattern**: The `EmailMessage` object is created and configured within the `send_sms` function.

#### Dependencies
- `smtplib`: For sending emails via SMTP.
- `argparse`: For parsing command-line arguments.
- `sys`: For handling system-level operations.
- `os`: For interacting with the operating system.
- `json`: For serializing and deserializing JSON data.
- `logging`: For logging messages.

#### Interfaces
- `send_sms(message: str, to: str, use_mms: bool) -> dict`: Sends an SMS message to the specified contact and returns a dictionary with the results.
- `main()`: Entry point for the script, which parses command-line arguments and calls `send_sms`.

#### Database
- **PostgreSQL Tables**:
  - `email`: Not directly used in this file but referenced in the context of the system.
  - `datetime`: Not directly used in this file but referenced in the context of the system.
  - `Arcturus`: Not directly used in this file but referenced in the context of the system.

#### Configuration
- Environment Variables:
  - `MYTHOS_SMS_FROM`: The sender email address.
  - `MYTHOS_SMTP_HOST`: The SMTP server host.
  - `MYTHOS_SMTP_PORT`: The SMTP server port.
- Configuration Files:
  - `LOG_FILE`: Path to the log file (`/opt/mythos/sms/logs/sms.log`).

#### Key Logic
1. **Contact Mapping**: The `CONTACTS` dictionary maps contact names to their phone numbers and SMS/MMS gateways.
2. **Message Sending**:
   - Creates an `EmailMessage` object and sets the content and recipients.
   - Connects to the SMTP server and sends the message.
   - Logs the results of the message sending process.
3. **Error Handling**: Catches exceptions during SMTP connection and message sending, logging errors appropriately.

#### Integration Points
- **SMTP Server**: The script integrates with the SMTP server to send emails.
- **Logging**: The script logs the results of message sending to a file.
- **Environment Configuration**: The script reads configuration from environment variables, which can be managed through the Mythos system's configuration.

### Detailed Analysis

#### `send_sms` Function
- **Parameters**:
  - `message`: The text of the SMS message.
  - `to`: The recipient, which can be a single contact or `"both"` to send to all contacts.
  - `use_mms`: A boolean indicating whether to use the MMS gateway.
- **Logic**:
  - Determines the recipients based on the `to` parameter.
  - Constructs the email message and sends it via SMTP.
  - Logs the results to a file.

#### `main` Function
- **Logic**:
  - Parses command-line arguments using `argparse`.
  - Calls `send_sms` with the parsed arguments.
  - Prints the results of the message sending process to the console.

#### Logging
- The script logs the results of message sending to a file specified by `LOG_FILE`.
- The log entries include the timestamp, message text, and results for each recipient.

#### Environment Variables
- `MYTHOS_SMS_FROM`: Specifies the sender email address.
- `MYTHOS_SMTP_HOST`: Specifies the SMTP server host.
- `MYTHOS_SMTP_PORT`: Specifies the SMTP server port.

This documentation provides a comprehensive overview of the `sms.py` file, detailing its purpose, architecture, dependencies, interfaces, and key logic within the Mythos system.
