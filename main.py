import asyncio
import base64
import json
import websockets
import os
import ssl
from dotenv import load_dotenv

load_dotenv()


def sts_connect():
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise Exception("DEEPGRAM_API_KEY not found")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", api_key],
        ssl=ssl_context
    )
    return sts_ws


def load_config(filename="therapist"):
    with open(f"{filename}.json", "r") as f:
        return json.load(f)


async def handle_barge_in(decoded, twilio_ws, streamsid):
    if decoded["type"] == "UserStartedSpeaking":
        clear_message = {
            "event": "clear",
            "streamSid": streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))


async def handle_text_message(decoded, twilio_ws, sts_ws, streamsid):
    await handle_barge_in(decoded, twilio_ws, streamsid)


async def sts_sender(sts_ws, audio_queue):
    print("sts_sender started")
    while True:
        chunk = await audio_queue.get()
        await sts_ws.send(chunk)


async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
    print("sts_receiver started")
    streamsid = None

    async for message in sts_ws:
        if type(message) is str:
            print(message)
            decoded = json.loads(message)
            

            if decoded.get("type") == "Welcome":
                print("Settings applied, conversation ready!")
                continue
            elif decoded.get("type") == "ConversationText":
                print(f"Agent: {decoded.get('text', '')}")

                if streamsid:
                    await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
            else:
                if streamsid:
                    await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
            continue


        if streamsid:
            raw_mulaw = message
            media_message = {
                "event": "media",
                "streamSid": streamsid,
                "media": {"payload": base64.b64encode(raw_mulaw).decode("ascii")}
            }
            await twilio_ws.send(json.dumps(media_message))
        

        if streamsid is None:
            try:
                streamsid = streamsid_queue.get_nowait()
                print(f"Got streamsid: {streamsid}")
            except asyncio.QueueEmpty:
                pass


async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue):
    BUFFER_SIZE = 20 * 160
    inbuffer = bytearray(b"")

    async for message in twilio_ws:
        try:
            data = json.loads(message)
            event = data["event"]

            if event == "start":
                print("get our streamsid")
                start = data["start"]
                streamsid = start["streamSid"]
                streamsid_queue.put_nowait(streamsid)
            elif event == "connected":
                continue
            elif event == "media":
                media = data["media"]
                chunk = base64.b64decode(media["payload"])
                if media["track"] == "inbound":
                    inbuffer.extend(chunk)
            elif event == "stop":
                break

            while len(inbuffer) >= BUFFER_SIZE:
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]
        except:
            break


async def twilio_handler(twilio_ws, character="therapist"):
    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue()

    async with sts_connect() as sts_ws:
        config_message = load_config(character)
        await sts_ws.send(json.dumps(config_message))

        await asyncio.wait(
            [
                asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
                asyncio.ensure_future(sts_receiver(sts_ws, twilio_ws, streamsid_queue)),
                asyncio.ensure_future(twilio_receiver(twilio_ws, audio_queue, streamsid_queue)),
            ]
        )

        await twilio_ws.close()


async def main():
    while True:
        character = input("Choose your character (pastor/therapist): ").lower().strip()
        if character in ["pastor", "therapist"]:
            break
        else:
            print("Please enter 'pastor' or 'therapist'")
    
    print(f"Starting server with {character} character...")
    

    async def handler(websocket):
        await twilio_handler(websocket, character)
    
    await websockets.serve(handler, "localhost", 5000)
    print("Started server.")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())