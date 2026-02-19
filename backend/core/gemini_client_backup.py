import os
import warnings
# Note: google.generativeai is deprecated but still works
# TODO: Migrate to google.genai package in the future
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
        Initialize Gemini API client.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY in environment variables.")
        
        genai.configure(api_key=self.api_key)
        
        # First, list all available models to find the right one
        print("🔍 Searching for available Gemini models...")
        available_models = []
        model_initialized = False
        
        try:
            # List all available models
            all_models = list(genai.list_models())
            print(f"📋 Found {len(all_models)} available models:")
            
            for model in all_models:
                model_name = model.name
                # Extract just the model name without the full path
                if '/' in model_name:
                    short_name = model_name.split('/')[-1]
                else:
                    short_name = model_name
                
                # Check if model supports generateContent
                supports_generate = False
                if hasattr(model, 'supported_generation_methods'):
                    supports_generate = 'generateContent' in model.supported_generation_methods
                
                print(f"  - {short_name} (supports generateContent: {supports_generate})")
                
                if supports_generate:
                    available_models.append(short_name)
            
            # Try models in order of preference
            preferred_models = [
                'gemini-pro',           # Most common and stable
                'gemini-1.5-pro',       # Newer version
                'gemini-1.5-flash',     # Faster version
                'gemini-2.0-flash-exp', # Experimental
            ]
            
            # Add any other available models
            for model_name in available_models:
                if model_name not in preferred_models:
                    preferred_models.append(model_name)
            
            print(f"\n🎯 Trying models in order: {preferred_models[:5]}...")
            
            # Try each model
            for model_name in preferred_models:
                if model_name not in available_models:
                    continue
                    
                try:
                    print(f"  Trying: {model_name}...")
                    self.model = genai.GenerativeModel(model_name)
                    self.vision_model = genai.GenerativeModel(model_name)
                    
                    # Test if it actually works
                    test_response = self.model.generate_content("test")
                    if test_response:
                        print(f"✅ Successfully initialized: {model_name}")
                        model_initialized = True
                        break
                except Exception as e:
                    print(f"  ❌ {model_name} failed: {str(e)[:100]}")
                    continue
            
            if not model_initialized:
                # Last resort: try gemini-pro without checking
                print("\n⚠️ Trying gemini-pro as last resort...")
                try:
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.vision_model = genai.GenerativeModel('gemini-pro')
                    print("✅ Using gemini-pro")
                    model_initialized = True
                except Exception as e:
                    print(f"❌ gemini-pro also failed: {e}")
                    
        except Exception as e:
            print(f"⚠️ Error listing models: {e}")
            # Fallback: try gemini-pro directly
            try:
                print("Trying gemini-pro directly...")
                self.model = genai.GenerativeModel('gemini-pro')
                self.vision_model = genai.GenerativeModel('gemini-pro')
                print("✅ Using gemini-pro (fallback)")
                model_initialized = True
            except Exception as e2:
                print(f"❌ Fallback failed: {e2}")
        
        if not model_initialized:
            error_msg = """
❌ Could not initialize any Gemini model!
Possible reasons:
1. Invalid API key - check GOOGLE_API_KEY in .env
2. API quota exceeded
3. Network connection issue
4. Model names have changed

Please check:
- Your API key is correct
- You have API access enabled
- Your internet connection is working
"""
            print(error_msg)
            raise ValueError("Could not initialize any Gemini model. Check API key and availability.")

    def generate_text_response(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict]] = None,
        language: str = "fr"
    ) -> str:
        """
        Generate a text response using Gemini API.
        
        Args:
            user_message: The user's message
            conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
            language: Detected language (fr, en, ar)
        
        Returns:
            Generated response text
        """
        try:
            # Add system prompt based on language - improved prompts for better responses
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
                # Keep last 6 messages for context (3 exchanges)
                recent_history = conversation_history[-6:]
                for msg in recent_history:
                    role_label = {
                        "fr": {"user": "Utilisateur", "assistant": "Assistant"},
                        "en": {"user": "User", "assistant": "Assistant"},
                        "ar": {"user": "المستخدم", "assistant": "المساعد"}
                    }
                    role_name = role_label[language].get(msg.get("role", "user"), "User")
                    conversation_context += f"{role_name}: {msg.get('content', '')}\n"
            
            # Build final prompt - improved format for better understanding
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
            try:
                response = self.model.generate_content(prompt)
            except Exception as api_error:
                # If generateContent fails, try with different approach
                error_str = str(api_error)
                if "404" in error_str or "not found" in error_str.lower():
                    raise Exception(f"Model not available. Error: {error_str}")
                raise api_error
            
            # Handle response - multiple formats possible
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            
            # Try alternative response formats
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content'):
                    if hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                        part = candidate.content.parts[0]
                        if hasattr(part, 'text') and part.text:
                            return part.text.strip()
                    # Try direct text access
                    if hasattr(candidate.content, 'text') and candidate.content.text:
                        return candidate.content.text.strip()
            
            # Last resort: convert to string
            response_str = str(response)
            if response_str and response_str != "None":
                return response_str.strip()
            
            raise Exception("Empty or invalid response from Gemini API")
            
        except Exception as e:
            error_msg = {
                "fr": f"Désolé, une erreur s'est produite lors de la génération de la réponse: {str(e)}",
                "en": f"Sorry, an error occurred while generating the response: {str(e)}",
                "ar": f"عذرًا، حدث خطأ أثناء إنشاء الرد: {str(e)}"
            }
            print(f"Gemini API Error: {e}")
            return error_msg.get(language, error_msg["fr"])

    def generate_image_response(
        self,
        user_message: str,
        image_data: bytes,
        conversation_history: Optional[List[Dict]] = None,
        language: str = "fr"
    ) -> str:
        """
        Generate a response based on image and text using Gemini Vision API.
        
        Args:
            user_message: The user's message/question about the image
            image_data: Image bytes
            conversation_history: Previous conversation context
            language: Detected language
        
        Returns:
            Generated response text
        """
        try:
            # Convert image bytes to PIL Image
            try:
                image = Image.open(io.BytesIO(image_data))
                # Convert to RGB if necessary (some formats like PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    # Create a white background
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    rgb_image.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = rgb_image
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                print(f"📸 Image processed: {image.size[0]}x{image.size[1]}, mode: {image.mode}")
            except Exception as img_error:
                raise Exception(f"Failed to process image: {str(img_error)}")
            
            # Build prompt based on language - improved for better image analysis
            if not user_message or not user_message.strip():
                prompts = {
                    "fr": "Analyse cette image en détail et décris tout ce que tu vois. Sois précis et complet.",
                    "en": "Analyze this image in detail and describe everything you see. Be precise and complete.",
                    "ar": "حلل هذه الصورة بالتفصيل ووصف كل ما تراه. كن دقيقًا وشاملًا."
                }
            else:
                prompts = {
                    "fr": f"""Analyse cette image attentivement et réponds à la question suivante en français de manière détaillée et précise: "{user_message}"

Si la question concerne le contenu de l'image, décris ce que tu vois. Si c'est une question générale, réponds en te basant sur ce que tu observes dans l'image.""",
                    "en": f"""Carefully analyze this image and answer the following question in English in a detailed and precise manner: "{user_message}"

If the question is about the image content, describe what you see. If it's a general question, answer based on what you observe in the image.""",
                    "ar": f"""حلل هذه الصورة بعناية وأجب على السؤال التالي بالعربية بشكل مفصل ودقيق: "{user_message}"

إذا كان السؤال يتعلق بمحتوى الصورة، فصف ما تراه. إذا كان سؤالًا عامًا، فأجب بناءً على ما تلاحظه في الصورة."""
                }
            
            prompt = prompts.get(language, prompts["fr"])
            
            # Generate response using vision model
            response = self.vision_model.generate_content([prompt, image])
            
            # Handle response
            if hasattr(response, 'text'):
                return response.text.strip()
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    if len(candidate.content.parts) > 0 and hasattr(candidate.content.parts[0], 'text'):
                        return candidate.content.parts[0].text.strip()
            else:
                return str(response)
            
        except Exception as e:
            error_msg = {
                "fr": f"Désolé, une erreur s'est produite lors de l'analyse de l'image: {str(e)}",
                "en": f"Sorry, an error occurred while analyzing the image: {str(e)}",
                "ar": f"عذرًا، حدث خطأ أثناء تحليل الصورة: {str(e)}"
            }
            return error_msg.get(language, error_msg["fr"])

# Global instance (will be initialized in main.py)
gemini_client = None

def get_gemini_client() -> Optional[GeminiClient]:
    """Get or create Gemini client instance"""
    global gemini_client
    if gemini_client is None:
        try:
            gemini_client = GeminiClient()
        except Exception as e:
            print(f"Warning: Could not initialize Gemini client: {e}")
            return None
    return gemini_client
