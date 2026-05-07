#!/usr/bin/env python3
"""
Test script for WebSocket endpoint /ws/asignacion/{id}
"""

import asyncio
import websockets
import json
import requests

async def test_websocket():
    # First, get a JWT token by logging in
    login_data = {
        "identifier": "admin",
        "contraseña": "admin12345"
    }
    
    try:
        # Login to get JWT token (using form data)
        response = requests.post("http://localhost:8000/api/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
        
        token = response.json()["data"]["access_token"]
        print(f"✅ Got JWT token: {token[:20]}...")
        
        # Test WebSocket connection
        id_asignacion = 2
        ws_url = f"ws://localhost:8000/ws/asignacion/{id_asignacion}?token={token}"
        
        print(f"🔌 Connecting to WebSocket: {ws_url}")
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send a test message to keep connection alive
            await websocket.send("ping")
            print("📤 Sent test message")
            
            # Wait for response (should keep connection alive)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received (this is expected for keep-alive)")
            
            print("✅ WebSocket test completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
