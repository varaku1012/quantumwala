from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="user-authentication-ml")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "user-authentication-ml", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
