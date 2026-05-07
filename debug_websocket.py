#!/usr/bin/env python3
"""
Debug WebSocket connection to identify permission issues
"""

import asyncio
import websockets
import json
import requests

async def debug_websocket():
    """Debug WebSocket connection step by step"""
    
    base_url = "localhost:8000"
    asignacion_id = 1  # Try with assignment ID 1
    
    print(f"🔍 Debugging WebSocket connection")
    print(f"📡 Target: ws://{base_url}/ws/asignacion/{asignacion_id}")
    
    # Step 1: Get JWT token
    try:
        print("🔐 Getting JWT token...")
        login_data = {
            "identifier": "admin",
            "contraseña": "admin12345"
        }
        
        response = requests.post(f"http://{base_url}/api/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
        
        token = response.json()["data"]["access_token"]
        payload = token.split('.')[1]
        # Simple base64 decode (without padding)
        import base64
        decoded = base64.b64decode(payload + '=' * (-len(payload) % 4))
        print(f"✅ JWT token payload: {decoded}")
        
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return
    
    # Step 2: Test different assignment IDs
    for test_id in [1, 2, 3, 44, 999]:
        try:
            ws_url = f"ws://{base_url}/ws/asignacion/{test_id}?token={token}"
            print(f"\n🔌 Testing assignment ID {test_id}...")
            
            async with websockets.connect(ws_url) as websocket:
                print(f"✅ Connection successful for assignment {test_id}!")
                await websocket.close()
                break
                
        except websockets.exceptions.InvalidStatus as e:
            print(f"❌ Assignment {test_id}: HTTP {e.response.status_code}")
            if e.response.status_code == 403:
                print(f"   Permission denied - user doesn't have access to this assignment")
            elif e.response.status_code == 404:
                print(f"   Assignment not found")
                
        except Exception as e:
            print(f"❌ Assignment {test_id}: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(debug_websocket())
