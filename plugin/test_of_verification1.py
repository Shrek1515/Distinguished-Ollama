from Chain_of_verification import ChainOfVerification
import requests
from sentence_transformers import SentenceTransformer, util
import ollama_modifs
import os

semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
#declaration de  la methode qui permet de recuperer les models disponibles sur ollama 
def get_available_models():
    response = requests.get("http://localhost:11434/api/tags") #appel api vers la classe tags qui contient les models de ollama 
    if response.status_code != 200: #exeption en cas d'erreur 
        raise Exception(f"Erreur lors de la récupération des modèles: {response.text}")
    return [model["name"] for model in response.json()["models"]] #  retour des models disponibles 
def are_questions_similar(q1, q2, threshold=0.8):
    emb1 = semantic_model.encode(q1, convert_to_tensor=True)
    emb2 = semantic_model.encode(q2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2)
    return similarity.item() >= threshold


#declaration methode qui ermets d'interagir avec un model et faire la verification
def test_with_model(model_name: str): 
    chain = ChainOfVerification(model_name=model_name) #creation d'un instance de la classe chain of verification avec le model choisi
    hallucination_count = 0  # Compte les hallucinations consécutives
    
    previous_question = None # variable qui contient la question precedente 

    while True:
        question = input("Posez votre question : ") #reception du promt de l'utilisateur 

        # Vérifie si l'utilisateur répète la même question
        if previous_question is not None and (question.strip().lower() == previous_question.strip().lower()  or are_questions_similar(question, previous_question)):
            print(" Vous avez déjà posé cette question récemment.")
        
        result = chain.verify_response(question)

        print("\n=== Résultats de la vérification ===")
        print(f"\nRéponse initiale : {result['initial_response']}")

        print("\n=== Questions de vérification et réponses ===")
        print(result['verification_results'])

        print(f"\nStatut de vérification : {result['verification_status']}")
        print(f"Pourcentage de vérification : {result['verification_percentage']:.2f}%")

        print(f"\nRéponse finale : {result['final_response']}")

        # Détection d'hallucination
        is_hallucination = (
            result['verification_status'].lower() !="Je ne peux pas donner une réponse certaine à cette question."
             and result[ 'verification_percentage'] >50
        )

        if is_hallucination:
            hallucination_count += 1
            print("Réponse considérée comme une hallucination.")

            if hallucination_count >= 3:
                print("\n Le modèle n’a pas pu générer une réponse fiable deux fois de suite.")
                print("Veuillez réessayer plus tard avec une autre question ou après avoir reformulé.")
                break
        else:
            hallucination_count = 0  # Réinitialiser le compteur si la réponse est correcte

        choix_continuer = input("Continuer à parler avec le modèle ? O/N")
        if choix_continuer != "O":
            break
            
        previous_question = question  # Mémorise la dernière question
        previous_embedding = semantic_model.encode(question, convert_to_tensor=True)

def main():
    print('Bonjour et bienvenue sur Distinguished Ollama, une version d\'Ollama plus civilisée.')
    print('Avant de commencer vous allez devoir choisir votre modèle,')
    print('pour vous aider voici la liste des modèles disponibles sur votre machine :')
    print('Si vous ne trouvez pas de modèles qui vous convient, vous pouvez en installer en suivant la procédure prévue par Ollama.')
    print()
    
    try:
        print("Modèles disponibles sur Ollama:")
        models = get_available_models()
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
        
        # Sélection du modèle
        while True:
            try:
                choice = int(input("\nChoisissez un numéro de modèle: "))
                if 1 <= choice <= len(models):
                    selected_model = models[choice - 1]
                    break
                print("Veuillez entrer un numéro valide.")
            except ValueError:
                print("Veuillez entrer un numéro.")
        
        print()
        print('Maitenant, vous devez aussi charger une liste de mots à bannir, pour cela veuillez entrer le chemin complet vers celle-ci :')
        # Sélection de la liste
        while True:
            choix = input("Entrez le chemin complet vers la liste de mots à bannir :")
            if not os.path.exists(choix):
                print("Veuillez entrer un chemin valide.")
            else:
                try:
                    ollama_modifs.load_list(choix, selected_model)
                    break
                except Exception as e:
                    print(f'Il y a eu un problème lors du chargement de la liste : {str(e)}')
        
        print()
        rep = 0
        verifier = ""

        while rep != 6:
            print()
            print("1. Choisir modèle.")
            print("2. Choisir liste.")
            print("3. Ajouter mot (assurez-vous d'avoir chargé une liste).")
            print("4. Enlever mot (assurez-vous d'avoir chargé une liste).")
            print("5. Chat (assurez-vous de charger une liste et de choisir un modèle au préalable).")
            print("6. Quitter")
            print()
            rep = int(input("Votre choix ?"))

            try:
                match rep:
                    case 1:
                        print("Modèles disponibles sur Ollama :")
                        models = get_available_models()
                        for i, model in enumerate(models, 1):
                            print(f"{i}. {model}")

                        while True:
                            try:
                                choice = int(input("\nChoisissez un numéro de modèle : "))
                                if 1 <= choice <= len(models):
                                    selected_model = models[choice - 1]
                                    break
                                print("Veuillez entrer un numéro valide.")
                            except ValueError:
                                print("Veuillez entrer un numéro.")

                    case 2:
                        while True:
                            choix = input("Entrez le chemin complet vers la liste de mots à bannir :")
                            if not os.path.exists(choix):
                                print("Veuillez entrer un chemin valide.")
                            else:
                                try:
                                    ollama_modifs.load_list(choix, selected_model)
                                    break
                                except Exception as e:
                                    print(f'Il y a eu un problème lors du chargement de la liste : {str(e)}')

                    case 3:
                        choix = input("Entrez le mot que vous souhaitez ajouter :")
                        ollama_modifs.add_word(choix)

                    case 4:
                        choix = input("Entrez le mot que vous souhaitez supprimer :")
                        ollama_modifs.remove_word(choix)

                    case 5:
                        test_with_model(selected_model)
                        
                    case 6:
                        print("Au revoir !")

                    case _:
                        print("Choix incorrect, veuillez réessayer.")

            except Exception as e:
                print(f"Une erreur est survenue: {str(e)}")
        
    except Exception as e:
        print(f'Erreur : {str(e)}')
    
    
        

if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
