import os
import warnings
# Note: google.generativeai is deprecated but still works
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import google.generativeai as genai
from typing import Optional, List, Dict
import base64
import io
from PIL import Image

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API client with automatic model discovery.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY in environment variables.")
        
        genai.configure(api_key=self.api_key)
        
        # Try models in order - gemini-pro is most reliable
        models_to_try = [
            'gemini-pro',           # Most stable and widely available
            'models/gemini-pro',    # With prefix
            'gemini-1.5-pro',       # Newer version
            'gemini-1.5-flash',    # Faster version
        ]
        
        model_initialized = False
        working_model = None
        
        print("🔍 Initializing Gemini model...")
        
        for model_name in models_to_try:
            try:
                print(f"  Trying: {model_name}...")
                test_model = genai.GenerativeModel(model_name)
                # Quick test
                test_response = test_model.generate_content("hi")
                if test_response:
                    self.model = test_model
                    self.vision_model = genai.GenerativeModel(model_name)
                    working_model = model_name
                    print(f"✅ Successfully initialized: {model_name}")
                    model_initialized = True
                    break
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower():
                    print(f"  ❌ {model_name} not available")
                else:
                    print(f"  ⚠️ {model_name} error: {str(e)[:80]}")
                continue
        
        if not model_initialized:
            # Last attempt: list all models and try first available
            try:
                print("\n🔍 Listing all available models...")
                all_models = list(genai.list_models())
                for model in all_models[:10]:  # Check first 10
                    model_name = model.name.split('/')[-1] if '/' in model.name else model.name
                    if model_name in models_to_try:
                        continue  # Already tried
                    
                    try:
                        print(f"  Trying: {model_name}...")
                        test_model = genai.GenerativeModel(model_name)
                        test_response = test_model.generate_content("hi")
                        if test_response:
                            self.model = test_model
                            self.vision_model = genai.GenerativeModel(model_name)
                            working_model = model_name
                            print(f"✅ Successfully initialized: {model_name}")
                            model_initialized = True
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Could not list models: {e}")
        
        if not model_initialized:
            error_msg = """
❌ CRITICAL: Could not initialize any Gemini model!

Possible solutions:
1. Check your API key in backend/.env
2. Verify API is enabled in Google Cloud Console
3. Check API quota/limits
4. Run: python backend/test_models.py

Error details will be shown above.
"""
            print(error_msg)
            raise ValueError("Could not initialize Gemini model")
        
        print(f"🎯 Using model: {working_model}\n")

    def generate_text_response(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict]] = None,
        language: str = "fr"
    ) -> str:
        """Generate a text response using Gemini API."""
        try:
            system_prompts = {
                "fr": """Tu es un assistant IA intelligent et très utile. Tu dois:
- Répondre à TOUTES les questions de manière directe et précise
- Comprendre le contexte et donner des réponses complètes
- Si tu ne connais pas quelque chose, dis-le honnêtement
- Sois naturel, amical et professionnel
- Réponds toujours en français""",
                "en": """You are an intelligent and very helpful AI assistant. You must:
- Answer ALL questions directly and accurately
- Understand context and provide complete answers
- If you don't know something, say so honestly
- Be natural, friendly, and professional
- Always respond in English""",
                "ar": """أنت مساعد ذكي ومفيد جدًا. يجب عليك:
- الإجابة على جميع الأسئلة بشكل مباشر ودقيق
- فهم السياق وإعطاء إجابات كاملة
- إذا كنت لا تعرف شيئًا، قل ذلك بصراحة
- كن طبيعيًا وودودًا ومهنيًا
- أجب دائمًا بالعربية"""
            }
            
            system_prompt = system_prompts.get(language, system_prompts["fr"])
            
            # Build conversation context
            conversation_context = ""
            if conversation_history:
                recent_history = conversation_history[-6:]
                for msg in recent_history:
                    role_label = {
                        "fr": {"user": "Utilisateur", "assistant": "Assistant"},
                        "en": {"user": "User", "assistant": "Assistant"},
                        "ar": {"user": "المستخدم", "assistant": "المساعد"}
                    }
                    role_name = role_label[language].get(msg.get("role", "user"), "User")
                    conversation_context += f"{role_name}: {msg.get('content', '')}\n"
            
            # Build prompt
            if conversation_context:
                if language == "ar":
                    prompt = f"{system_prompt}\n\nتاريخ المحادثة:\n{conversation_context}\nالمستخدم: {user_message}\nالمساعد:"
                elif language == "fr":
                    prompt = f"{system_prompt}\n\nHistorique de la conversation:\n{conversation_context}\nUtilisateur: {user_message}\nAssistant:"
                else:
                    prompt = f"{system_prompt}\n\nConversation history:\n{conversation_context}\nUser: {user_message}\nAssistant:"
            else:
                if language == "ar":
                    prompt = f"{system_prompt}\n\nالمستخدم: {user_message}\nالمساعد:"
                elif language == "fr":
                    prompt = f"{system_prompt}\n\nUtilisateur: {user_message}\nAssistant:"
                else:
                    prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract text from response
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    if len(candidate.content.parts) > 0:
                        part = candidate.content.parts[0]
                        if hasattr(part, 'text') and part.text:
                            return part.text.strip()
            
            return str(response).strip()
            
        except Exception as e:
            error_msg = {
                "fr": f"Désolé, une erreur s'est produite: {str(e)[:150]}",
                "en": f"Sorry, an error occurred: {str(e)[:150]}",
                "ar": f"عذرًا، حدث خطأ: {str(e)[:150]}"
            }
            print(f"❌ Gemini API Error: {e}")
            return error_msg.get(language, error_msg["fr"])

    def generate_image_response(
        self,
        user_message: str,
        image_data: bytes,
        conversation_history: Optional[List[Dict]] = None,
        language: str = "fr"
    ) -> str:
        """Generate a response based on image and text using Gemini Vision API."""
        try:
            # Convert image bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Build prompt
            if not user_message or not user_message.strip():
                prompts = {
                    "fr": "Analyse cette image en détail et décris tout ce que tu vois.",
                    "en": "Analyze this image in detail and describe everything you see.",
                    "ar": "حلل هذه الصورة بالتفصيل ووصف كل ما تراه."
                }
            else:
                prompts = {
                    "fr": f"Analyse cette image et réponds à cette question en français: {user_message}",
                    "en": f"Analyze this image and answer this question in English: {user_message}",
                    "ar": f"حلل هذه الصورة وأجب على هذا السؤال بالعربية: {user_message}"
                }
            
            prompt = prompts.get(language, prompts["fr"])
            
            # Generate response
            response = self.vision_model.generate_content([prompt, image])
            
            # Extract text
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    if len(candidate.content.parts) > 0:
                        part = candidate.content.parts[0]
                        if hasattr(part, 'text') and part.text:
                            return part.text.strip()
            
            return str(response).strip()
            
        except Exception as e:
            error_msg = {
                "fr": f"Erreur lors de l'analyse de l'image: {str(e)[:150]}",
                "en": f"Error analyzing image: {str(e)[:150]}",
                "ar": f"خطأ في تحليل الصورة: {str(e)[:150]}"
            }
            print(f"❌ Vision API Error: {e}")
            return error_msg.get(language, error_msg["fr"])

# Global instance
gemini_client = None

def get_gemini_client() -> Optional[GeminiClient]:
    """Get or create Gemini client instance"""
    global gemini_client
    if gemini_client is None:
        try:
            gemini_client = GeminiClient()
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Gemini client: {e}")
            return None
    return gemini_client
