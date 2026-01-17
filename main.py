"""Main entry point for pet-chat application"""
import sys
import argparse
import socket
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup, QMessageBox
from PyQt6.QtCore import Qt, QTimer

from core.network import NetworkManager
from core.database import Database
from core.ai_service import AIService
from core.config_manager import ConfigManager
from core.window_manager import window_manager
from ui.main_window import MainWindow
from ui.user_profile_dialog import UserProfileDialog
from ui.api_config_dialog import APIConfigDialog
from config.settings import Settings
from ui.theme import Theme


class RoleSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_role = "host"
        self.host_ip = ""
        self.port_text = str(Settings.DEFAULT_PORT)
        self.relay_port_text = str(Settings.DEFAULT_RELAY_PORT)
        self.use_relay = False
        self.relay_host = ""
        self.room_id = "default"
        self.setWindowTitle("选择启动模式")
        self.setModal(True)
        self.setMinimumWidth(420)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(Theme.SPACING_MD)
        self.setStyleSheet(Theme.get_stylesheet())

        title = QLabel("选择启动模式")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: {Theme.FONT_SIZE_XL}px; font-weight: 600; color: {Theme.TEXT_PRIMARY};"
        )
        layout.addWidget(title)
        
        hint = QLabel("请选择您的角色：房主负责创建房间，访客可以加入现有房间。可选使用中转服务器实现跨网段连接。")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: {Theme.FONT_SIZE_SM}px;")
        layout.addWidget(hint)

        role_layout = QHBoxLayout()
        host_radio = QRadioButton("Host（房主）")
        guest_radio = QRadioButton("Guest（访客）")
        host_radio.setChecked(True)

        group = QButtonGroup(self)
        group.addButton(host_radio)
        group.addButton(guest_radio)

        role_layout.addWidget(host_radio)
        role_layout.addWidget(guest_radio)
        role_layout.addStretch()
        layout.addLayout(role_layout)

        ip_label = QLabel("Host IP（仅 Guest 需要填写，或中转服务器地址）")
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("例如 192.168.1.100")
        self.ip_input.setEnabled(False)

        layout.addWidget(ip_label)
        layout.addWidget(self.ip_input)

        port_label = QLabel("端口")
        self.port_input = QLineEdit(self.port_text)
        layout.addWidget(port_label)
        layout.addWidget(self.port_input)

        relay_label = QLabel("中转服务器配置（可选，用于不在同一网段时）")
        relay_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: {Theme.FONT_SIZE_SM}px;")
        layout.addWidget(relay_label)

        relay_layout = QHBoxLayout()
        self.relay_checkbox = QRadioButton("使用中转服务器")
        relay_layout.addWidget(self.relay_checkbox)
        layout.addLayout(relay_layout)

        relay_host_label = QLabel("中转服务器地址")
        self.relay_host_input = QLineEdit()
        self.relay_host_input.setPlaceholderText("例如 your-vps.com 或 1.2.3.4")
        relay_port_label = QLabel("中转端口")
        self.relay_port_input = QLineEdit(self.relay_port_text)
        self.relay_port_input.setPlaceholderText("默认 9000")
        room_id_label = QLabel("房间ID（Host 与 Guest 需一致）")
        self.room_id_input = QLineEdit()
        self.room_id_input.setPlaceholderText("例如 my-room-1")

        layout.addWidget(relay_host_label)
        layout.addWidget(self.relay_host_input)
        layout.addWidget(relay_port_label)
        layout.addWidget(self.relay_port_input)
        layout.addWidget(room_id_label)
        layout.addWidget(self.room_id_input)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QPushButton("取消")
        ok_btn = QPushButton("确定")
        cancel_btn.setStyleSheet(
            f"QPushButton {{ background-color: {Theme.SECONDARY}; color: {Theme.PRIMARY_TEXT}; }}"
        )
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        def on_host_selected(checked):
            if checked:
                self.selected_role = "host"
                self.ip_input.setEnabled(False)

        def on_guest_selected(checked):
            if checked:
                self.selected_role = "guest"
                self.ip_input.setEnabled(True)

        host_radio.toggled.connect(on_host_selected)
        guest_radio.toggled.connect(on_guest_selected)

        def on_ok():
            self.host_ip = self.ip_input.text().strip()
            self.port_text = self.port_input.text().strip() or str(Settings.DEFAULT_PORT)
            self.use_relay = self.relay_checkbox.isChecked()
            self.relay_host = self.relay_host_input.text().strip()
            self.relay_port_text = self.relay_port_input.text().strip()
            self.room_id = self.room_id_input.text().strip() or "default"
            self.accept()

        def on_cancel():
            self.reject()

        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(on_cancel)


