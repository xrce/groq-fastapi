#!/usr/bin/env python3
import os
import sys
import subprocess
import requests

def main():
    print("• Setup")
    print("="*50)
    
    # Install requirements
    print("• Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ Dependencies installed")
    except:
        print("✗ Failed to install dependencies")
        sys.exit(1)
    
    # Get API key
    print("\n• Setup API Key")
    print("Get your key from: https://console.groq.com/")
    while True:
        api_key = input("Enter Groq API Key: ").strip()
        if api_key:
            break
        print("✗ API key required!")
    
    # Test API key and get models
    print("• Testing API key...")
    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        models_data = response.json()
        print("✓ API key valid!")
    except:
        print("✗ Invalid API key")
        sys.exit(1)
    
    # Filter and show models
    print("\n• Available Models:")
    text_models = [m for m in models_data.get("data", []) 
                   if not any(x in m.get("id", "").lower() 
                             for x in ["whisper", "tts", "guard"])]
    
    for i, model in enumerate(text_models[:10], 1):  # Show top 10
        print(f"{i:2d}. {model['id']} ({model.get('owned_by', 'Unknown')})")
    
    # Get model choice
    while True:
        try:
            choice = input(f"\nChoose model (1-{min(10, len(text_models))}) [1]: ").strip() or "1"
            model_id = text_models[int(choice)-1]["id"]
            print(f"✓ Selected: {model_id}")
            break
        except:
            print("✗ Invalid choice")
    
    # Create .env file
    env_content = f"""GROQ_API_KEY={api_key}
GROQ_MODEL={model_id}
MAX_TOKENS=1024
TEMPERATURE=0.7
"""
    with open(".env", "w") as f:
        f.write(env_content)
    print("✓ .env file created")
    
    # Show next steps
    print("\n✓ Setup Complete!")
    print("• Next Steps:")
    print("1. python main.py")
    print("2. locust -f load_test.py --host=http://localhost:8000 --users=200 --spawn-rate=20 --headless")

if __name__ == "__main__":
    main()