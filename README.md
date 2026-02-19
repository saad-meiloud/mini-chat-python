# 🤖 Mini Chatbot Intelligent

Un chatbot intelligent similaire à ChatGPT avec support multilingue (français, anglais, arabe), analyse d'images, et gestion d'historique des conversations.

## ✨ Fonctionnalités

- 🤖 **IA Gemini intégrée** : Réponses intelligentes avec Google Gemini API
- 💬 **Chat intelligent multilingue** : Support du français, anglais et arabe
- 🖼️ **Analyse d'images** : Téléversement et analyse d'images avec vision IA
- 📝 **Historique des conversations** : Sauvegarde et gestion des conversations
- 🎨 **Interface moderne** : Design inspiré de ChatGPT et Gemini
- 🌙 **Mode sombre/clair** : Basculement entre les thèmes
- 💾 **Base de données MySQL** : Persistance des données avec WampServer64
- ⚡ **Performance optimisée** : Réponses rapides et contextuelles

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** : Framework web moderne et rapide
- **Google Gemini API** : Intelligence artificielle pour les réponses
- **SQLAlchemy** : ORM pour la base de données
- **MySQL/WampServer64** : Base de données relationnelle
- **Pillow & Tesseract** : Analyse d'images et OCR
- **NLTK** : Traitement du langage naturel

### Frontend (React)
- **React 18** : Bibliothèque UI moderne
- **Axios** : Client HTTP
- **React Syntax Highlighter** : Coloration syntaxique du code
- **Lucide React** : Icônes modernes

## 📋 Prérequis

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Tesseract OCR (pour l'analyse d'images)

### Installation de Tesseract OCR

**Windows:**
1. Téléchargez Tesseract depuis [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
2. Installez-le et notez le chemin d'installation
3. Décommentez et modifiez la ligne dans `backend/core/image_analyzer.py` :
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng tesseract-ocr-ara
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

## 🚀 Installation

### 1. Configuration de la base de données (WampServer64)

Créez la base de données dans phpMyAdmin :
1. Ouvrez `http://localhost/phpmyadmin`
2. Créez une nouvelle base de données : `mini-chat-python`
3. Interclassement : `utf8mb4_unicode_ci`

**Note** : Le fichier `.env` est déjà configuré avec :
- Base de données : `mini-chat-python`
- Utilisateur : `root`
- Mot de passe : (vide/null)
- Clé API Gemini : Déjà configurée

### 2. Configuration du backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Créez un fichier `.env` dans le dossier `backend` :
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/minichatbot
```

### 3. Configuration du frontend

```bash
cd frontend
npm install
```

## 🎯 Utilisation

### Démarrer le backend

```bash
cd backend
python main.py
```

Le serveur API sera accessible sur `http://localhost:8000`

### Démarrer le frontend

```bash
cd frontend
npm start
```

L'application sera accessible sur `http://localhost:3000`

## 📡 API Endpoints

### Chat
- `POST /api/chat` - Envoyer un message (avec option d'image)
- `GET /api/conversations` - Récupérer toutes les conversations
- `GET /api/conversations/{id}` - Récupérer une conversation
- `GET /api/conversations/{id}/messages` - Récupérer les messages d'une conversation
- `POST /api/conversations/new` - Créer une nouvelle conversation
- `PUT /api/conversations/{id}` - Mettre à jour le titre d'une conversation
- `DELETE /api/conversations/{id}` - Supprimer une conversation

## 🎨 Fonctionnalités de l'interface

### Barre latérale gauche
- Bouton "Nouvelle discussion" pour créer une conversation
- Liste des conversations précédentes
- Renommer une conversation (clic sur l'icône ✏️)
- Supprimer une conversation (clic sur l'icône 🗑️)
- Basculement mode sombre/clair

### Zone de conversation
- Affichage des messages sous forme de bulles
- Support de la coloration syntaxique pour le code
- Affichage des images téléversées
- Indicateur de chargement "Le bot est en train d'écrire..."

### Zone de saisie
- Champ texte multi-lignes avec redimensionnement automatique
- Bouton de téléversement d'image
- Bouton d'envoi
- Envoi avec Entrée (Shift+Entrée pour nouvelle ligne)

## 🔧 Configuration avancée

### Intégration Gemini API

Le projet utilise déjà **Google Gemini API** pour générer des réponses intelligentes. La clé API est configurée dans le fichier `.env`.

**Fonctionnalités** :
- Réponses contextuelles basées sur l'historique de conversation
- Support multilingue (français, anglais, arabe)
- Analyse d'images avec Gemini Vision
- Détection automatique de la langue

### Personnalisation des réponses

Modifiez `backend/core/gemini_client.py` pour personnaliser les prompts système et le comportement du bot.

### Changer la clé API

Modifiez `GOOGLE_API_KEY` dans le fichier `backend/.env` :
```env
GOOGLE_API_KEY=votre_nouvelle_cle_api
```

## 🐛 Dépannage

### Erreur de connexion à la base de données
- Vérifiez que WampServer64 est démarré (icône verte)
- Vérifiez que MySQL est actif
- Vérifiez que la base de données `mini-chat-python` existe dans phpMyAdmin
- Vérifiez que le mot de passe MySQL est bien null/vide

### Erreur Gemini API
- Vérifiez que `GOOGLE_API_KEY` est dans le fichier `.env`
- Vérifiez que la clé API est valide
- Consultez les logs du backend pour plus de détails

### Erreur Tesseract
- Vérifiez que Tesseract est installé
- Vérifiez le chemin dans `image_analyzer.py`
- Installez les langues nécessaires (fra, eng, ara)

### Erreur CORS
- Vérifiez que le frontend pointe vers le bon URL backend
- Modifiez `allow_origins` dans `main.py` pour la production

## 📝 Structure du projet

```
mini-chat-python/
├── backend/
│   ├── core/
│   │   ├── processor.py          # Traitement du texte
│   │   ├── image_analyzer.py     # Analyse d'images
│   │   └── response_generator.py  # Génération de réponses
│   ├── database.py               # Modèles de base de données
│   ├── main.py                   # Application FastAPI
│   ├── requirements.txt          # Dépendances Python
│   └── .env                      # Configuration (à créer)
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/           # Composants React
│   │   ├── context/              # Context API
│   │   └── App.js
│   └── package.json
└── README.md
```

## 🚧 Améliorations futures

- [ ] Intégration avec un LLM (GPT, Claude, etc.)
- [ ] Support de la régénération de réponses
- [ ] Export des conversations
- [ ] Recherche dans l'historique
- [ ] Support de fichiers PDF/DOCX
- [ ] Authentification utilisateur
- [ ] Rate limiting avancé
- [ ] Tests unitaires et d'intégration

## 📄 Licence

Ce projet est sous licence MIT.

## 👨‍💻 Auteur

Développé avec ❤️ pour créer un chatbot intelligent et moderne.
