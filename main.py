import os
import time
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Configure verbose logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Generative AI Service", version="1.0.0")

# Initialize Groq client
groq_client = None

def get_groq_client():
    global groq_client
    if groq_client is None:
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
        groq_client = Groq(api_key=GROQ_API_KEY)
    return groq_client

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    max_tokens: int = None
    temperature: float = None

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    response_time: float
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    client_ip = request.client.host
    logger.info(f"• HEALTH CHECK - Client: {client_ip}")
    
    response = HealthResponse(status="healthy", timestamp=datetime.now())
    logger.info(f"✓ Health response: {response.status}")
    return response

@app.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest, req: Request):
    start_time = time.time()
    client_ip = req.client.host
    
    # Log incoming request
    logger.info(f"• CHAT REQUEST - Client: {client_ip}")
    logger.info(f"• Message: {request.message[:100]}{'...' if len(request.message) > 100 else ''}")
    logger.info(f"• Config - Model: {GROQ_MODEL}, Tokens: {request.max_tokens or MAX_TOKENS}, Temp: {request.temperature or TEMPERATURE}")
    
    try:
        client = get_groq_client()
        
        max_tokens = request.max_tokens or MAX_TOKENS
        temperature = request.temperature or TEMPERATURE
        
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": request.message}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False
        )
        
        response_time = time.time() - start_time
        ai_response = completion.choices[0].message.content
        
        # Log response details
        logger.info(f"✓ Response time: {response_time:.3f}s")
        logger.info(f"✓ Tokens used: {completion.usage.total_tokens}")
        logger.info(f"✓ AI response: {ai_response[:200]}{'...' if len(ai_response) > 200 else ''}")
        
        return ChatResponse(
            response=ai_response,
            model=GROQ_MODEL,
            tokens_used=completion.usage.total_tokens,
            response_time=response_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"✗ CHAT ERROR - Client: {client_ip}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI response failed: {str(e)}")

@app.get("/models")
async def get_available_models(request: Request):
    """Get list of available models from Groq API"""
    client_ip = request.client.host
    start_time = time.time()
    
    logger.info(f"• MODELS REQUEST - Client: {client_ip}")
    
    try:
        url = "https://api.groq.com/openai/v1/models"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        models_data = response.json()
        
        # Extract model information
        available_models = []
        for model in models_data.get("data", []):
            model_info = {
                "id": model.get("id"),
                "owned_by": model.get("owned_by"),
                "active": model.get("active"),
                "context_window": model.get("context_window"),
                "max_completion_tokens": model.get("max_completion_tokens")
            }
            available_models.append(model_info)
        
        response_time = time.time() - start_time
        result = {
            "object": models_data.get("object"),
            "data": available_models,
            "current_model": GROQ_MODEL,
            "total_models": len(available_models)
        }
        
        logger.info(f"✓ Models response time: {response_time:.3f}s")
        logger.info(f"✓ Models found: {len(available_models)} models")
        logger.info(f"• Current model: {GROQ_MODEL}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ MODELS API ERROR - Client: {client_ip}, Error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Unable to fetch models from Groq API: {str(e)}")
    except Exception as e:
        logger.error(f"✗ MODELS ERROR - Client: {client_ip}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve models: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)