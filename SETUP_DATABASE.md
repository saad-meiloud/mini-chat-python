# 🗄️ Configuration de la Base de Données - WampServer64

## Étapes de Configuration

### 1. Démarrer WampServer64

Assurez-vous que WampServer64 est démarré et que le service MySQL est actif (icône verte).

### 2. Créer la Base de Données

1. Ouvrez phpMyAdmin :
   - Cliquez sur l'icône WampServer dans la barre des tâches
   - Sélectionnez "phpMyAdmin"
   - Ou accédez à `http://localhost/phpmyadmin`

2. Créez la base de données :
   - Cliquez sur l'onglet "Bases de données"
   - Dans "Créer une base de données", entrez : `mini-chat-python`
   - Sélectionnez l'interclassement : `utf8mb4_unicode_ci`
   - Cliquez sur "Créer"

### 3. Vérifier la Configuration

La base de données `mini-chat-python` doit être créée avec :
- **Nom** : `mini-chat-python`
- **Utilisateur** : `root`
- **Mot de passe** : (vide/null)
- **Hôte** : `localhost`
- **Port** : `3306`

### 4. Configuration du Fichier .env

Le fichier `.env` dans le dossier `backend` doit contenir :

```env
DATABASE_URL=mysql+pymysql://root@localhost:3306/mini-chat-python
GOOGLE_API_KEY=AIzaSyCVRXxDvQZfH-BUVYSLGUFpRwdJXjKHtJg
```

**Note** : Pas de mot de passe après `root@` car le mot de passe est null/vide.

### 5. Tester la Connexion

Lancez le backend :
```bash
cd backend
python main.py
```

Si tout fonctionne, vous verrez :
- ✅ Les tables sont créées automatiquement
- ✅ Gemini API client initialized successfully

### 6. Vérification dans phpMyAdmin

Après le premier démarrage du backend, vous devriez voir deux tables créées :
- `conversations` : Stocke les conversations
- `messages` : Stocke les messages de chaque conversation

## 🔧 Dépannage

### Erreur : "Access denied for user 'root'@'localhost'"

**Solution** :
1. Ouvrez phpMyAdmin
2. Allez dans l'onglet "Comptes d'utilisateurs"
3. Vérifiez que l'utilisateur `root` existe et n'a pas de mot de passe
4. Si nécessaire, modifiez le mot de passe de `root` pour le laisser vide

### Erreur : "Unknown database 'mini-chat-python'"

**Solution** :
1. Vérifiez que la base de données existe dans phpMyAdmin
2. Vérifiez l'orthographe du nom de la base de données
3. Assurez-vous que le nom est exactement : `mini-chat-python` (avec tirets)

### Erreur : "Can't connect to MySQL server"

**Solution** :
1. Vérifiez que WampServer64 est démarré
2. Vérifiez que le service MySQL est actif (icône verte)
3. Redémarrez WampServer64 si nécessaire

### Erreur : "Table 'conversations' doesn't exist"

**Solution** :
- C'est normal au premier démarrage
- Les tables sont créées automatiquement par SQLAlchemy
- Si l'erreur persiste, vérifiez les permissions de l'utilisateur `root`

## 📝 Notes Importantes

- Le mot de passe MySQL est **null/vide**, donc pas besoin de `:password` dans l'URL
- La base de données sera créée automatiquement si elle n'existe pas (selon les permissions)
- Les tables sont créées automatiquement au premier démarrage du backend
- Assurez-vous que le port MySQL est bien 3306 (port par défaut de WampServer)
