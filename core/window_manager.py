"""
Window Manager for handling multi-window application state and thread pool.
Implements Singleton pattern to provide global access to shared resources.
"""
from PyQt6.QtCore import QObject, QThreadPool, QRunnable, pyqtSignal
from PyQt6.QtWidgets import QMainWindow
from typing import Dict, Optional
import uuid

class WindowManager(QObject):
    _instance = None
    
    # Signals
    window_registered = pyqtSignal(str)
    window_closed = pyqtSignal(str)
    # Event for data synchronization between windows
    data_sync_event = pyqtSignal(str, object)  # event_type, data
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WindowManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._windows: Dict[str, QMainWindow] = {}
        self._thread_pool = QThreadPool.globalInstance()
        # Optimize thread pool for IO-bound tasks typical in chat apps
        self._thread_pool.setMaxThreadCount(8) 
        self._initialized = True
        
    def register_window(self, window: QMainWindow) -> str:
        """Register a new window instance and return its ID"""
        window_id = str(uuid.uuid4())
        self._windows[window_id] = window
        self.window_registered.emit(window_id)
        return window_id
        
    def unregister_window(self, window_id: str):
        """Unregister a window instance"""
        if window_id in self._windows:
            del self._windows[window_id]
            self.window_closed.emit(window_id)
            
    def get_window(self, window_id: str) -> Optional[QMainWindow]:
        """Get window by ID"""
        return self._windows.get(window_id)
        
    def get_all_windows(self) -> list[QMainWindow]:
        """Get all registered windows"""
        return list(self._windows.values())
        
    def submit_task(self, runnable: QRunnable):
        """Submit a task to the global thread pool"""
        self._thread_pool.start(runnable)
        
    def broadcast(self, event_type: str, data: object):
        """Broadcast an event to all registered windows (Data Sync)"""
        self.data_sync_event.emit(event_type, data)
        
    @property
    def thread_pool(self):
        return self._thread_pool

# Global instance
window_manager = WindowManager()
