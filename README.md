# AI Service Load Test

Real-time AI response service using Groq API, FastAPI, and Python with load testing using Locust.

## Quick Start

### 1. Setup
```bash
python setup.py
```

### 2. Start Server
```bash
python main.py
```
Server runs at: `http://localhost:8000`

### 3. Run Load Test
```bash
locust -f load_test.py --host=http://localhost:8000 --users=200 --spawn-rate=20 --headless
```

With time limit:
```bash
locust -f load_test.py --host=http://localhost:8000 --users=200 --spawn-rate=20 --headless --run-time=60s
```

## API Endpoints

**Health Check:**
```http
GET /health
```

**Chat Completion:**
```http
POST /chat
Content-Type: application/json

{
  "message": "What is AI?",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Get Models:**
```http
GET /models
```

## Load Testing

### Configuration
- Questions: 30 (simple, medium, complex)
- Users: 200 concurrent users
- Spawn Rate: 20 users per second
- Endpoints: /chat , /health , /models

### Sample Output
```
==================================================
AI SERVICE TEST RESULTS
==================================================
Total Requests: 156
Successful: 148 (94.9%)
Failed: 8
Avg Response Time: 1247ms
Test Duration: 45.2s
Service Status: GOOD
==================================================
```

## Project Structure
```
.
├── main.py           # FastAPI application
├── load_test.py      # Locust load testing
├── setup.py          # Interactive setup
├── requirements.txt  # Dependencies
└── README.md         # Documentation
```

## Requirements
- Python 3.8+
- Groq API key

## Dependencies
```
fastapi==0.115.6
uvicorn[standard]==0.32.1
groq==0.13.0
pydantic==2.10.5
python-dotenv==1.0.1
locust==2.32.4
requests==2.32.3
```

## Environment Variables
```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
MAX_TOKENS=1024
TEMPERATURE=0.7
```
