from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional
import os
from dotenv import load_dotenv

from api import victims, police, ai_engine, blockchain
from core.database import init_db, get_db
from core.config import settings
from ml.prediction import AIModelManager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    AIModelManager.initialize()
    print("AI Cyber Safety Platform started")
    yield
    # Shutdown
    print("Shutting down")

app = FastAPI(
    title="AI Cyber Safety Platform",
    description="Holistic platform merging cyber safety, governance, law & order with AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(victims.router, prefix="/api/v1/victims", tags=["victims"])
app.include_router(police.router, prefix="/api/v1/police", tags=["police"])
app.include_router(ai_engine.router, prefix="/api/v1/ai", tags=["ai-engine"])
app.include_router(blockchain.router, prefix="/api/v1/blockchain", tags=["blockchain"])

@app.get("/")
async def root():
    return {
        "message": "AI Cyber Safety Platform API",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
