#!/usr/bin/env python
import os
import subprocess
import argparse
import time
import webbrowser
import signal
import sys

def run_app(backend_only=False, frontend_only=False):
    """Run the university application locally."""
    processes = []
    
    try:
        if not frontend_only:
            print("Starting backend server...")
            backend_env = os.environ.copy()
            backend_env["POSTGRES_SERVER"] = "localhost"
            backend_cmd = ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
            backend_process = subprocess.Popen(
                backend_cmd,
                cwd="backend",
                env=backend_env
            )
            processes.append(backend_process)
            print("Backend server started at http://localhost:8000")
            
            # Wait a bit for the backend to start
            time.sleep(2)
        
        if not backend_only:
            print("Starting frontend development server...")
            frontend_env = os.environ.copy()
            frontend_env["REACT_APP_API_URL"] = "http://localhost:8000/api"
            frontend_cmd = ["npm", "start"]
            frontend_process = subprocess.Popen(
                frontend_cmd,
                cwd="frontend",
                env=frontend_env
            )
            processes.append(frontend_process)
            print("Frontend server started at http://localhost:3000")
            
            # Open browser after a short delay
            time.sleep(3)
            webbrowser.open("http://localhost:3000")
        
        print("\nPress Ctrl+C to stop the servers...\n")
        
        # Keep the script running until interrupted
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\nStopping servers...")
        for process in processes:
            process.terminate()
        
        # Give processes time to terminate gracefully
        time.sleep(2)
        
        # Force kill any remaining processes
        for process in processes:
            if process.poll() is None:
                process.kill()
        
        print("Servers stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the University App locally")
    parser.add_argument("--backend-only", action="store_true", help="Run only the backend server")
    parser.add_argument("--frontend-only", action="store_true", help="Run only the frontend server")
    args = parser.parse_args()
    
    run_app(backend_only=args.backend_only, frontend_only=args.frontend_only)
