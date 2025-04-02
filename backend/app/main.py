from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

# Create FastAPI app instance  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
app = FastAPI(title="LLM-Powered API")

# CORS configuration
origins = [
    "https://multiagentapp.netlify.app",  
    "https://multiagentapp.onrender.com",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include API routes
app.include_router(router)

@app.get("/")
def home():
    return {"message": "LLM API is running!"}
