from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend funcionando", "status": "OK", "port": 8000}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "sales-backend"}

@app.get("/test")
def test_endpoint():
    return {"test": "success", "data": [1, 2, 3, 4, 5]}

if __name__ == "__main__":
    import uvicorn
    print("=== INICIANDO SERVIDOR DE PRUEBA ===")
    print("URL: http://127.0.0.1:8000")
    print("Health: http://127.0.0.1:8000/health")
    print("Test: http://127.0.0.1:8000/test")
    print("=====================================")
    uvicorn.run(app, host="127.0.0.1", port=8000)