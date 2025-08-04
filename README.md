# Voice Agent

A real-time AI voice conversation system that enables natural voice interactions with customizable AI personas.

## What it does

- Real-time voice conversations with AI characters
- Choose between Pastor Eli or Therapist Marian
- Sub-second latency voice interactions
- Bidirectional audio streaming via WebSockets

## Tech Stack

- **Backend**: Python 3.12+, asyncio, websockets
- **AI/ML**: Deepgram API (speech-to-text, text-to-speech), OpenAI GPT-4
- **Audio Processing**: Base64 encoding/decoding, mu-law audio format
- **Real-time Communication**: WebSocket connections
- **Development**: uv package manager

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Create `.env` file:

   ```env
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Run the server:

   ```bash
   uv run ./main.py
   ```

4. Choose your character (pastor/therapist) when prompted

The server runs on `localhost:5000` and accepts WebSocket connections.
