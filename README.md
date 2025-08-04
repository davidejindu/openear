# Voice Agent

A real-time AI voice conversation system that enables natural voice interactions with customizable AI personas.

## What it does

- Real-time voice conversations with AI characters
- Choose between Pastor Eli or Therapist Marian
- Sub-second latency voice interactions
- Bidirectional audio streaming via WebSockets

## Tech Stack

- **Backend**: Python 3.12+, asyncio, websockets
- **AI/ML**: Deepgram API (speech-to-text, text-to-speech), Grok AI
- **Audio Processing**: Base64 encoding/decoding, mu-law audio format
- **Real-time Communication**: WebSocket connections
- **Tunneling**: ngrok for public access
- **Development**: uv package manager
