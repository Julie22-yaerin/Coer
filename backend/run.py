import uvicorn
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def main():
    print(f"Starting Coer Engine on {settings.BACKEND_HOST}:{settings.BACKEND_PORT} (debug={settings.DEBUG})")
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )

if __name__ == "__main__":
    main()
