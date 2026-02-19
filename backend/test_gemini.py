"""
Script de test pour vérifier la connexion à l'API Gemini
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Erreur: GOOGLE_API_KEY non trouvée dans .env")
    exit(1)

print(f"🔑 Clé API trouvée: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    
    # Lister les modèles disponibles
    print("\n📋 Liste des modèles disponibles:")
    models = list(genai.list_models())
    for model in models:
        print(f"  - {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Méthodes supportées: {model.supported_generation_methods}")
    
    # Tester un modèle simple
    print("\n🧪 Test de génération avec gemini-1.5-flash...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Dis bonjour en français")
        print(f"✅ Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur avec gemini-1.5-flash: {e}")
        
        # Essayer gemini-pro
        print("\n🧪 Test de génération avec gemini-pro...")
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Dis bonjour en français")
            print(f"✅ Réponse: {response.text}")
        except Exception as e2:
            print(f"❌ Erreur avec gemini-pro: {e2}")
            
            # Essayer avec le préfixe models/
            print("\n🧪 Test de génération avec models/gemini-pro...")
            try:
                model = genai.GenerativeModel('models/gemini-pro')
                response = model.generate_content("Dis bonjour en français")
                print(f"✅ Réponse: {response.text}")
            except Exception as e3:
                print(f"❌ Erreur avec models/gemini-pro: {e3}")
                print("\n❌ Aucun modèle ne fonctionne. Vérifiez votre clé API.")

except Exception as e:
    print(f"❌ Erreur générale: {e}")
    import traceback
    traceback.print_exc()
