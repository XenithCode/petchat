import socket
import json
import threading
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import PetChatServer

def receive_json(sock):
    try:
        header = sock.recv(4)
        if not header:
            return None
        length = int.from_bytes(header, 'big')
        data = b''
        while len(data) < length:
            packet = sock.recv(length - len(data))
            if not packet:
                return None
            data += packet
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"Receive error: {e}")
        return None

def send_json(sock, data):
    payload = json.dumps(data).encode('utf-8')
    header = len(payload).to_bytes(4, 'big')
    sock.sendall(header + payload)

def test_cs_flow():
    # Start Server
    server = PetChatServer(host="127.0.0.1", port=8899)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(1) # Wait for server start

    try:
        # Client A
        client_a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_a.connect(("127.0.0.1", 8899))
        
        # Client B
        client_b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_b.connect(("127.0.0.1", 8899))

        # Register A
        send_json(client_a, {
            "type": "register",
            "user_id": "user_a",
            "user_name": "Alice",
            "avatar": "cat"
        })
        
        # Register B
        send_json(client_b, {
            "type": "register",
            "user_id": "user_b",
            "user_name": "Bob",
            "avatar": "dog"
        })

        time.sleep(0.5)

        # Test 1: Chat Message A -> B
        print("Testing Chat Message A -> B...")
        msg_content = "Hello Bob"
        send_json(client_a, {
            "type": "chat_message",
            "sender_id": "user_a",
            "sender_name": "Alice",
            "content": msg_content,
            "target": "user_b" # Server logic for target routing needs verification
        })
        
        # Server currently broadcasts chat messages if target is public, or logic might be missing for private routing?
        # Let's check server.py again.
        # It calls self._handle_chat_message(message)
        
        # Client B should receive it.
        # Note: server.py _handle_chat_message might broadcast to all or selective.
        # I need to handle potential 'presence' messages first.
        
        start_time = time.time()
        received_chat = False
        while time.time() - start_time < 2:
            msg = receive_json(client_b)
            if msg and msg.get("type") == "chat_message":
                if msg.get("content") == msg_content:
                    print("PASS: Client B received chat message.")
                    received_chat = True
                    break
        
        if not received_chat:
            print("FAIL: Client B did not receive chat message.")

        # Test 2: AI Request Broadcast
        print("Testing AI Request Broadcast...")
        send_json(client_b, {
            "type": "ai_request",
            "sender_id": "user_b"
        })
        
        # Client A should receive it
        start_time = time.time()
        received_ai = False
        while time.time() - start_time < 2:
            msg = receive_json(client_a)
            if msg and msg.get("type") == "ai_request":
                print("PASS: Client A received AI request.")
                received_ai = True
                break
        
        if not received_ai:
            print("FAIL: Client A did not receive AI request.")

    finally:
        client_a.close()
        client_b.close()
        server.stop()
        print("Test finished.")

if __name__ == "__main__":
    test_cs_flow()