class PetChatApp:
    """Main application controller"""
    
    def __init__(self, is_host: bool, host_ip: str, port: int, from_cli_args: bool):
        print("[DEBUG] PetChatApp.__init__ starting...")
        
        # Create QApplication first, before any other PyQt6 operations
        print("[DEBUG] Creating QApplication...")
        self.app = QApplication(sys.argv)
        print("[DEBUG] QApplication created")
        
        # Apply global theme
        print("[DEBUG] Applying theme...")
        self.app.setStyleSheet(Theme.get_stylesheet())
        print("[DEBUG] Theme applied")
        
        self.is_host = is_host
        self.host_ip = host_ip
        self.port = port
        self.from_cli_args = from_cli_args
        self.use_relay = False
        self.relay_host = Settings.DEFAULT_RELAY_HOST
        self.relay_port = Settings.DEFAULT_RELAY_PORT
        self.room_id = "default"
        print(f"[DEBUG] Configuration: is_host={is_host}, host_ip={host_ip}, port={port}, from_cli_args={from_cli_args}")
        
        print("[DEBUG] Creating ConfigManager...")
        self.config_manager = ConfigManager()
        print("[DEBUG] ConfigManager created")

        print("[DEBUG] Initializing user profile...")
        self.current_user_id, self.current_user_name, self.current_user_avatar = self._ensure_user_profile()
        print(f"[DEBUG] User profile: id={self.current_user_id}, name={self.current_user_name}, avatar={self.current_user_avatar}")
        
        print("[DEBUG] Creating Database...")
        self.db = Database()
        print("[DEBUG] Database created")
        
        # Register local user in database
        self.db.upsert_user(self.current_user_id, self.current_user_name, self.current_user_avatar, is_online=True)
        
        self.current_conversation_id = "default"  # Changed from session_id
        self.loaded_message_limit = 50
        
        self.ai_service = None
        self.discovery_service = None  # Will be initialized in start()
        
        print("[DEBUG] Creating MainWindow...")
        self.window = MainWindow(is_host=is_host, user_name=self.current_user_name)
        print("[DEBUG] MainWindow created")
        
        print("[DEBUG] Registering window...")
        self.window_id = window_manager().register_window(self.window)
        print(f"[DEBUG] Window registered with ID: {self.window_id}")
        
        self.app.aboutToQuit.connect(lambda: window_manager().unregister_window(self.window_id))
        self.message_count = 0
        print("[DEBUG] PetChatApp.__init__ completed")
        self._load_messages(reset=True)
        self._load_conversations_list()

    def _ensure_user_profile(self):
        """Ensure user profile exists with persistent UUID"""
        from core.models import generate_uuid
        
        # Get or generate user ID
        user_id = self.config_manager.get_user_id()
        if not user_id:
            user_id = generate_uuid()
            self.config_manager.set_user_id(user_id)
            print(f"[DEBUG] Generated new user ID: {user_id}")
        
        name = self.config_manager.get_user_name()
        avatar = self.config_manager.get_user_avatar()
        if name and 2 <= len(name.strip()) <= 20:
            return user_id, name.strip(), avatar or ""

        dialog = UserProfileDialog(current_name=name or "", current_avatar=avatar or "")
        result = dialog.exec()
        if result != QDialog.DialogCode.Accepted:
            sys.exit(0)
        final_name = dialog.user_name()
        final_avatar = dialog.avatar()
        self.config_manager.set_user_profile(final_name, final_avatar, user_id)
        return user_id, final_name, final_avatar

    def _load_messages(self, reset: bool = False):
        if reset:
            self.loaded_message_limit = 50
        try:
            messages = self.db.get_recent_messages(self.loaded_message_limit, conversation_id=self.current_conversation_id)
            self.window.clear_messages()
            for msg in messages:
                ts = msg.get("timestamp", "")
                display_ts = ts[11:16] if len(ts) >= 16 and ts[10] == "T" else ts[-5:]
                # Determine if this message is from me
                is_me = msg.get("sender_id") == self.current_user_id
                self.window.add_message(msg["sender"], msg["content"], display_ts, is_me=is_me)
        except Exception as e:
            print(f"Error loading message history: {e}")
    
    def _load_conversations_list(self):
        """Load conversations from database into sidebar"""
        try:
            conversations = self.db.get_conversations()
            self.window.load_conversations(conversations)
        except Exception as e:
            print(f"Error loading conversations: {e}")
    
    
    def _setup_connections(self):
        """Setup signal/slot connections"""
        self.network.message_received.connect(self._on_message_received)
        self.network.connection_status_changed.connect(self._on_connection_status)
        self.network.error_occurred.connect(self._on_network_error)
        self.network.ai_suggestion_received.connect(self._on_remote_suggestion)
        self.network.ai_emotion_received.connect(self._on_remote_emotion)
        self.network.ai_memories_received.connect(self._on_remote_memories)
        self.network.ai_request_received.connect(self._on_remote_ai_request)
        
        self.window.message_sent.connect(self._on_message_sent)
        self.window.ai_requested.connect(self._on_ai_requested)
        self.window.conversation_selected.connect(self._on_conversation_selected)
        self.window.load_more_requested.connect(self._on_load_more_requested)
        self.window.typing_changed.connect(self._on_local_typing_changed)
        self.window.reset_user_requested.connect(self._on_reset_user)
        self.window.user_selected.connect(self._on_user_selected_for_chat)
        
        if self.is_host:
            self.window.api_config_changed.connect(self._on_api_config_applied)
            self.window.api_config_reset.connect(self._on_api_config_reset)
            self.window.memory_viewer.clear_requested.connect(self._on_clear_memories)
        
        # Update memories display periodically
        self._update_memories_display()
    
    def _on_connection_status(self, connected: bool, message: str):
        """Handle connection status changes"""
        self.window.update_status(message)
        if not connected:
            self.window.add_message("System", f"⚠️ 连接断开: {message}")

    def _on_network_error(self, error_msg: str):
        """Handle network errors"""
        self.window.update_status(f"Error: {error_msg}")
        # Optional: log error to console or file
        print(f"Network Error: {error_msg}")

    def _on_remote_suggestion(self, suggestion: dict):
        """Handle suggestion sent from peer"""
        self.window.show_suggestion(suggestion)

    def _on_conversation_selected(self, conversation_id: str):
        self.current_conversation_id = conversation_id or "default"
        self._load_messages(reset=True)

    def _on_load_more_requested(self):
        self.loaded_message_limit += 50
        self._load_messages(reset=True)

    def _on_local_typing_changed(self, is_typing: bool):
        if self.network:
            self.network.send_typing(is_typing)
    
    def _on_user_discovered(self, user_info: dict):
        """Handle discovered user from LAN"""
        user_id = user_info.get("id")
        user_name = user_info.get("name")
        ip = user_info.get("ip")
        port = user_info.get("port")
        
        print(f"[DEBUG] User discovered: {user_name} ({user_id}) at {ip}:{port}")
        
        # Add/update user in database
        self.db.upsert_user(user_id, user_name, "", ip, port, is_online=True)
        
        # Update UI online user list
        self._load_online_users()
    
    def _on_user_left(self, user_id: str):
        """Handle user leaving the LAN"""
        print(f"[DEBUG] User left: {user_id}")
        
        # Mark user as offline
        self.db.set_user_online_status(user_id, False)
        
        # Update UI
        self._load_online_users()
    
    def _load_online_users(self):
        """Load online users into sidebar"""
        try:
            users = self.db.get_all_users()
            online_users = [u for u in users if u.get("is_online") and u.get("id") != self.current_user_id]
            self.window.load_online_users(online_users)
            print(f"[DEBUG] Loaded {len(online_users)} online users to UI")
        except Exception as e:
            print(f"Error loading online users: {e}")
    
    def _on_user_selected_for_chat(self, peer_user_id: str, peer_user_name: str):
        """Handle user selection to start chat"""
        print(f"[DEBUG] User selected for chat: {peer_user_name} ({peer_user_id})")
        
        # Get or create conversation with this user
        conversation = self.db.get_or_create_conversation(peer_user_id, peer_user_name)
        conv_id = conversation.get("id")
        
        print(f"[DEBUG] Conversation ID: {conv_id}")
        
        # Switch to this conversation
        self.current_conversation_id = conv_id
        self._load_messages(reset=True)
        
        # Refresh conversation list to show new conversation
        self._load_conversations_list()
        
        # Show status message
        self.window.update_status(f"开始与 {peer_user_name} 的对话")
      
      
    def _on_remote_emotion(self, emotion_scores: dict):
        """Handle emotion scores sent from peer"""
        self.window.update_emotion(emotion_scores)

    def _on_remote_memories(self, memories: list):
        """Handle memories sent from peer"""
        self.window.update_memories(memories)

    def _on_remote_ai_request(self):
        """Handle explicit AI request forwarded from guest to host"""
        if self.is_host and self.ai_service:
            self._on_ai_requested()

    def _on_typing_status(self, is_typing: bool):
        self.window.show_typing_status(is_typing)

    def _init_ai_service(self):
        """Initialize AI service with config"""
        if not self.is_host:
            return
        
        api_key = self.config_manager.get_api_key()
        if api_key:
            try:
                api_base = self.config_manager.get_api_base()
                self.ai_service = AIService(api_key=api_key, api_base=api_base)
            except Exception as e:
                self.window.show_suggestion({
                    "title": "AI服务初始化失败",
                    "content": f"无法初始化AI服务: {str(e)}\n请通过菜单栏配置API Key。"
                })
        else:
            # Show API config dialog on first run
            self._show_api_config_dialog()
    
    def _show_api_config_dialog(self):
        """Show API config dialog"""
        current_key = self.config_manager.get_api_key() or ""
        current_base = self.config_manager.get_api_base() or ""
        dialog = APIConfigDialog(current_key, current_base, self.window)
        dialog.config_applied.connect(self._on_api_config_applied)
        dialog.config_reset.connect(self._on_api_config_reset)
        dialog.exec()
    
    def _on_api_config_applied(self, api_key: str, api_base: str, persist: bool):
        if persist:
            self.config_manager.set_api_config(api_key, api_base)
        try:
            self.ai_service = AIService(api_key=api_key, api_base=api_base)
            QMessageBox.information(self.window, "配置已应用", "API配置已应用，AI功能已启用。")
        except Exception as e:
            QMessageBox.warning(self.window, "配置错误", f"无法初始化AI服务: {str(e)}")

    def _on_api_config_reset(self):
        self.config_manager.reset()
        self.ai_service = None
        QMessageBox.information(self.window, "配置已重置", "已清除所有API配置并恢复默认设置。")
    
    def _update_memories_display(self):
        """Update memories display in UI"""
        memories = self.db.get_memories()
        self.window.update_memories(memories)
    
    def _on_clear_memories(self):
        """Handle clear memories request"""
        self.db.clear_memories()
        self._update_memories_display()
        self.window.add_message("System", "📝 已清空所有记忆")
    
    def _on_reset_user(self):
        """Handle user reset request"""
        import os
        import sys
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            print("[DEBUG] Starting user reset...")
            
            # Stop network services first
            if hasattr(self, 'network') and self.network:
                print("[DEBUG] Stopping network...")
                self.network.stop()
            
            if hasattr(self, 'discovery_service') and self.discovery_service:
                print("[DEBUG] Stopping discovery service...")
                self.discovery_service.stop()
            
            # Mark user as offline in database
            try:
                self.db.set_user_online_status(self.current_user_id, False)
                print("[DEBUG] Marked user as offline")
            except Exception as e:
                print(f"[WARN] Could not mark user offline: {e}")
            
            # Close database connection
            try:
                self.db.close()
                print("[DEBUG] Database closed")
            except Exception as e:
                print(f"[WARN] Could not close database: {e}")
            
            # Delete database file
            db_file = "petchat.db"
            try:
                if os.path.exists(db_file):
                    os.remove(db_file)
                    print(f"[DEBUG] Deleted database file: {db_file}")
            except Exception as e:
                print(f"[ERROR] Could not delete database: {e}")
            
            # Clear user data from config
            try:
                self.config_manager.config.pop('user_id', None)
                self.config_manager.config.pop('user_name', None)
                self.config_manager.config.pop('user_avatar', None)
                self.config_manager._save_config()
                print("[DEBUG] Cleared user data from config")
            except Exception as e:
                print(f"[ERROR] Could not clear config: {e}")
            
            # Show success message
            QMessageBox.information(
                self.window,
                "重置成功",
                "用户数据已清除。\n应用程序将关闭，请重新启动。"
            )
            
            # Close window and quit
            print("[DEBUG] Closing application...")
            self.app.quit()
            
        except Exception as e:
            print(f"[ERROR] Failed to reset user: {e}")
            self.window.add_message("System", f"❌ 重置用户失败: {e}")
    
    def _on_message_received(self, sender: str, content: str):
        """Handle received message"""
        # Default to public chat for incoming messages
        # TODO: Extract conversation_id from network packet in future
        target_conversation = "public"
        
        # Save to database (use sender name as sender_id for now)
        self.db.add_message(sender, content, target_conversation, sender)
        
        # Update conversation last message
        self.db.update_conversation_last_message(target_conversation, content[:50])
        
        # Only display if currently viewing this conversation
        if target_conversation == self.current_conversation_id:
            self.window.add_message(sender, content, is_me=False)
        else:
            print(f"[DEBUG] Message received for conversation '{target_conversation}' but currently viewing '{self.current_conversation_id}'")
        
        # Trigger AI analysis (host only)
        if self.is_host and self.ai_service:
            self.message_count += 1
            self._trigger_ai_analysis()
    
    def _on_message_sent(self, sender: str, content: str):
        """Handle sent message"""
        # Store with current user's ID
        self.db.add_message(sender, content, self.current_conversation_id, self.current_user_id)
        
        # Update conversation last message
        self.db.update_conversation_last_message(self.current_conversation_id, content[:50])
        
        # Send via network based on conversation type
        if self.current_conversation_id == "public":
            # Public chat room: broadcast to all users
            print(f"[DEBUG] Broadcasting to public chat room")
            # Current P2P network sends to connected peer (broadcast needs implementation)
            if self.network:
                self.network.send_message(sender, content)
        else:
            # P2P private chat: send to specific user
            print(f"[DEBUG] Sending P2P message in conversation {self.current_conversation_id}")
            if self.network:
                self.network.send_message(sender, content)
        
        # Trigger AI analysis (host only)
        if self.is_host and self.ai_service:
            self.message_count += 1
            self._trigger_ai_analysis()
    
    def _trigger_ai_analysis(self):
        """Trigger AI analysis based on message count"""
        # Emotion analysis (every N messages)
        if self.message_count % Settings.EMOTION_ANALYSIS_INTERVAL == 0:
            self._analyze_emotion()
        
        # Memory extraction (every N messages)
        if self.message_count % Settings.MEMORY_EXTRACTION_INTERVAL == 0:
            self._extract_memories()
        
        # Suggestion check (every N messages)
        if self.message_count % Settings.SUGGESTION_CHECK_INTERVAL == 0:
            self._check_suggestions()
    
    def _analyze_emotion(self):
        """Analyze emotion from recent messages"""
        if not self.ai_service:
            return
        
        recent_messages = self.db.get_recent_messages(Settings.RECENT_MESSAGES_FOR_EMOTION)
        if len(recent_messages) < 2:
            return
        
        try:
            emotion_scores = self.ai_service.analyze_emotion(recent_messages)
            self.window.update_emotion(emotion_scores)
            if self.network:
                self.network.send_ai_emotion(emotion_scores)
            emotion_type = max(emotion_scores.items(), key=lambda x: x[1])[0]
            confidence = emotion_scores[emotion_type]
            self.db.add_emotion(emotion_type, confidence)
        except Exception as e:
            print(f"Error analyzing emotion: {e}")
    
    def _extract_memories(self):
        """Extract memories from conversation"""
        if not self.ai_service:
            return
        
        recent_messages = self.db.get_recent_messages(20)
        if len(recent_messages) < 3:
            return
        
        try:
            memories = self.ai_service.extract_memories(recent_messages)
            for memory in memories:
                # Check if similar memory already exists
                existing = self.db.get_memories()
                # Simple duplicate check
                if memory['content'] not in [m['content'] for m in existing]:
                    self.db.add_memory(memory['content'], memory.get('category'))
            self._update_memories_display()
            if self.network:
                self.network.send_ai_memories(self.db.get_memories())
        except Exception as e:
            print(f"Error extracting memories: {e}")
    
    def _check_suggestions(self):
        """Check if suggestion should be generated"""
        if not self.ai_service:
            return
        
        recent_messages = self.db.get_recent_messages(5)
        if len(recent_messages) < 2:
            return
        
        try:
            suggestion = self.ai_service.generate_suggestion(recent_messages)
            if suggestion:
                self.window.show_suggestion(suggestion)
                if self.network:
                    self.network.send_ai_suggestion(suggestion)
        except Exception as e:
            print(f"Error generating suggestion: {e}")
    
    def _on_ai_requested(self):
        """Handle explicit AI request (/ai command)"""
        if not self.is_host:
            if hasattr(self, "network") and self.network and self.network.running:
                self.window.update_status("已向 Host 请求 AI 分析...")
                self.network.send_ai_request()
            else:
                self.window.show_suggestion({
                    "title": "AI服务不可用",
                    "content": "尚未连接到 Host，无法请求 AI 建议。"
                })
            return

        if not self.ai_service:
            self.window.show_suggestion({
                "title": "AI服务不可用",
                "content": "AI服务未初始化。请检查API Key配置。"
            })
            return
        
        recent_messages = self.db.get_recent_messages(10)
        if len(recent_messages) < 2:
            self.window.show_suggestion({
                "title": "信息不足",
                "content": "需要更多对话内容才能生成建议。"
            })
            return
        
        try:
            # Generate comprehensive suggestion
            suggestion = self.ai_service.generate_suggestion(recent_messages)
            if suggestion:
                self.window.show_suggestion(suggestion)
            else:
                # Try to extract memories as suggestion
                memories = self.ai_service.extract_memories(recent_messages)
                if memories:
                    memory_text = "\n".join([f"- {m['content']}" for m in memories[:3]])
                    self.window.show_suggestion({
                        "title": "对话要点",
                        "content": memory_text
                    })
                else:
                    self.window.show_suggestion({
                        "title": "暂无建议",
                        "content": "当前对话暂无可提取的建议。"
                    })
        except Exception as e:
            self.window.show_suggestion({
                "title": "AI处理错误",
                "content": f"处理请求时出错: {str(e)}"
            })
    
    def start(self):
        """Start the application"""
        if not self.from_cli_args:
            dialog = RoleSelectionDialog(self.window)
            result = dialog.exec()
            if result != QDialog.DialogCode.Accepted:
                return
            if dialog.selected_role == "host":
                self.is_host = True
                self.host_ip = Settings.DEFAULT_HOST_IP
            else:
                self.is_host = False
                self.host_ip = dialog.host_ip or Settings.DEFAULT_GUEST_IP
            try:
                self.port = int(dialog.port_text)
            except ValueError:
                self.port = Settings.DEFAULT_PORT
            self.use_relay = getattr(dialog, "use_relay", False)
            relay_host_text = getattr(dialog, "relay_host", "").strip()
            if self.use_relay:
                if relay_host_text:
                    self.relay_host = relay_host_text
                else:
                    self.relay_host = Settings.DEFAULT_RELAY_HOST
            else:
                self.relay_host = self.host_ip
            try:
                relay_port_text = getattr(dialog, "relay_port_text", "") or str(Settings.DEFAULT_RELAY_PORT)
                self.relay_port = int(relay_port_text)
            except ValueError:
                self.relay_port = Settings.DEFAULT_RELAY_PORT
            self.room_id = getattr(dialog, "room_id", "default") or "default"
            self.window.update_role(self.is_host)

        self.network = NetworkManager(
            is_host=self.is_host,
            host_ip=self.host_ip,
            port=self.port,
            use_relay=self.use_relay,
            relay_host=self.relay_host,
            relay_port=self.relay_port,
            room_id=self.room_id,
        )
        self._setup_connections()
        
        # Initialize UDP Discovery for LAN mode (not for relay)
        if not self.use_relay:
            from core.network import UDPDiscovery
            self.discovery_service = UDPDiscovery(
                user_id=self.current_user_id,
                user_name=self.current_user_name,
                tcp_port=self.port
            )
            # Connect discovery signals
            self.discovery_service.user_discovered.connect(self._on_user_discovered)
            self.discovery_service.user_left.connect(self._on_user_left)
            # Start discovery
            self.discovery_service.start()
            print("[DEBUG] UDP Discovery service started")
            # Load initial online users to UI
            self._load_online_users()
        if self.is_host:
            self._init_ai_service()

        if self.is_host:
            if self.use_relay:
                self.window.update_status(f"Host模式 - 使用中转服务器 {self.relay_host}:{self.relay_port} 房间 {self.room_id}")
                self.network.start_host()
            else:
                self.network.start_host()
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                    self.window.update_status(f"Host模式 - 本地IP: {local_ip}, 端口: {self.port}")
                except:
                    self.window.update_status(f"Host模式 - 端口: {self.port}")
        else:
            if self.use_relay:
                self.window.update_status(f"Guest模式 - 使用中转服务器 {self.relay_host}:{self.relay_port} 房间 {self.room_id}")
                self.network.connect_as_guest()
            else:
                self.window.update_status("正在连接 Host...")
                self.network.connect_as_guest()
        
        # Show window
        print("[DEBUG] Showing window...")
        self.window.show()
        print("[DEBUG] Window shown")
        
        # Run application
        print("[DEBUG] Starting event loop...")
        result = self.app.exec()
        print(f"[DEBUG] Event loop exited with code: {result}")
        sys.exit(result)


