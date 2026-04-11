# voice/static/index.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 319

---

### File: `voice/static/index.html`

#### Purpose
This HTML file serves as the user interface for the voice interaction component of the Mythos system, specifically for the "Iris" voice assistant. It provides a simple, responsive interface for users to interact with the voice assistant through a microphone button and displays the conversation transcript.

#### Architecture
The file consists of a basic HTML structure with embedded CSS and JavaScript. The main components are:
- **Header**: Displays the title "I R I S" and a status message.
- **Transcript Area**: Displays the conversation between the user and the assistant.
- **Controls**: Contains the microphone button for voice input.
- **JavaScript**: Manages WebSocket communication, audio recording, and playback.

#### Patterns
- **Singleton**: The WebSocket connection (`ws`) is a singleton instance that manages the communication with the server.
- **Observer**: The WebSocket connection observes incoming messages and updates the UI accordingly.

#### Dependencies
- **WebSockets**: For real-time communication with the server.
- **Web Audio API**: For audio processing and playback.
- **MediaDevices API**: For accessing the user's microphone.

#### Interfaces
- **WebSocket**: Connects to the server at `WS_URL` and handles messages.
- **Microphone Button**: Toggles recording and sends audio data to the server.
- **Status Updates**: Updates the status message based on connection and processing states.

#### Database
- **No direct database interaction**: The file does not interact directly with any database. All data exchange is handled via WebSocket communication with the server.

#### Configuration
- **Environment Variables**: The WebSocket URL (`WS_URL`) is dynamically generated based on the current protocol (`http` or `https`).

#### Key Logic
1. **WebSocket Connection**:
   - Establishes a WebSocket connection to the server.
   - Handles opening, closing, and error events.
   - Processes incoming messages to update the transcript and play audio responses.

2. **Audio Recording**:
   - Uses the Web Audio API to capture and process audio from the user's microphone.
   - Resamples the audio to 16kHz and converts it to PCM format.
   - Sends the recorded audio data to the server via WebSocket.

3. **UI Updates**:
   - Updates the status message based on the current state (connected, listening, processing, etc.).
   - Displays user and assistant messages in the transcript area.

#### Integration Points
- **WebSocket Communication**: The file communicates with the server via WebSocket to send audio data and receive responses.
- **Microphone Access**: The file accesses the user's microphone to capture audio input.
- **Audio Playback**: The file plays back audio responses received from the server using the Web Audio API.

#### Detailed Breakdown

1. **WebSocket Connection**:
   - `connect()`: Establishes a WebSocket connection to the server.
   - `ws.onopen`: Updates the status to "connected".
   - `ws.onmessage`: Handles incoming messages, updating the transcript or playing audio.
   - `ws.onclose`: Handles disconnection and attempts to reconnect.
   - `ws.onerror`: Updates the status to "connection error".

2. **Audio Recording**:
   - `startRecording()`: Initializes the audio context and starts recording audio from the microphone.
   - `stopRecording()`: Stops recording, processes the audio data, and sends it to the server.

3. **UI Updates**:
   - `setStatus(text, cls)`: Updates the status message and class.
   - `addMsg(text, who)`: Adds a new message to the transcript area.

4. **Event Listeners**:
   - `mousedown`, `mouseup`, `mouseleave`, `touchstart`, `touchend`, `touchcancel`: Handle the microphone button events for recording and sending audio data.

This file provides a complete, self-contained interface for voice interaction with the Mythos system, leveraging modern web technologies for real-time communication and audio processing.
