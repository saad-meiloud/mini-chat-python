# 🚀 Guide de Démarrage Rapide

## Configuration Rapide

### 1. Base de Données (WampServer64)

✅ **Déjà configuré** :
- Nom de la base : `mini-chat-python`
- Utilisateur : `root`
- Mot de passe : (vide/null)
- Le fichier `.env` est déjà configuré

**Action requise** : Créez la base de données dans phpMyAdmin :
1. Ouvrez `http://localhost/phpmyadmin`
2. Créez une nouvelle base de données nommée `mini-chat-python`
3. Interclassement : `utf8mb4_unicode_ci`

### 2. Installation des Dépendances

#### Backend (Python)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### Frontend (Node.js)
```bash
cd frontend
npm install
```

### 3. Démarrage

#### Terminal 1 - Backend
```bash
cd backend
python main.py
```
✅ Vous devriez voir : `Gemini API client initialized successfully`

#### Terminal 2 - Frontend
```bash
cd frontend
npm start
```
✅ L'application s'ouvrira sur `http://localhost:3000`

### 4. Test

1. Ouvrez `http://localhost:3000`
2. Cliquez sur "Nouvelle discussion"
3. Tapez un message (en français, anglais ou arabe)
4. Le bot répondra avec l'IA Gemini ! 🎉

## ✅ Vérifications

- [ ] WampServer64 est démarré (icône verte)
- [ ] Base de données `mini-chat-python` créée
- [ ] Fichier `.env` existe dans `backend/`
- [ ] Dépendances Python installées
- [ ] Dépendances Node.js installées
- [ ] Backend démarre sans erreur
- [ ] Frontend démarre sans erreur

## 🐛 Problèmes Courants

### "Gemini API client not initialized"
→ Vérifiez que `GOOGLE_API_KEY` est dans le fichier `.env`

### "Can't connect to MySQL"
→ Vérifiez que WampServer64 est démarré et que MySQL est actif

### "Table doesn't exist"
→ Normal au premier démarrage, les tables sont créées automatiquement

### Port 8000 déjà utilisé
→ Changez le port dans `main.py` ou arrêtez l'autre application

## 📝 Notes

- La clé API Gemini est déjà configurée dans `.env`
- Les tables de base de données sont créées automatiquement
- Les images sont stockées dans `backend/uploads/`
