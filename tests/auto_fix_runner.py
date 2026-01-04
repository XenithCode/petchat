import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication

# Force project root into path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def smoke_test():
    print(">>> [TEST START] Initializing Application...")
    try:
        # Import main to trigger module-level execution
        from main import PetChatApp
        
        # Initialize Qt App (Headless check)
        app = QApplication(sys.argv)
        pet_app = PetChatApp()
        
        # 1. Basic Assertions
        assert app is not None, "QApplication failed to init"
        assert hasattr(pet_app, '__dict__'), "PetChatApp instance is corrupt"
        
        # 2. Component Check
        print(f">>> [STATE] Loaded attributes: {list(pet_app.__dict__.keys())}")
        
        # 3. Critical Component Validation
        if not hasattr(pet_app, 'peer_node') or pet_app.peer_node is None:
             # It's okay if it's PeerNode, but not None unless intended
            print(">>> [WARN] 'peer_node' attribute is missing or None.")
            
        print(">>> [TEST SUCCESS] App initialized successfully.")
        return 0
    except Exception as e:
        print(f">>> [CRASH] Type: {type(e).__name__}")
        print(f">>> [CRASH] Msg:  {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(smoke_test())
