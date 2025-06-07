# Distinguished-Ollama
Projet de fin de L3, une modification d'Ollama visant à supprimer des mots bannis, ainsi qu'à détecter et traiter les hallucinations.

## Téléchargement et Préparation

1. **Téléchargez ce dépôt GitHub.** 
   Clonez ou téléchargez les fichiers localement.

2. **Récupérez le code source d'Ollama.** 
   - Téléchargez la version **0.6.0** d’Ollama. 
    *Le bon fonctionnement n'est garanti qu’avec cette version. Des versions plus récentes peuvent provoquer des incompatibilités.*

## Intégration du Plugin

3. **Ajoutez le plugin au code source :** 
   - Copiez le dossier `plugin_filtre` dans le code source d’Ollama. 
   - Remplacez les fichiers existants dans les autres dossiers si nécessaire *(pensez à sauvegarder les originaux).*

4. **Compilez Ollama** selon les instructions officielles de leur documentation.

## Ressources

5. **Placez le dossier `ressources`** dans le même répertoire que l’exécutable compilé d’Ollama.

## Lancement du plugin

6. **Préparez l’environnement Python :** 
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

