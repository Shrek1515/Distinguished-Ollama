# Distinguished-Ollama
Projet de fin de L3, une modification d'Ollama visant à supprimer des mots bannis, ainsi qu'à détecter et traiter les hallucinations.

## Téléchargement et Préparation

1. **Téléchargez ce dépôt GitHub.** 
   Clonez ou téléchargez le dépôt.

2. **Récupérez le code source d'Ollama.** 
   - Téléchargez la version **0.6.0** d’Ollama. 
    *Le bon fonctionnement n'est garanti qu’avec cette version. Des versions plus récentes peuvent provoquer des incompatibilités.*

## Intégration du Plugin

3. **Ajoutez le plugin au code source :** 
   - Les fichiers contenus dans le dossier `ollama_source` doivent être placés dans le code source d'Ollama.
   - Copiez le dossier `plugin_filtre` dans le code source d’Ollama. 
   - Placez les fichiers restant d'`ollama_source` dans les dossiers correspondants *(pensez à sauvegarder les originaux).*

4. **Compilez Ollama** selon les instructions officielles de leur documentation.

## Ressources

5. **Placez le dossier `ressources`** dans le même répertoire que l’exécutable compilé d’Ollama.

## Lancement du plugin

6. **Préparez l’environnement Python :** 
   - Placez-vous dans le dossier `plugin`.
   - Créez un environnement virtuel :
     ```bash
     python -m venv venv
     source venv/bin/activate  # ou venv\Scripts\activate sur Windows
     ```
   - Installez les dépendances :
     ```bash
     pip install pydantic sentence-transformers
     ```

7. **Lancez le script de test :**
   ```bash
   python test_of_verification1.py

## Liste des Commandes

Le programme fonctionne via des menus, permettant à l’utilisateur de choisir les actions à effectuer :

- **1. Choisir un modèle** : Sélectionner le LLM à utiliser. Une liste des modèles disponibles sur l’ordinateur est affichée.

- **2. Choisir une liste de mots bannis** : Chemin complet vers un fichier texte listant les mots interdits (un mot par ligne). Cette étape est obligatoire.

- **3. Ajouter un mot** : Ajouter un mot à la liste des mots bannis.

- **4. Supprimer un mot** : Supprimer un mot de la liste. Si le mot n’existe pas, rien ne se passe.

- **5. Chat** : Fonction principale du plugin.
  - L'utilisateur pose une question.
  - La réponse est analysée : détection de mots bannis puis détection d'hallucinations.
  - Les mots interdits sont remplacés par “censuré” (avec le mot original entre parenthèses).
  - Une vérification d’hallucination est également effectuée et le résultat est affiché.

- **6. Quitter** : Ferme proprement le programme.

---

## Démonstration du Plugin

Voici un exemple de fonctionnement du plugin (consultez le manuel d’installation avant utilisation) :

1. **Sélection du modèle** : 
   Llama3.2 et Mistral sont généralement installés par défaut. Pour utiliser d’autres modèles, suivez la documentation Ollama.

2. **Chargement de la liste de mots bannis** : 
   Fournir le **chemin complet** vers le fichier texte. Les chemins relatifs ne fonctionnent pas.

3. **Choix des actions suivantes** : 
   - **3. Ajouter un mot** : Saisir un mot puis valider. Les doublons sont ignorés.
   - **4. Supprimer un mot** : Saisir un mot à retirer. Si absent de la liste, rien ne change.
   - **5. Lancer une discussion** : Poser une question, obtenir une réponse filtrée, avec analyse d’hallucination.
   - **6. Quitter** : Fermer l'application.

---

## Messages d’Erreur Fréquents

- **Erreur : Modèle non disponible** 
  → Vérifiez que Ollama est lancé et que le nom du modèle est correct.

- **Erreur : Réponse API invalide**
  → Vérifiez votre connexion internet ou l’état de l’API Ollama.

- **Erreur : Format de la langue**
  → Évitez les guillemets dans votre prompt.

- **Erreur : Dossier manquant pour la génération de tokens**
  → Assurez-vous que le dossier `ressources` est bien présent à côté de l’exécutable Ollama.

---
