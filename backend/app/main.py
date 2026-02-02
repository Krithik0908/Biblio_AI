from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
app = FastAPI() 
app.add_middleware(CORSMiddleware, allow_origins=["*"]) 
@app.get("/") 
def root(): 
    return {"message": "BiblioAI Running"} 
@app.get("/health") 
def health(): 
    return {"status": "healthy", "database": True, "ai_models": {"recommender": True}} 