def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def main():
    """Main entry point"""
    print("Starting pet-chat application...")
    parser = argparse.ArgumentParser(description="pet-chat - AI-powered chat application")
    parser.add_argument("--host", action="store_true", help="Run as host (server)")
    parser.add_argument("--guest", action="store_true", help="Run as guest (client)")
    parser.add_argument("--host-ip", type=str, default=Settings.DEFAULT_GUEST_IP, 
                       help=f"Host IP address (default: {Settings.DEFAULT_GUEST_IP})")
    parser.add_argument("--port", type=int, default=Settings.DEFAULT_PORT,
                       help=f"Port number (default: {Settings.DEFAULT_PORT})")
    
    args = parser.parse_args()
    print(f"Parsed args: host={args.host}, guest={args.guest}, host_ip={args.host_ip}, port={args.port}")
    
    # Determine role
    is_host = args.host
    # If no role specified in CLI, we'll ask in GUI (unless pure CLI mode is desired, but here we have GUI)
    # The App controller handles the dialog if from_cli_args is False
    from_cli_args = args.host or args.guest
    print(f"Role: {'host' if is_host else 'guest'}, from_cli_args={from_cli_args}")
    
    print("Creating PetChatApp instance...")
    app = PetChatApp(is_host=is_host, host_ip=args.host_ip, port=args.port, from_cli_args=from_cli_args)
    print("PetChatApp instance created, starting application...")
    app.start()
    print("Application started")


if __name__ == "__main__":
    main()
