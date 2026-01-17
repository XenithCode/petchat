"""
Network Client for PetChat Server-Client Architecture.
Manages TCP connection to the central server.
"""
import socket
import threading
import json
import time
from typing import Optional, Dict, List
from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker

class NetworkManager(QObject):
    """
    Client-side Network Manager.
    Connects to PetChatServer, handles registration, and routes messages.
    """
    
    # Signals
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    connection_status_changed = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str)
    
    # Message signals
    # sender_id, sender_name, content, target, sender_avatar
    message_received = pyqtSignal(str, str, str, str, str)
    
    # Presence signals (mapped from server events)
    user_discovered = pyqtSignal(dict)  # {id, name, avatar, ip}
    user_left = pyqtSignal(str)         # user_id
    online_users_received = pyqtSignal(list) # list of user dicts
    
    # AI signals (keep for compatibility, though maybe unused in pure chat)
    ai_suggestion_received = pyqtSignal(dict)
    ai_emotion_received = pyqtSignal(dict)
    ai_memories_received = pyqtSignal(list)
    ai_request_received = pyqtSignal()
    typing_status_changed = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.server_ip = "127.0.0.1"
        self.server_port = 8888
        
        self.user_id: str = ""
        self.user_name: str = ""
        self.avatar: str = ""
        
        self._send_lock = QMutex()
        self._send_queue: List[dict] = []
        self._send_queue_timer = threading.Thread(target=self._process_send_queue, daemon=True)
        self._recv_thread: Optional[threading.Thread] = None
        
    def _process_send_queue(self):
        """Worker to process send queue"""
        while True:
            if not self.running:
                time.sleep(0.1)
                continue
                
            msg = None
            with QMutexLocker(self._send_lock):
                if self._send_queue:
                    msg = self._send_queue.pop(0)
            
            if msg:
                self._send_json_internal(msg)
            else:
                time.sleep(0.05)
                
    def connect_to_server(self, server_ip: str, port: int, user_id: str, user_name: str, avatar: str):
        """Connect to central server and register"""
        self.server_ip = server_ip
        self.server_port = port
        self.user_id = user_id
        self.user_name = user_name
        self.avatar = avatar
        
        # Start connection in thread to avoid freezing UI
        threading.Thread(target=self._connect_task, daemon=True).start()
        
        # Start queue processor if not already running
        if not self._send_queue_timer.is_alive():
             self._send_queue_timer.start()

    def _connect_task(self):
        """Connection logic running in background"""
        try:
            self.connection_status_changed.emit(False, f"Connecting to {self.server_ip}:{self.server_port}...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0) # Connection timeout
            self.socket.connect((self.server_ip, self.server_port))
            self.socket.settimeout(None) # Reset timeout for blocking operations
            
            self.running = True
            self.connected.emit()
            self.connection_status_changed.emit(True, f"Connected to {self.server_ip}")
            
            # Send registration
            self._register()
            
            # Start receive loop
            self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._recv_thread.start()
            
        except Exception as e:
            self.running = False
            self.error_occurred.emit(f"Connection failed: {e}")
            self.connection_status_changed.emit(False, f"Connection failed: {e}")

    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.disconnected.emit()

    def _register(self):
        """Send register message"""
        msg = {
            "type": "register",
            "user_id": self.user_id,
            "user_name": self.user_name,
            "avatar": self.avatar
        }
        self.send_json(msg)

    def send_chat_message(self, target: str, content: str):
        """
        Send chat message.
        target: 'public' or user_id
        """
        msg = {
            "type": "chat_message",
            "sender_id": self.user_id,
            "sender_name": self.user_name,
            "sender_avatar": self.avatar,
            "target": target,
            "content": content
        }
        self.send_json(msg)
        
    def send_json(self, message: dict):
        """Enqueue message to be sent"""
        with QMutexLocker(self._send_lock):
            self._send_queue.append(message)
            
    def _send_json_internal(self, message: dict):
        """Send raw JSON message (internal use)"""
        if not self.socket or not self.running:
            return
            
        try:
            data = json.dumps(message).encode('utf-8')
            length = len(data).to_bytes(4, 'big')
            
            self.socket.sendall(length + data)
        except Exception as e:
            print(f"[Network] Send error: {e}")
            self.error_occurred.emit(f"Send error: {e}")
            self.disconnect()

    def stop(self):
        """Stop network manager"""
        self.disconnect()

    def send_typing(self, is_typing: bool):
        """Send typing status"""
        # TODO: Add target support for typing
        msg = {
            "type": "typing_status",
            "is_typing": is_typing,
            "sender_id": self.user_id,
            "sender_name": self.user_name
        }
        self.send_json(msg)

    def send_ai_request(self):
        """Send request for AI to Generate something"""
        msg = {
            "type": "ai_request",
            "sender_id": self.user_id
        }
        self.send_json(msg)

    def send_ai_suggestion(self, suggestion: dict):
        """Send AI suggestion to others"""
        msg = {
            "type": "ai_suggestion",
            "suggestion": suggestion,
            "sender_id": self.user_id
        }
        self.send_json(msg)

    def send_ai_emotion(self, emotion: dict):
        """Send AI emotion to others"""
        msg = {
            "type": "ai_emotion",
            "emotion": emotion,
            "sender_id": self.user_id
        }
        self.send_json(msg)

    def send_ai_memories(self, memories: list):
        """Send AI memories to others"""
        msg = {
            "type": "ai_memories",
            "memories": memories,
            "sender_id": self.user_id
        }
        self.send_json(msg)
        
    def _receive_loop(self):
        """Main receive loop"""
        while self.running and self.socket:
            try:
                # Read length
                length_data = self._recv_all(self.socket, 4)
                if not length_data:
                    break
                
                length = int.from_bytes(length_data, 'big')
                data = self._recv_all(self.socket, length)
                
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                self._process_message(message)
                
            except Exception as e:
                print(f"[Network] Receive error: {e}")
                if self.running:
                    self.error_occurred.emit(f"Connection lost: {e}")
                break
        
        self.running = False
        self.disconnected.emit()
        self.connection_status_changed.emit(False, "Disconnected")

    def _recv_all(self, sock: socket.socket, n: int) -> Optional[bytes]:
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

    def _process_message(self, message: dict):
        """Handle incoming messages"""
        msg_type = message.get("type")
        
        if msg_type == "chat_message":
            sender_id = message.get("sender_id", "")
            sender_name = message.get("sender_name", "Unknown")
            content = message.get("content", "")
            target = message.get("target", "public")
            sender_avatar = message.get("sender_avatar", "")
            
            # We trust the server to route correctly
            self.message_received.emit(sender_id, sender_name, content, target, sender_avatar)
            
        elif msg_type == "presence":
            # Server tells us about a user event
            status = message.get("status")
            if status == "online":
                self.user_discovered.emit({
                    "id": message.get("user_id"),
                    "name": message.get("user_name"),
                    "avatar": message.get("avatar"),
                    "ip": "Server Managed" # We don't know their real IP, nor do we need to
                })
            elif status == "offline":
                self.user_left.emit(message.get("user_id"))
                
        elif msg_type == "online_users_list":
            users = message.get("users", [])
            self.online_users_received.emit(users)
            # Also emit individual discovery for compatibility
            for u in users:
                if u["id"] != self.user_id:
                    self.user_discovered.emit(u)
                    
        elif msg_type == "typing_status":
            sender_id = message.get("sender_id")
            if sender_id != self.user_id:
                is_typing = message.get("is_typing", False)
                self.typing_status_changed.emit(message.get("sender_name", "Someone"), is_typing)
