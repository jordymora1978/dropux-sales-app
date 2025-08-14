from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="DROPUX API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "DROPUX API v2.0", 
        "status": "funcionando",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "DROPUX API"}

@app.get("/test")
def test_endpoint():
    return {"message": "Test successful", "environment": "production"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Iniciando DROPUX API en http://{host}:{port}")
    print(f"Documentacion en http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)