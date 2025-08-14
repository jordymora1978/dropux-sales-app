#!/usr/bin/env python3

import uvicorn
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_simple import app

if __name__ == "__main__":
    print("="*50)
    print("SALES BACKEND API SERVER")
    print("="*50)
    print("Starting server on: http://127.0.0.1:8002")
    print("API Documentation: http://127.0.0.1:8002/docs")
    print("Health Check: http://127.0.0.1:8002/health")
    print("="*50)
    print("Press Ctrl+C to stop the server")
    print("="*50)
    
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8002,
            reload=False,  # Disable reload for stability
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nServer error: {e}")
        sys.exit(1)