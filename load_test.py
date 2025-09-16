import random
import time
import sys
import os
import signal
from datetime import datetime, timedelta

import logging

# Suppress logging
logging.getLogger().setLevel(logging.CRITICAL)
for name in ['locust', 'urllib3', 'requests']:
    logging.getLogger(name).setLevel(logging.CRITICAL)

from locust import HttpUser, task, between, events

class AIServiceUser(HttpUser):
    wait_time = between(1, 3)
    
    total_requests = 0
    successful_requests = 0
    failed_requests = 0
    response_times = []
    test_start_time = None
    
    questions = [
        # Short Questions
        "Hello, how are you?", "What is AI?", "Tell me a joke.", "What is 2+2?", 
        "Define machine learning.", "What is Python?", "How does internet work?", 
        "What is climate change?", "Explain blockchain.", "What is quantum computing?",
        # Medium Questions
        "Explain the difference between artificial intelligence and machine learning.",
        "How does natural language processing work in modern AI systems?",
        "What are the main challenges in developing autonomous vehicles?",
        "Describe the process of training a neural network from scratch.",
        "How do recommendation systems work on platforms like Netflix and Amazon?",
        "What are the ethical implications of using AI in healthcare diagnostics?",
        "Explain the concept of transfer learning in deep learning models.",
        "How does computer vision technology enable facial recognition systems?",
        "What are the advantages and disadvantages of cloud computing for businesses?",
        "Describe the role of data preprocessing in machine learning workflows.",
        # Long Questions
        "Provide a comprehensive analysis of how transformer architectures revolutionized natural language processing, including their attention mechanism, scalability benefits, and impact on models like GPT and BERT.",
        "Explain in detail the technical challenges and solutions involved in building a distributed microservices architecture for a high-traffic e-commerce platform, including database sharding, load balancing, and fault tolerance.",
        "Discuss the complete software development lifecycle for a machine learning project, from data collection and cleaning through model deployment and monitoring, including best practices for MLOps.",
        "Analyze the environmental impact of large-scale data centers and cryptocurrency mining, and propose sustainable solutions that balance technological advancement with environmental responsibility.",
        "Describe the technical implementation details of implementing a real-time recommendation engine that can handle millions of users simultaneously while maintaining sub-second response times and personalized accuracy.",
        "Explain the security challenges and solutions in implementing a zero-trust network architecture for a multinational corporation with hybrid cloud infrastructure and remote workforce.",
        "Provide a detailed technical comparison between different containerization technologies (Docker, Kubernetes, etc.) and their optimal use cases in various enterprise scenarios.",
        "Analyze the technical and business implications of transitioning from a monolithic application architecture to a serverless, event-driven architecture using cloud-native technologies.",
        "Discuss the implementation challenges of building a scalable, real-time chat application that supports millions of concurrent users, including WebSocket management, message routing, and data consistency.",
        "Explain the complete process of designing and implementing a computer vision system for autonomous drone navigation, including sensor fusion, path planning, obstacle avoidance, and real-time decision making."
    ]
    
    @classmethod
    def track_request(cls, status_code, response_time_ms):
        if cls.test_start_time is None:
            cls.test_start_time = datetime.now()
            
        cls.total_requests += 1
        cls.response_times.append(response_time_ms)
        
        if status_code == 200:
            cls.successful_requests += 1
        else:
            cls.failed_requests += 1
    
    @classmethod  
    def show_final_results(cls):
        print("=" * 50)
        print("AI SERVICE TEST RESULTS")
        print("=" * 50)
        
        if cls.total_requests == 0:
            print("✗ No requests completed")
            return
            
        success_rate = (cls.successful_requests / cls.total_requests) * 100
        
        if cls.response_times:
            avg_response_time = sum(cls.response_times) / len(cls.response_times)
        else:
            avg_response_time = 0
            
        if cls.test_start_time:
            test_duration = (datetime.now() - cls.test_start_time).total_seconds()
        else:
            test_duration = 0
            
        print(f"Total Requests: {cls.total_requests}")
        print(f"Successful: {cls.successful_requests} ({success_rate:.1f}%)")
        print(f"Failed: {cls.failed_requests}")
        print(f"Avg Response Time: {avg_response_time:.0f}ms")
        print(f"Test Duration: {test_duration:.1f}s")
        
        if success_rate >= 95:
            print(f"✓ Service Status: EXCELLENT")
        elif success_rate >= 85:
            print(f"✓ Service Status: GOOD")
        elif success_rate >= 70:
            print(f"Service Status: ACCEPTABLE")
        else:
            print(f"✗ Service Status: POOR")
            
        print("=" * 50)
    
    def on_start(self):
        self.client.verify = False
        
    @task(8)
    def test_chat_endpoint(self):
        question = random.choice(self.questions)
        payload = {
            "message": question,
            "temperature": random.uniform(0.1, 1.0),
            "max_tokens": random.randint(100, 512)
        }
        
        with self.client.post("/chat", json=payload, catch_response=True) as response:
            response_time_ms = response.elapsed.total_seconds() * 1000
            
            print(f"> POST /chat - Question: {question[:50]}{'...' if len(question) > 50 else ''}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "response" in data and data["response"]:
                        print(f"> Content: {data['response'][:100]}{'...' if len(data['response']) > 100 else ''}")
                        response.success()
                    else:
                        response.failure("Empty response received")
                except:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
                
            self.track_request(response.status_code, response_time_ms)
    
    @task(2)
    def test_health_endpoint(self):
        with self.client.get("/health", catch_response=True) as response:
            response_time_ms = response.elapsed.total_seconds() * 1000
            
            print(f"> GET /health - Status check")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"> Content: {data.get('status', 'unknown')} status")
                    response.success()
                except:
                    response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
                
            self.track_request(response.status_code, response_time_ms)
    
    @task(1)
    def test_models_endpoint(self):
        with self.client.get("/models", catch_response=True) as response:
            response_time_ms = response.elapsed.total_seconds() * 1000
            
            print(f"> GET /models - Fetching available models")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "data" in data and "current_model" in data:
                        total_models = data.get("total_models", 0)
                        current_model = data.get("current_model", "unknown")
                        print(f"> Content: {total_models} models available, current: {current_model}")
                        response.success()
                    else:
                        response.failure("Invalid models response structure")
                except:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
                
            self.track_request(response.status_code, response_time_ms)

def signal_handler(signum, frame):
    print(f"\n✗ Test interrupted by user")
    AIServiceUser.show_final_results()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@events.test_stop.add_listener  
def on_test_stop(environment, **kwargs):
    AIServiceUser.show_final_results()

if __name__ == "__main__":
    print("SERVICE LOAD TEST")
    print("=" * 50)
    print(f"Test Questions: {len(AIServiceUser.questions)}")
    print("=" * 50)
    print("USAGE:")
    print("locust -f load_test.py --host=http://localhost:8000 --users=200 --spawn-rate=20 --headless")
    print("")
    print("With duration:")
    print("locust -f load_test.py --host=http://localhost:8000 --users=200 --spawn-rate=20 --headless --run-time=60s")
    print("=" * 50)