# 📦 Guide d'Installation - Mini Chatbot

## Étape 1 : Prérequis

### Installer Python 3.8+
Téléchargez depuis [python.org](https://www.python.org/downloads/)

### Installer Node.js 16+
Téléchargez depuis [nodejs.org](https://nodejs.org/)

### Installer MySQL 8.0+
Téléchargez depuis [mysql.com](https://dev.mysql.com/downloads/mysql/)

### Installer Tesseract OCR

**Windows:**
1. Téléchargez depuis [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
2. Installez-le (par exemple dans `C:\Program Files\Tesseract-OCR`)
3. Ouvrez `backend/core/image_analyzer.py` et décommentez/modifiez la ligne :
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng tesseract-ocr-ara
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

## Étape 2 : Configuration de la Base de Données

1. Démarrez MySQL
2. Connectez-vous à MySQL :
   ```bash
   mysql -u root -p
   ```
3. Créez la base de données :
   ```sql
   CREATE DATABASE minichatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

## Étape 3 : Configuration du Backend

1. Naviguez vers le dossier backend :
   ```bash
   cd backend
   ```

2. Créez un environnement virtuel :
   ```bash
   python -m venv venv
   ```

3. Activez l'environnement virtuel :
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```

4. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

5. Créez le fichier `.env` :
   ```bash
   copy .env.example .env
   ```
   (Sur Linux/macOS : `cp .env.example .env`)

6. Modifiez `.env` avec vos identifiants MySQL :
   ```env
   DATABASE_URL=mysql+pymysql://root:VOTRE_MOT_DE_PASSE@localhost:3306/minichatbot
   ```

7. Téléchargez les données NLTK (si nécessaire) :
   ```python
   python -c "import nltk; nltk.download('punkt')"
   ```

## Étape 4 : Configuration du Frontend

1. Naviguez vers le dossier frontend :
   ```bash
   cd frontend
   ```

2. Installez les dépendances :
   ```bash
   npm install
   ```

3. (Optionnel) Créez un fichier `.env` si vous voulez changer l'URL de l'API :
   ```env
   REACT_APP_API_URL=http://localhost:8000
   ```

## Étape 5 : Démarrage

### Démarrer le Backend

Dans un terminal, depuis le dossier `backend` :
```bash
python main.py
```

Le serveur sera accessible sur `http://localhost:8000`

### Démarrer le Frontend

Dans un autre terminal, depuis le dossier `frontend` :
```bash
npm start
```

L'application sera accessible sur `http://localhost:3000`

## 🚀 Démarrage Rapide (Windows)

Vous pouvez utiliser les scripts batch fournis :
- `start_backend.bat` - Démarre le backend
- `start_frontend.bat` - Démarre le frontend

## ✅ Vérification

1. Ouvrez votre navigateur sur `http://localhost:3000`
2. Cliquez sur "Nouvelle discussion"
3. Tapez un message et envoyez-le
4. Le bot devrait répondre !

## 🐛 Dépannage

### Erreur de connexion à la base de données
- Vérifiez que MySQL est démarré
- Vérifiez les identifiants dans `.env`
- Assurez-vous que la base de données `minichatbot` existe

### Erreur Tesseract
- Vérifiez que Tesseract est installé
- Vérifiez le chemin dans `image_analyzer.py`
- Testez avec : `tesseract --version`

### Erreur CORS
- Vérifiez que le backend tourne sur le port 8000
- Vérifiez que le frontend pointe vers la bonne URL

### Erreur de port déjà utilisé
- Changez le port dans `main.py` (backend) ou `package.json` (frontend)

## 📝 Notes

- Le premier démarrage peut prendre quelques instants pour installer toutes les dépendances
- Les images téléversées sont stockées dans `backend/uploads/`
- Les conversations sont stockées dans la base de données MySQL
