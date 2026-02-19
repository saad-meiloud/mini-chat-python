import random
import re
from typing import Optional, Dict, List
from .processor import processor
from .image_analyzer import image_analyzer
from .gemini_client import get_gemini_client

class ResponseGenerator:
    def __init__(self):
        self.greetings = {
            "fr": ["Bonjour ! Comment puis-je vous aider ?", "Salut ! Que puis-je faire pour vous ?", "Bonjour ! En quoi puis-je vous assister aujourd'hui ?"],
            "en": ["Hello! How can I help you?", "Hi! What can I do for you?", "Hello! How may I assist you today?"],
            "ar": ["مرحبا! كيف يمكنني مساعدتك؟", "أهلا! ماذا يمكنني أن أفعل لك؟", "مرحبا! كيف يمكنني مساعدتك اليوم؟"]
        }
        
        self.empty_message_responses = {
            "fr": "Veuillez saisir un message. Je suis là pour vous aider !",
            "en": "Please enter a message. I'm here to help!",
            "ar": "يرجى إدخال رسالة. أنا هنا لمساعدتك!"
        }
        
        self.clarification_responses = {
            "fr": "Pourriez-vous reformuler votre question ? Je ne suis pas sûr de comprendre exactement ce que vous voulez dire.",
            "en": "Could you rephrase your question? I'm not sure I understand exactly what you mean.",
            "ar": "هل يمكنك إعادة صياغة سؤالك؟ لست متأكدًا من أنني أفهم بالضبط ما تقصده."
        }
        
        self.not_understood_responses = {
            "fr": "Je ne comprends pas bien votre question. Pouvez-vous être plus précis ou reformuler différemment ?",
            "en": "I don't understand your question well. Can you be more specific or rephrase it differently?",
            "ar": "لا أفهم سؤالك جيدًا. هل يمكنك أن تكون أكثر تحديدًا أو إعادة صياغته بشكل مختلف؟"
        }

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        Returns: 'fr', 'en', or 'ar'
        """
        text_lower = text.lower().strip()
        
        # Arabic words written in Latin script (common transliterations)
        arabic_latin_words = ['salam', 'salaam', 'ahlan', 'marhaba', 'shukran', 'afwan', 
                             'ma3a salama', 'inshallah', 'mashallah', 'alhamdulillah',
                             'bismillah', 'assalamu', 'alaikum', 'waalaikum']
        
        # Check for Arabic characters
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        if arabic_pattern.search(text):
            return "ar"
        
        # Check for Arabic words in Latin script
        if any(word in text_lower for word in arabic_latin_words):
            return "ar"
        
        # French detection
        french_pattern = re.compile(r'[àâäéèêëïîôùûüÿç]', re.IGNORECASE)
        french_words = ['bonjour', 'salut', 'merci', 'comment', 'pourquoi', 'quand', 'où', 
                        'comment ça va', 'ça va', 'très bien', 'excusez-moi', 's\'il vous plaît']
        
        if french_pattern.search(text) or any(word in text_lower for word in french_words):
            return "fr"
        
        # Default to English
        return "en"

    def generate_response(self, user_message: str, image_data: Optional[bytes] = None, conversation_history: List[Dict] = None) -> Dict[str, str]:
        """
        Generate a response based on user message and optional image using Gemini API.
        Returns a dictionary with 'content' and 'language'.
        """
        if conversation_history is None:
            conversation_history = []
        
        # Detect language
        language = self.detect_language(user_message)
        
        # Normalize and process text
        normalized_text = processor.normalize(user_message)
        tokens = processor.tokenize(normalized_text)
        
        # Check for empty message
        if not normalized_text.strip() and not image_data:
            return {
                "content": random.choice(self.empty_message_responses[language]),
                "language": language
            }
        
        # ALWAYS try to use Gemini API first - it's the main intelligence engine
        gemini = get_gemini_client()
        
        if not gemini:
            # If Gemini is not available, return a helpful error message
            error_msg = {
                "fr": "Désolé, le service d'IA n'est pas disponible pour le moment. Veuillez réessayer plus tard.",
                "en": "Sorry, the AI service is not available at the moment. Please try again later.",
                "ar": "عذرًا، خدمة الذكاء الاصطناعي غير متاحة حاليًا. يرجى المحاولة مرة أخرى لاحقًا."
            }
            return {
                "content": error_msg.get(language, error_msg["en"]),
                "language": language
            }
        
        # Use Gemini API - this is the primary method
        try:
            # If image is provided, use vision model
            if image_data:
                print(f"📸 Analyzing image with Gemini Vision API (language: {language})")
                response_content = gemini.generate_image_response(
                    user_message=user_message if user_message.strip() else {
                        "fr": "Décris cette image en détail",
                        "en": "Describe this image in detail",
                        "ar": "اوصف هذه الصورة بالتفصيل"
                    }.get(language, "Describe this image in detail"),
                    image_data=image_data,
                    conversation_history=conversation_history,
                    language=language
                )
            else:
                # Use text model
                print(f"💬 Generating text response with Gemini API (language: {language})")
                response_content = gemini.generate_text_response(
                    user_message=user_message,
                    conversation_history=conversation_history,
                    language=language
                )
            
            # Always return Gemini response if we got one
            if response_content:
                print(f"✅ Gemini response received: {response_content[:100]}...")
                return {
                    "content": response_content,
                    "language": language
                }
            else:
                raise Exception("Empty response from Gemini API")
                
        except Exception as e:
            print(f"❌ Error using Gemini API: {e}")
            import traceback
            traceback.print_exc()
            
            # Only use fallback for very specific errors, otherwise retry
            error_msg = {
                "fr": f"Désolé, une erreur s'est produite. Veuillez réessayer. Erreur: {str(e)[:100]}",
                "en": f"Sorry, an error occurred. Please try again. Error: {str(e)[:100]}",
                "ar": f"عذرًا، حدث خطأ. يرجى المحاولة مرة أخرى. الخطأ: {str(e)[:100]}"
            }
            return {
                "content": error_msg.get(language, error_msg["en"]),
                "language": language
            }
        
        # This should never be reached, but keep fallback as absolute last resort
        # Process image if provided
        image_context = ""
        if image_data:
            analysis = image_analyzer.analyze_image(image_data)
            if analysis.get("has_text"):
                image_context = f"L'image contient le texte suivant: {analysis['text']}. "
            image_context += f"Description de l'image: {analysis.get('description', 'Image fournie')}. "
        
        # Check for greetings
        greeting_keywords = {
            "fr": ["bonjour", "salut", "bonsoir", "bonne nuit", "hello", "hi"],
            "en": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
            "ar": ["مرحبا", "أهلا", "السلام عليكم"]
        }
        
        if any(keyword in normalized_text for keyword in greeting_keywords[language]):
            return {
                "content": random.choice(self.greetings[language]),
                "language": language
            }
        
        # Generate intelligent response
        response = self._generate_intelligent_response(
            normalized_text, 
            tokens, 
            image_context, 
            language,
            conversation_history
        )
        
        return {
            "content": response,
            "language": language
        }

    def _generate_intelligent_response(self, normalized_text: str, tokens: List[str], image_context: str, language: str, history: List[Dict]) -> str:
        """
        Generate an intelligent response based on the processed text.
        This is a simplified version - can be enhanced with LLM integration.
        """
        # Question words detection
        question_words = {
            "fr": ["quoi", "comment", "pourquoi", "quand", "où", "qui", "quel", "quelle", "combien"],
            "en": ["what", "how", "why", "when", "where", "who", "which", "how many"],
            "ar": ["ماذا", "كيف", "لماذا", "متى", "أين", "من"]
        }
        
        is_question = any(word in normalized_text for word in question_words[language])
        
        # Simple response generation based on keywords
        responses = {
            "fr": self._generate_french_response(normalized_text, tokens, image_context, is_question),
            "en": self._generate_english_response(normalized_text, tokens, image_context, is_question),
            "ar": self._generate_arabic_response(normalized_text, tokens, image_context, is_question)
        }
        
        return responses.get(language, responses["en"])

    def _generate_french_response(self, text: str, tokens: List[str], image_context: str, is_question: bool) -> str:
        """Generate response in French"""
        if image_context:
            return f"{image_context}Basé sur l'image que vous avez fournie, je peux vous dire que c'est une image intéressante. Comment puis-je vous aider davantage avec cette image ?"
        
        # Simple keyword-based responses (can be enhanced with LLM)
        if "aide" in text or "help" in text:
            return "Je suis là pour vous aider ! Posez-moi vos questions et je ferai de mon mieux pour y répondre."
        
        if "merci" in text or "thank" in text:
            return "De rien ! N'hésitez pas si vous avez d'autres questions."
        
        if is_question:
            return f"Excellente question ! Basé sur votre demande '{text}', je peux vous dire que c'est un sujet intéressant. Pourriez-vous être plus spécifique pour que je puisse vous donner une réponse plus précise ?"
        
        return f"Je comprends que vous dites '{text}'. Pouvez-vous me donner plus de détails ou poser une question spécifique ?"

    def _generate_english_response(self, text: str, tokens: List[str], image_context: str, is_question: bool) -> str:
        """Generate response in English"""
        if image_context:
            return f"{image_context}Based on the image you provided, I can tell you that it's an interesting image. How can I help you further with this image?"
        
        if "help" in text:
            return "I'm here to help! Ask me your questions and I'll do my best to answer them."
        
        if "thank" in text:
            return "You're welcome! Feel free to ask if you have other questions."
        
        if is_question:
            return f"Great question! Based on your request '{text}', I can tell you that it's an interesting topic. Could you be more specific so I can give you a more precise answer?"
        
        return f"I understand you're saying '{text}'. Can you give me more details or ask a specific question?"

    def _generate_arabic_response(self, text: str, tokens: List[str], image_context: str, is_question: bool) -> str:
        """Generate response in Arabic"""
        if image_context:
            return f"{image_context}بناءً على الصورة التي قدمتها، يمكنني أن أخبرك أنها صورة مثيرة للاهتمام. كيف يمكنني مساعدتك أكثر مع هذه الصورة؟"
        
        if "مساعدة" in text or "help" in text:
            return "أنا هنا لمساعدتك! اطرح علي أسئلتك وسأبذل قصارى جهدي للإجابة عليها."
        
        if "شكر" in text or "thank" in text:
            return "عفوًا! لا تتردد في السؤال إذا كان لديك أسئلة أخرى."
        
        if is_question:
            return f"سؤال رائع! بناءً على طلبك '{text}'، يمكنني أن أخبرك أنه موضوع مثير للاهتمام. هل يمكنك أن تكون أكثر تحديدًا حتى أتمكن من إعطائك إجابة أكثر دقة؟"
        
        return f"أفهم أنك تقول '{text}'. هل يمكنك إعطائي المزيد من التفاصيل أو طرح سؤال محدد؟"

response_generator = ResponseGenerator()
