import socket
import threading
import json
import time
from datetime import datetime
from typing import Dict, Optional

class PetChatServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8888):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        
        # Connected clients: {user_id: {"socket": socket, "addr": addr, "name": name, "avatar": avatar}}
        self.clients: Dict[str, Dict] = {}
        self.clients_lock = threading.Lock()
        
    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"[SERVER] Listening on {self.host}:{self.port}")
            
            while self.running:
                client_sock, addr = self.server_socket.accept()
                print(f"[SERVER] New connection from {addr}")
                
                # Handle client in separate thread
                threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True).start()
                
        except Exception as e:
            print(f"[SERVER] Start error: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
                
    def _handle_client(self, client_sock: socket.socket, addr):
        """Handle individual client connection"""
        user_id = None
        
        try:
            while self.running:
                # Read message length (4 bytes)
                length_data = self._recv_all(client_sock, 4)
                if not length_data:
                    break
                    
                length = int.from_bytes(length_data, 'big')
                data = self._recv_all(client_sock, length)
                
                if not data:
                    break
                    
                message = json.loads(data.decode('utf-8'))
                msg_type = message.get("type")
                
                if msg_type == "register":
                    user_id = self._handle_register(client_sock, addr, message)
                elif msg_type == "chat_message":
                    self._handle_chat_message(message)
                elif msg_type == "get_online_users":
                    self._send_online_users(client_sock)
                elif msg_type in ["typing_status", "ai_request", "ai_suggestion", "ai_emotion", "ai_memories"]:
                     # Broadcast these events to all users
                     self._broadcast(message)
                    
        except Exception as e:
            print(f"[SERVER] Client error {addr}: {e}")
        finally:
            self._handle_disconnect(user_id)
            client_sock.close()
            
    def _recv_all(self, sock: socket.socket, n: int) -> Optional[bytes]:
        """Helper to receive exactly n bytes"""
        data = b''
        while len(data) < n:
            try:
                packet = sock.recv(n - len(data))
                if not packet:
                    return None
                data += packet
            except:
                return None
        return data
        
    def _send_json(self, sock: socket.socket, message: dict):
        """Send JSON message to socket"""
        try:
            data = json.dumps(message).encode('utf-8')
            length = len(data).to_bytes(4, 'big')
            sock.sendall(length + data)
        except Exception as e:
            print(f"[SERVER] Send error: {e}")

    def _handle_register(self, sock: socket.socket, addr, message: dict) -> str:
        """Register a new user"""
        user_id = message.get("user_id")
        user_name = message.get("user_name")
        avatar = message.get("avatar", "")
        
        if user_id:
            with self.clients_lock:
                self.clients[user_id] = {
                    "socket": sock,
                    "addr": addr,
                    "name": user_name,
                    "avatar": avatar,
                    "ip": addr[0]
                }
            print(f"[SERVER] Registered user: {user_name} ({user_id})")
            
            # Broadcast presence to all
            self._broadcast({
                "type": "presence",
                "user_id": user_id,
                "user_name": user_name,
                "avatar": avatar,
                "status": "online"
            })
            
            # Send current online list to new user
            self._send_online_users(sock)
            
        return user_id

    def _handle_chat_message(self, message: dict):
        """Route chat message"""
        target = message.get("target", "public")
        
        if target == "public":
            print(f"[SERVER] Broadcasting public message from {message.get('sender_name')}")
            self._broadcast(message)
        else:
            # Private message
            with self.clients_lock:
                target_client = self.clients.get(target)
                if target_client:
                    print(f"[SERVER] Forwarding private message to {target_client['name']}")
                    self._send_json(target_client["socket"], message)
                    
                    # Also send back to sender (echo) so they know it was sent?
                    # Or client handles their own "sent" UI. 
                    # Usually client handles own UI, but server helps with sync.
                    # For now, just forward.

    def _handle_disconnect(self, user_id: str):
        """Handle user disconnect"""
        if user_id:
            with self.clients_lock:
                if user_id in self.clients:
                    del self.clients[user_id]
            
            print(f"[SERVER] User disconnected: {user_id}")
            self._broadcast({
                "type": "presence",
                "user_id": user_id,
                "status": "offline"
            })

    def _broadcast(self, message: dict):
        """Send message to all connected clients"""
        with self.clients_lock:
            for uid, client in self.clients.items():
                self._send_json(client["socket"], message)

    def _send_online_users(self, sock: socket.socket):
        """Send list of currently online users"""
        users_list = []
        with self.clients_lock:
            for uid, info in self.clients.items():
                users_list.append({
                    "id": uid,
                    "name": info["name"],
                    "avatar": info["avatar"],
                    "ip": info["ip"]
                })
        
        self._send_json(sock, {
            "type": "online_users_list",
            "users": users_list
        })

if __name__ == "__main__":
    server = PetChatServer()
    server.start()
