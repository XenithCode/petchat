"""
AI Session Manager
Manages AI conversation contexts per conversation ID on the server.
Handles history tracking, snapshot merging, and token usage tracking.
"""
from typing import Dict, List, Optional, Any
import time
import threading
from datetime import datetime

class AISessionManager:
    """
    Manages AI contexts for different conversations.
    Thread-safe implementation for server use.
    """
    
    def __init__(self):
        # Conversation contexts: {conversation_id: {"messages": [], "last_active": timestamp}}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        # Token usage tracking: {conversation_id: total_tokens}
        self.token_usage: Dict[str, int] = {}
        
        # Limit history size per session to avoid token overflow
        self.max_history_len = 50
    
    def get_context(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get current context for a conversation"""
        with self.lock:
            if conversation_id not in self.sessions:
                return []
            return self.sessions[conversation_id]["messages"]
    
    def update_context(self, conversation_id: str, snapshot: Optional[List[Dict[str, Any]]] = None):
        """
        Update context for a conversation.
        If snapshot is provided and session is empty/stale, use snapshot.
        Otherwise, we assume server intercepts chat messages to keep context up to date (to be implemented).
        For now, we rely heavily on the snapshot for the AI request if server history is empty.
        """
        with self.lock:
            current_time = time.time()
            
            if conversation_id not in self.sessions:
                self.sessions[conversation_id] = {
                    "messages": [],
                    "last_active": current_time
                }
            
            session = self.sessions[conversation_id]
            session["last_active"] = current_time
            
            # Cold-start recovery or sync:
            # If we have a snapshot and our local history is empty or significantly different,
            # we accept the snapshot.
            if snapshot:
                # Simple logic: if server has fewer messages than snapshot, use snapshot
                # In a real sync scenario, we'd do ID matching, but simple replacement is safer for now
                # to ensure AI sees what the user sees.
                if len(session["messages"]) < len(snapshot):
                    session["messages"] = snapshot
                
                # Update last active again
                session["last_active"] = time.time()
    
    def add_message(self, conversation_id: str, sender: str, content: str, is_user: bool = True):
        """Add a single message to context (for real-time tracking)"""
        with self.lock:
            if conversation_id not in self.sessions:
                self.sessions[conversation_id] = {
                    "messages": [],
                    "last_active": time.time()
                }
            
            message = {
                "role": "user" if is_user else "assistant",
                "content": content,
                # Add sender info if needed by AI service, but OpenAI format is strictly role/content
                # We can prepend sender name to content if it's a multi-user chat
            }
            
            if is_user and sender:
                message["content"] = f"{sender}: {content}"
            
            self.sessions[conversation_id]["messages"].append(message)
            
            # Trim history
            if len(self.sessions[conversation_id]["messages"]) > self.max_history_len:
                self.sessions[conversation_id]["messages"] = self.sessions[conversation_id]["messages"][-self.max_history_len:]
                
            self.sessions[conversation_id]["last_active"] = time.time()

    def track_usage(self, conversation_id: str, tokens: int):
        """Track token usage"""
        with self.lock:
            if conversation_id not in self.token_usage:
                self.token_usage[conversation_id] = 0
            self.token_usage[conversation_id] += tokens
            
    def get_usage(self, conversation_id: str = None) -> Dict[str, int]:
        """Get token usage stats"""
        with self.lock:
            if conversation_id:
                return {conversation_id: self.token_usage.get(conversation_id, 0)}
            return self.token_usage.copy()

    def cleanup_inactive(self, timeout_seconds: int = 3600):
        """Cleanup inactive sessions to free memory"""
        with self.lock:
            current_time = time.time()
            to_remove = []
            for cid, session in self.sessions.items():
                if current_time - session["last_active"] > timeout_seconds:
                    to_remove.append(cid)
            
            for cid in to_remove:
                del self.sessions[cid]
                # We might want to keep token usage stats even if session is cleared
