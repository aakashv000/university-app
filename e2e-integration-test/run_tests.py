#!/usr/bin/env python
import os
import subprocess
import argparse
import time

def run_tests(wait_for_backend=True):
    """Run the E2E integration tests."""
    print("Running E2E integration tests...")
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    if wait_for_backend:
        print("Waiting for backend to be ready...")
        max_retries = 30
        retry_interval = 2
        
        for i in range(max_retries):
            try:
                import requests
                from dotenv import load_dotenv
                
                load_dotenv()
                api_url = os.getenv("API_BASE_URL", "http://localhost:8000/api")
                
                response = requests.get(f"{api_url}/health")
                if response.status_code == 200:
                    print("Backend is ready!")
                    break
            except Exception:
                pass
            
            print(f"Waiting for backend... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
        else:
            print("Backend is not ready after maximum retries. Running tests anyway...")
    
    # Run pytest
    cmd = ["pytest", "-v", "--html=reports/report.html"]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("All tests passed!")
    else:
        print(f"Tests failed with exit code {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run E2E integration tests")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for backend to be ready")
    args = parser.parse_args()
    
    exit_code = run_tests(wait_for_backend=not args.no_wait)
    exit(exit_code)
