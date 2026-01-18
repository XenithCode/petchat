---
name: PetChat Development Standards
description: Comprehensive guidelines for maintaining consistency in the PetChat project, covering architecture, protocol, UI theming, and coding/logging habits.
---

# PetChat Development Standards

## 1. Architectural Overview

The project follows a **Client-Server Architecture** using Python `socket` for networking and `PyQt6` for the GUI.

### 1.1 Core Components
*   **Server (`server.py`)**:
    *   Manages TCP connections using `ServerThread`.
    *   Routes messages (Private P2P or Public Broadcast).
    *   Centralizes AI processing (Emotion, Suggestion, Memories) via `AIService` + `QThreadPool`.
    *   Maintains user sessions and state.
*   **Client (`main.py`)**:
    *   `PetChatApp`: Main controller, initializes `QApplication`, `Database`, `NetworkManager`.
    *   `MainWindow`: Primary UI, handles signals/slots from core components.
    *   **Architecture Change**: AI logic has been moved from Client to Server.
*   **Data Layer (`core/database.py`)**:
    *   SQLite database (`petchat.db`).
    *   Stores `users`, `conversations`, `messages`, `memories` (key-value + vector-like usage for context).

### 1.2 Network Protocol (`core/protocol.py`)
*   **Format**: JSON payload preceded by a fixed-size header.
*   **Header**: 8 bytes (`>II`: 4-byte Length, 4-byte CRC32).
*   **Message Types**: Defined in `MessageType` Enum (e.g., `chat_message`, `ai_analysis_request`, `user_joined`).
*   **AI Handling**: Client sends `AIAnalysisRequest` (with context snapshot); Server responds asynchronously with `AISuggestion`, `AIEmotion`, or `AIMemory`.

---

## 2. Coding Style & Habits

### 2.1 General Python Patterns
*   **Type Hinting**: Use standard `typing` (e.g., `List`, `Dict`, `Optional`) in function signatures.
*   **Imports**: Group standard libs, then third-party (`PyQt6`), then local modules (`core.`, `ui.`).
*   **Error Handling**:
    *   Wrap volatile blocks (Network/DB) in `try...except`.
    *   **Prefer printing to console** over complex logging setups for now: `print(f"[DEBUG] ...")` or `print(f"[ERROR] ...")`.
*   **Comments**:
    *   Write docstrings for classes and complex methods.
    *   **Avoid inline comments** unless explaining "why" (not "what").
    *   Keep code self-documenting via variable names.

### 2.2 PyQt6 Patterns
*   **Signals & Slots**:
    *   Define custom signals in `QObject` subclasses (e.g., `NetworkManager`).
    *   Connect signals in `__init__` or dedicated `_setup_connections` methods.
*   **Threading**:
    *   Network I/O must happen in background threads (`threading.Thread` or `QThread`).
    *   **ALWAYS** emit signals to update UI from background threads. Never access UI widgets directly from non-main threads.
*   **Cleanups**: Connect `app.aboutToQuit` or `closeEvent` to cleanup methods (stopping threads, closing sockets/DB).

---

## 3. UI & Theming Standards (`ui/theme.py`)

### 3.1 Design System
*   **Theme Engine**: Use `ui.theme.Theme` class for all colors/metrics. Support Light/Dark modes via `ThemeManager`.
*   **Material Design 3**: Follow M3 principles (Surface levels, primary/secondary/tertiary colors).
*   **Color Palette**:
    *   Use predefined constants: `Theme.PRIMARY`, `Theme.BG_MAIN`, `Theme.TEXT_SECONDARY`, etc.
    *   Avoid hardcoded hex values in `ui/` files.

### 3.2 Styling (QSS)
*   **Global Stylesheet**: `Theme.get_stylesheet()` constructs the master QSS string.
*   **Scoped Styling**: Use object names (e.g., `setObjectName("sidebar")`) to target specific areas in QSS.
*   **Custom Widgets**:
    *   **`PetWidget`**: Floating overlay, translucent background, drag-supported.
    *   **`SuggestionPanel`**: standard cards, shadow effects.
    *   **Chat Bubbles**: Use `msg_type` property selectors (e.g., `QLabel[msg_type="me"]`) for styling different message types.

---

## 4. AI Service Integration

*   **Location**: Server-side only (`core/ai_service.py`).
*   **Implementation**:
    *   Use `requests` library for synchronous HTTP calls to LLM endpoints (LM Studio/Ollama/OpenAI compatible).
    *   **Prompting**: Embed prompts directly in methods (`analyze_emotion`, `extract_memories`).
    *   **JSON Enforcement**: Instruct LLM to return strictly JSON; use helper `_extract_json` to parse resiliently.
*   **Context**: Client provides a "snapshot" of recent messages to help the server (cold-start recovery).

## 5. File Organization

```
g:/project/petchat/
├── core/               # logic & data
│   ├── database.py     # SQLite wrapper
│   ├── network.py      # Client networking
│   ├── protocol.py     # Shared message defs
│   ├── models.py       # Dataclasses
│   └── ai_service.py   # LLM interaction (Server-only)
├── ui/                 # Presentation
│   ├── main_window.py  # Main Client UI
│   ├── server_window.py# Server Dashboard
│   ├── theme.py        # Central styling
│   └── *.py            # Custom widgets
├── config/             # Configuration handling
├── server.py           # Server entry point
├── main.py             # Client entry point
└── SKILL.md            # This file
```
