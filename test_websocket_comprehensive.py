#!/usr/bin/env python3
"""
Comprehensive WebSocket test script for /ws/asignacion/{id}
Tests ping/pong keepalive and connection stability
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

async def test_websocket_connection():
    """Test WebSocket connection with ping/pong handling"""
    
    # Configuration
    base_url = "localhost:8000"  # Change to production URL when needed
    asignacion_id = 3
    test_duration = 120  # Test for 2 minutes
    
    print(f"🧪 Starting comprehensive WebSocket test")
    print(f"📡 Target: ws://{base_url}/ws/asignacion/{asignacion_id}")
    print(f"⏱️  Duration: {test_duration} seconds")
    print(f"🕐 Started at: {datetime.now().isoformat()}")
    print("-" * 60)
    
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
            return False
        
        token = response.json()["data"]["access_token"]
        print(f"✅ JWT token obtained: {token[:30]}...")
        
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return False
    
    # Step 2: Connect to WebSocket
    ws_url = f"ws://{base_url}/ws/asignacion/{asignacion_id}?token={token}"
    
    try:
        print(f"🔌 Connecting to WebSocket...")
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ WebSocket connected successfully!")
            
            # Track statistics
            stats = {
                "pings_received": 0,
                "pongs_sent": 0,
                "messages_received": 0,
                "connection_start": time.time(),
                "last_activity": time.time()
            }
            
            # Test 1: Send initial message
            initial_message = {
                "type": "test_connection",
                "timestamp": time.time(),
                "asignacion_id": asignacion_id
            }
            await websocket.send(json.dumps(initial_message))
            print(f"📤 Sent initial test message")
            
            # Test 2: Monitor connection for specified duration
            print(f"⏳ Monitoring connection for {test_duration} seconds...")
            
            end_time = time.time() + test_duration
            last_status_report = time.time()
            
            while time.time() < end_time:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    stats["messages_received"] += 1
                    stats["last_activity"] = time.time()
                    
                    try:
                        data = json.loads(message)
                        msg_type = data.get("type", "unknown")
                        
                        if msg_type == "ping":
                            stats["pings_received"] += 1
                            print(f"💓 Ping #{stats['pings_received']} received at {datetime.now().strftime('%H:%M:%S')}")
                            
                            # Send pong response
                            pong_message = {
                                "type": "pong",
                                "timestamp": time.time(),
                                "ping_timestamp": data.get("timestamp")
                            }
                            await websocket.send(json.dumps(pong_message))
                            stats["pongs_sent"] += 1
                            print(f"🏓 Pong sent in response")
                            
                        elif msg_type == "ack":
                            print(f"✅ ACK received: {data}")
                            
                        else:
                            print(f"📨 Other message: {msg_type} - {data}")
                            
                    except json.JSONDecodeError:
                        print(f"⚠️  Non-JSON message: {message[:100]}")
                        
                except asyncio.TimeoutError:
                    # No message received, connection is still alive
                    pass
                
                # Report status every 30 seconds
                if time.time() - last_status_report >= 30:
                    elapsed = time.time() - stats["connection_start"]
                    print(f"📊 Status Report ({elapsed:.0f}s elapsed):")
                    print(f"   - Pings received: {stats['pings_received']}")
                    print(f"   - Pongs sent: {stats['pongs_sent']}")
                    print(f"   - Total messages: {stats['messages_received']}")
                    print(f"   - Last activity: {time.time() - stats['last_activity']:.1f}s ago")
                    last_status_report = time.time()
            
            # Test 3: Send status update
            print("\n🔄 Testing status update...")
            status_message = {
                "type": "status_update",
                "id": f"test_{int(time.time())}",
                "estado": "en_progreso",
                "estado_anterior": "pendiente",
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(status_message))
            print(f"📤 Status update sent")
            
            # Wait for ACK
            try:
                ack_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                ack_data = json.loads(ack_message)
                if ack_data.get("type") == "ack":
                    print(f"✅ Status update ACK received: {ack_data}")
                else:
                    print(f"⚠️  Unexpected response: {ack_data}")
            except asyncio.TimeoutError:
                print(f"⚠️  No ACK received for status update")
            
            # Final statistics
            total_time = time.time() - stats["connection_start"]
            print(f"\n🎉 Test completed successfully!")
            print(f"📊 Final Statistics:")
            print(f"   - Total connection time: {total_time:.1f} seconds")
            print(f"   - Pings received: {stats['pings_received']}")
            print(f"   - Pongs sent: {stats['pongs_sent']}")
            print(f"   - Total messages: {stats['messages_received']}")
            print(f"   - Ping frequency: {stats['pings_received'] / (total_time / 60):.1f} per minute")
            
            return True
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed: {e.code} - {e.reason}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

async def test_connection_stability():
    """Test multiple rapid connections and disconnections"""
    print("\n🔄 Testing connection stability with rapid connect/disconnect...")
    
    base_url = "localhost:8000"
    asignacion_id = 3
    
    # Get token once
    login_data = {
        "identifier": "admin",
        "contraseña": "admin12345"
    }
    
    response = requests.post(f"http://{base_url}/api/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed for stability test")
        return False
    
    token = response.json()["data"]["access_token"]
    
    # Test multiple connections
    successful_connections = 0
    total_tests = 5
    
    for i in range(total_tests):
        try:
            ws_url = f"ws://{base_url}/ws/asignacion/{asignacion_id}?token={token}"
            
            async with websockets.connect(ws_url) as websocket:
                # Send a test message
                test_msg = {"type": "test", "iteration": i}
                await websocket.send(json.dumps(test_msg))
                
                # Wait briefly
                await asyncio.sleep(1)
                
                successful_connections += 1
                print(f"✅ Connection {i+1}/{total_tests} successful")
                
        except Exception as e:
            print(f"❌ Connection {i+1}/{total_tests} failed: {e}")
        
        # Small delay between connections
        await asyncio.sleep(0.5)
    
    print(f"📊 Stability test result: {successful_connections}/{total_tests} connections successful")
    return successful_connections == total_tests

async def main():
    """Run all WebSocket tests"""
    print("🚀 Starting comprehensive WebSocket test suite")
    print("=" * 60)
    
    # Test 1: Basic connection and ping/pong
    success1 = await test_websocket_connection()
    
    # Test 2: Connection stability
    success2 = await test_connection_stability()
    
    print("\n" + "=" * 60)
    print("🏁 Test Suite Summary:")
    print(f"   - Connection & Ping/Pong: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   - Connection Stability: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("🎉 All tests passed! WebSocket implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
