import subprocess
import time
import sys
import os

def launch_instances(num_clients=2):
    """Launch Server and multiple Clients"""
    # Get python executable
    python_exe = sys.executable
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    server_script = os.path.join(root_dir, "server.py")
    client_script = os.path.join(root_dir, "main.py")
    
    processes = []
    
    # Launch Server
    print("Launching Server...")
    # Run server in a new console window if possible, or just background
    # On Windows, creationflags=subprocess.CREATE_NEW_CONSOLE can open new window
    server_proc = subprocess.Popen([python_exe, server_script])
    processes.append(server_proc)
    
    # Wait for server to start
    time.sleep(2)
    
    # Launch Clients
    for i in range(num_clients):
        print(f"Launching Client {i+1}...")
        client_proc = subprocess.Popen([python_exe, client_script, "--server-ip", "127.0.0.1"])
        processes.append(client_proc)
        time.sleep(1)
        
    print(f"Launched Server and {num_clients} Clients.")
    print("Press Ctrl+C to stop all instances.")
    
    try:
        while True:
            time.sleep(1)
            # Check if any process died
            for p in processes:
                if p.poll() is not None:
                    print(f"Process {p.pid} terminated unexpectedly.")
                    return
    except KeyboardInterrupt:
        print("\nStopping all instances...")
        for p in processes:
            p.terminate()
            
if __name__ == "__main__":
    launch_instances(num_clients=2)
