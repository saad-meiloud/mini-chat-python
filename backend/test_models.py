"""
Script to test and list available Gemini models
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
    exit(1)

print(f"🔑 API Key found: {api_key[:10]}...\n")

try:
    genai.configure(api_key=api_key)
    
    print("📋 Listing all available models:\n")
    all_models = list(genai.list_models())
    
    working_models = []
    
    for model in all_models:
        model_name = model.name
        if '/' in model_name:
            short_name = model_name.split('/')[-1]
        else:
            short_name = model_name
        
        supports_generate = False
        if hasattr(model, 'supported_generation_methods'):
            supports_generate = 'generateContent' in model.supported_generation_methods
        
        print(f"Model: {short_name}")
        print(f"  Full name: {model_name}")
        print(f"  Supports generateContent: {supports_generate}")
        
        if supports_generate:
            # Test if it actually works
            try:
                test_model = genai.GenerativeModel(short_name)
                test_response = test_model.generate_content("Say hello")
                if test_response and hasattr(test_response, 'text'):
                    print(f"  ✅ WORKS! Response: {test_response.text[:50]}...")
                    working_models.append(short_name)
                else:
                    print(f"  ⚠️ Model loaded but response format unexpected")
            except Exception as e:
                print(f"  ❌ Test failed: {str(e)[:100]}")
        
        print()
    
    print(f"\n✅ Working models: {working_models}")
    
    if working_models:
        print(f"\n🎯 Recommended model: {working_models[0]}")
    else:
        print("\n❌ No working models found!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
