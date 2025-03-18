import asyncio
import websockets
import json
from asn_j2735 import J2735_201603_combined
import sys, os
import datetime

from binascii import hexlify

# A set to store all connected WebSocket clients
connected_clients = set()

async def handle_client(websocket):
    """Handles communication with a single client."""
    # Add the new client to the set of connected clients
    connected_clients.add(websocket)
    print('A client connected.')
    try:
        # Keep listening for messages from this client
        async for message in websocket:
            # Broadcast the received message to all connected clients
            if "BasicSafetyMessage" or "MobilityOperationMessage" in message:
                await broadcast(message)
            else: print('not the correct message type')
    except websockets.exceptions.ConnectionClosed:
        # Handle client disconnection
        print("A client disconnected.")
    finally:
        # Remove the client from the set of connected clients
        connected_clients.remove(websocket)

async def broadcast(message):
    """Broadcasts a message to all connected clients."""
    if connected_clients:  # Only send if there are connected clients
        try:
            await asyncio.gather(
                *[client.send(message) for client in connected_clients]
            )
        except:
            pass

async def main():
    """Main function to start the WebSocket server."""
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("WebSocket server is running on ws://localhost:8765")
    # Run the periodic broadcasting task alongside the server
    await asyncio.gather(
        server.wait_closed()  # Keep the server running
    )

if __name__ == "__main__":
    asyncio.run(main())