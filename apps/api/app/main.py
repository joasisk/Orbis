from fastapi import FastAPI

app = FastAPI(title="ADHD OS API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/health")
def v1_health():
    return {"status": "ok", "version": "v1"}
