"""
Network Client for PetChat - Clean Client-Server Architecture
Manages TCP connection to the server and handles message routing.
"""
import socket
import threading
import json
from typing import Optional, List, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal

# Use shared protocol module
from core.protocol import (
    Protocol, MessageType, HEADER_SIZE,
    pack_message, unpack_header, verify_crc,
    AIAnalysisRequest
)


class NetworkManager(QObject):
    """
    Client-side network manager.
    Handles connection to server, sending and receiving messages.
    """
    
    # Connection signals
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    connection_error = pyqtSignal(str)
    
    # Message signal: sender_id, sender_name, content, target, sender_avatar
    message_received = pyqtSignal(str, str, str, str, str)
    
    # User presence signals
    user_joined = pyqtSignal(str, str, str)  # user_id, user_name, avatar
    user_left = pyqtSignal(str)  # user_id
    online_users_received = pyqtSignal(list)  # list of user dicts
    
    # Typing signal
    typing_status_received = pyqtSignal(str, str, bool)  # user_id, user_name, is_typing
    
    # AI signals - server sends AI results to client
    ai_suggestion_received = pyqtSignal(str, dict)  # conversation_id, suggestion dict
    ai_emotion_received = pyqtSignal(str, dict)  # conversation_id, emotion scores
    ai_memory_received = pyqtSignal(str, list)  # conversation_id, memories list

    def __init__(self):
        super().__init__()
        self.socket: Optional[socket.socket] = None
        self.running = False
        
        self.server_ip = "127.0.0.1"
        self.server_port = 8888
        
        self.user_id = ""
        self.user_name = ""
        self.avatar = ""
        
        self._send_lock = threading.Lock()
        self._recv_thread: Optional[threading.Thread] = None

    def connect_to_server(self, server_ip: str, port: int, user_id: str, user_name: str, avatar: str = ""):
        """Connect to the server and register"""
        self.server_ip = server_ip
        self.server_port = port
        self.user_id = user_id
        self.user_name = user_name
        self.avatar = avatar
        
        # Connect in background thread
        threading.Thread(target=self._connect_thread, daemon=True).start()

    def _connect_thread(self):
        """Background connection thread"""
        try:
            print(f"[Network] Connecting to {self.server_ip}:{self.server_port}...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.server_ip, self.server_port))
            self.socket.settimeout(None)
            
            self.running = True
            print("[Network] Connected!")
            
            # Register with server
            self._send_message({
                "type": "register",
                "user_id": self.user_id,
                "user_name": self.user_name,
                "avatar": self.avatar
            })
            
            self.connected.emit()
            
            # Start receive loop
            self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._recv_thread.start()
            
        except Exception as e:
            print(f"[Network] Connection failed: {e}")
            self.running = False
            self.connection_error.emit(str(e))

    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.disconnected.emit()

    def stop(self):
        """Stop the network manager"""
        self.disconnect()

    def send_chat_message(self, target: str, content: str):
        """Send a chat message"""
        self._send_message({
            "type": "chat_message",
            "sender_id": self.user_id,
            "sender_name": self.user_name,
            "sender_avatar": self.avatar,
            "target": target,
            "content": content
        })

    def send_typing_status(self, is_typing: bool):
        """Send typing status"""
        self._send_message({
            "type": "typing_status",
            "sender_id": self.user_id,
            "sender_name": self.user_name,
            "is_typing": is_typing
        })

    def send_ai_analysis_request(self, conversation_id: str, context_snapshot: List[Dict[str, Any]] = None):
        """
        Send AI analysis request to server.
        
        Args:
            conversation_id: ID of the conversation to analyze
            context_snapshot: Recent messages for cold-start recovery (optional but recommended)
                             Server uses this if its session is empty or stale.
        """
        request = AIAnalysisRequest(
            conversation_id=conversation_id,
            sender_id=self.user_id,
            sender_name=self.user_name,
            context_snapshot=context_snapshot
        )
        self._send_message(request.to_dict())

    def _send_message(self, message: dict):
        """Send a message to the server"""
        if not self.socket or not self.running:
            print("[Network] Cannot send - not connected")
            return
            
        try:
            with self._send_lock:
                packet = pack_message(message)
                self.socket.sendall(packet)
                print(f"[Network] Sent: {message.get('type')}")
        except Exception as e:
            print(f"[Network] Send error: {e}")
            self.disconnect()

    def _receive_loop(self):
        """Main receive loop"""
        print("[Network] Receive loop started")
        
        while self.running and self.socket:
            try:
                # Read header
                header = self._recv_exact(HEADER_SIZE)
                if not header:
                    print("[Network] Connection closed by server")
                    break
                
                length, expected_crc = unpack_header(header)
                
                # Read payload
                payload = self._recv_exact(length)
                if not payload:
                    print("[Network] Connection lost during payload read")
                    break
                
                # Verify CRC
                if not verify_crc(payload, expected_crc):
                    print("[Network] CRC mismatch, skipping message")
                    continue
                
                # Parse and handle message
                try:
                    message = json.loads(payload.decode('utf-8'))
                    self._handle_message(message)
                except json.JSONDecodeError:
                    print("[Network] Invalid JSON received")
                    
            except Exception as e:
                if self.running:
                    print(f"[Network] Receive error: {e}")
                break
        
        print("[Network] Receive loop ended")
        self.running = False
        self.disconnected.emit()

    def _recv_exact(self, n: int) -> Optional[bytes]:
        """Receive exactly n bytes"""
        data = b''
        while len(data) < n and self.running:
            try:
                chunk = self.socket.recv(n - len(data))
                if not chunk:
                    return None
                data += chunk
            except:
                return None
        return data if len(data) == n else None

    def _handle_message(self, message: dict):
        """Handle incoming message"""
        msg_type = message.get("type")
        print(f"[Network] Received: {msg_type}")
        
        if msg_type == "chat_message":
            self.message_received.emit(
                message.get("sender_id", ""),
                message.get("sender_name", "Unknown"),
                message.get("content", ""),
                message.get("target", "public"),
                message.get("sender_avatar", "")
            )
            
        elif msg_type == "user_joined":
            self.user_joined.emit(
                message.get("user_id", ""),
                message.get("user_name", "Unknown"),
                message.get("avatar", "")
            )
            
        elif msg_type == "user_left":
            self.user_left.emit(message.get("user_id", ""))
            
        elif msg_type == "online_users":
            users = message.get("users", [])
            self.online_users_received.emit(users)
            
        elif msg_type == "typing_status":
            sender_id = message.get("sender_id", "")
            if sender_id != self.user_id:  # Ignore own typing status
                self.typing_status_received.emit(
                    sender_id,
                    message.get("sender_name", "Someone"),
                    message.get("is_typing", False)
                )
        
        # AI message handlers - from server
        elif msg_type == MessageType.AI_SUGGESTION.value:
            self.ai_suggestion_received.emit(
                message.get("conversation_id", ""),
                {
                    "title": message.get("title", "AI 建议"),
                    "content": message.get("content", ""),
                    "type": message.get("suggestion_type", "suggestion")
                }
            )
        
        elif msg_type == MessageType.AI_EMOTION.value:
            self.ai_emotion_received.emit(
                message.get("conversation_id", ""),
                message.get("scores", {})
            )
        
        elif msg_type == MessageType.AI_MEMORY.value:
            self.ai_memory_received.emit(
                message.get("conversation_id", ""),
                message.get("memories", [])
            )
