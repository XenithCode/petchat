import socket
import json
import threading
import time
import sys
import os
import random
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import PetChatServer

# Performance test parameters
NUM_CLIENTS = 20
MESSAGES_PER_CLIENT = 10
MAX_LATENCY_MS = 200

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
        # print(f"Receive error: {e}")
        return None

def send_json(sock, data):
    try:
        payload = json.dumps(data).encode('utf-8')
        header = len(payload).to_bytes(4, 'big')
        sock.sendall(header + payload)
    except:
        pass

def client_worker(client_id, stats):
    """Simulate a client sending and receiving messages"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("127.0.0.1", 8899))
        
        # Register
        send_json(sock, {
            "type": "register",
            "user_id": f"user_{client_id}",
            "user_name": f"User {client_id}",
            "avatar": "cat"
        })
        
        # Read registration ack/online list
        msg = receive_json(sock)
        
        # Send loop
        for i in range(MESSAGES_PER_CLIENT):
            content = f"Message {i} from {client_id} at {time.time()}"
            send_time = time.time()
            send_json(sock, {
                "type": "chat_message",
                "sender_id": f"user_{client_id}",
                "sender_name": f"User {client_id}",
                "content": content,
                "target": "public"
            })
            stats['sent'] += 1
            time.sleep(random.uniform(0.05, 0.15)) # Simulate typing delay
            
    except Exception as e:
        print(f"Client {client_id} error: {e}")
        stats['errors'] += 1
    finally:
        sock.close()

def monitor_latency(stats):
    """Monitor server broadcast latency"""
    # Connect a monitor client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 8899))
    send_json(sock, {
        "type": "register",
        "user_id": "monitor",
        "user_name": "Monitor",
        "avatar": "monitor"
    })
    
    try:
        while True:
            msg = receive_json(sock)
            if not msg:
                break
            
            if msg.get("type") == "chat_message":
                content = msg.get("content", "")
                if "at " in content:
                    try:
                        sent_time = float(content.split("at ")[1])
                        latency = (time.time() - sent_time) * 1000
                        stats['latencies'].append(latency)
                        stats['received'] += 1
                    except:
                        pass
    except:
        pass
    finally:
        sock.close()

def run_stress_test():
    print(f"Starting stress test with {NUM_CLIENTS} clients, {MESSAGES_PER_CLIENT} msgs each...")
    
    # Start Server
    server = PetChatServer(host="127.0.0.1", port=8899)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(1) 
    
    stats = {
        'sent': 0,
        'received': 0,
        'errors': 0,
        'latencies': []
    }
    
    # Start monitor
    monitor_thread = threading.Thread(target=monitor_latency, args=(stats,), daemon=True)
    monitor_thread.start()
    
    # Start clients
    with ThreadPoolExecutor(max_workers=NUM_CLIENTS) as executor:
        futures = [executor.submit(client_worker, i, stats) for i in range(NUM_CLIENTS)]
        
        # Wait for all to finish
        for future in futures:
            future.result()
            
    time.sleep(2) # Wait for remaining messages
    
    server.stop()
    
    # Report
    print("\n=== Performance Report ===")
    print(f"Total Sent: {stats['sent']}")
    print(f"Total Received (Monitor): {stats['received']}")
    print(f"Errors: {stats['errors']}")
    
    if stats['latencies']:
        avg_latency = sum(stats['latencies']) / len(stats['latencies'])
        max_latency = max(stats['latencies'])
        print(f"Average Latency: {avg_latency:.2f} ms")
        print(f"Max Latency: {max_latency:.2f} ms")
        
        if avg_latency < MAX_LATENCY_MS:
            print("PASS: Average latency within 200ms limit.")
        else:
            print("FAIL: High latency detected.")
    else:
        print("FAIL: No messages received.")

if __name__ == "__main__":
    run_stress_test()
