import subprocess
import time
import sys
import os

def launch_instances(num_guests=1):
    """Launch one host and multiple guests"""
    # Get python executable
    python_exe = sys.executable
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
    
    processes = []
    
    # Launch Host
    print("Launching Host...")
    host_proc = subprocess.Popen([python_exe, script_path, "--host", "--port", "8888"])
    processes.append(host_proc)
    
    # Wait for host to start
    time.sleep(2)
    
    # Launch Guests
    for i in range(num_guests):
        print(f"Launching Guest {i+1}...")
        guest_proc = subprocess.Popen([python_exe, script_path, "--guest", "--host-ip", "127.0.0.1", "--port", "8888"])
        processes.append(guest_proc)
        time.sleep(1)
        
    print(f"Launched 1 Host and {num_guests} Guests.")
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
    launch_instances(num_guests=2)
