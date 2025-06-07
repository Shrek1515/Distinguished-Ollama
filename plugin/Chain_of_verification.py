from typing import Dict, List
import requests
from pydantic import BaseModel
import time

class VerificationStep(BaseModel):
    question: str
    answer: str

class ChainOfVerification:
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"  # Port par défaut d'Ollama
        # Cache pour stocker les réponses fréquentes
        self.response_cache = {}
    
    def _call_ollama(self, prompt: str, cache_key: str = None) -> str:
        # Vérifier si la réponse est dans le cache
        if cache_key and cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        # Mesurer le temps de réponse
        start_time = time.time()
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream":False,
                "temperature":0.9
            }
        )
        
        # Calculer le temps de réponse
        elapsed_time = time.time() - start_time
        
        if response.status_code != 200:
            raise Exception(f"Erreur Ollama: {response.text}")
        
        result = response.json()["message"]["content"]
        
        # Stocker dans le cache si une clé est fournie
        if cache_key:
            self.response_cache[cache_key] = result
            
        return result

    def verify_response(self, question: str) -> Dict:
        # Étape 0: Vérification préalable et génération de la réponse initiale en une seule requête
        combined_prompt = f"""Question: {question}
IMPORTANT: Réponds uniquement en français.
IMPORTANT: Réponds à cette question de manière précise et factuelle.
IMPORTANT: Si tu n'es pas ABSOLUMENT CERTAIN de la réponse, dis "Je ne suis pas certain de cette information."
IMPORTANT: Ne fais JAMAIS d'hypothèses sur des informations historiques ou factuelles.
IMPORTANT: Ne pas inventer d'informations.
IMPORTANT: Si tu n'as pas de source fiable, dis "Je ne peux pas confirmer cette information avec certitude."
IMPORTANT: Format: Une seule phrase simple.
IMPORTANT: Ne pas utiliser d'anglais.

Ensuite, génère exactement 3 questions de vérification qui permettraient de confirmer ou infirmer ta réponse.
Les questions doivent être spécifiques, vérifiables, et ne pas commencer par "Est-ce que" ou des numéros.

Format de sortie:
RÉPONSE: [ta réponse à la question]
QUESTIONS:
[question 1]
[question 2]
[question 3]"""
        
        combined_response = self._call_ollama(combined_prompt, f"combined_{question}")
        
        # Extraire la réponse initiale et les questions
        initial_response = ""
        verification_questions = []
        
        # Analyser la réponse combinée
        parts = combined_response.split("QUESTIONS:")
        if len(parts) >= 2:
            response_part = parts[0].strip()
            questions_part = parts[1].strip()
            
            # Extraire la réponse initiale
            if "RÉPONSE:" in response_part:
                initial_response = response_part.split("RÉPONSE:")[1].strip()
            else:
                initial_response = response_part.strip()
            
            # Extraire les questions
            for line in questions_part.split('\n'):
                q = line.strip()
                if q and len(q) > 10:
                    verification_questions.append(q)
        
        # Si l'extraction a échoué, utiliser la réponse complète comme réponse initiale
        if not initial_response:
            initial_response = combined_response.strip()
        
        # Si nous n'avons pas de questions, en générer quelques-unes basées sur la réponse
        if not verification_questions:
            verification_questions = [
                f"Cette information est-elle vérifiable ?",
                f"Cette information est-elle cohérente avec les faits connus ?",
                f"Cette information est-elle précise et détaillée ?"
            ]
        
        # Limiter à 3 questions maximum
        verification_questions = verification_questions[:3]
        
        # Vérifier si la réponse contient des mots indiquant l'incertitude
        uncertainty_indicators = ["je ne suis pas certain", "je ne peux pas confirmer", "je ne sais pas", "incertain", "probablement", "peut-être"]
        has_uncertainty = any(indicator in initial_response.lower() for indicator in uncertainty_indicators)
        
        # Étape 1: Vérification de toutes les questions en une seule requête
        verification_steps = []
        verification_results = []
        
        # Créer un prompt unique pour toutes les questions avec des instructions plus claires
        all_questions_prompt = f"""IMPORTANT: Réponds uniquement en français.
IMPORTANT: Pour chaque question, réponds uniquement par 'Vérifié' ou 'Non vérifié', sans explication supplémentaire.
IMPORTANT: Format: Une réponse par ligne, sans numérotation ni puces.
IMPORTANT: Ne pas utiliser d'anglais.
IMPORTANT: Réponds 'Vérifié' si l'information est généralement acceptée comme vraie et vérifiable.
IMPORTANT: Réponds 'Non vérifié' uniquement si l'information est clairement fausse ou si tu n'en sais vraiment rien.
IMPORTANT: Pour les informations de connaissances générales, sois plus indulgent.
IMPORTANT: Pour les questions sur les fondateurs d'entreprises, les dates historiques, ou les faits vérifiables, réponds 'Vérifié' si tu es certain.

Questions:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(verification_questions)])}

Réponses (une par ligne):"""
        
        # Obtenir toutes les réponses en une seule requête
        all_answers_text = self._call_ollama(all_questions_prompt, f"all_answers_{question}")
        
        # Traiter les réponses
        answers = []
        for line in all_answers_text.split('\n'):
            line = line.strip()
            # Extraire la réponse (Vérifié ou Non vérifié)
            if 'vérifié' in line.lower():
                if 'non' in line.lower():
                    answers.append('Non vérifié')
                else:
                    answers.append('Vérifié')
        
        # S'assurer qu'il y a assez de réponses
        while len(answers) < len(verification_questions):
            answers.append('Non vérifié')
        
        # Créer les étapes de vérification avec un format plus clair
        for i, q in enumerate(verification_questions):
            answer = answers[i] if i < len(answers) else 'Non vérifié'
            step = VerificationStep(question=q, answer=answer)
            verification_steps.append(step)
            # Format plus clair pour l'affichage
            verification_results.append(f"Question {i+1}: {q}\nRéponse: {answer}\n")
        
        # Étape 2: Évaluation finale simplifiée
        # Calculer le pourcentage de vérification
        verified_count = sum(1 for step in verification_steps if step.answer == "Vérifié")
        total_questions = len(verification_steps)
        verification_percentage = (verified_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Déterminer le statut de vérification
        verification_status = "Vérifié" if verification_percentage >= 66 and not has_uncertainty else "Non vérifié"
        
        # Générer une réponse finale qui corrige si nécessaire
        if verification_status == "Vérifié":
            final_response = initial_response  # Garder la réponse initiale si elle est vérifiée
        else:
            # Vérifier si la réponse initiale indique déjà l'incertitude
            if any(indicator in initial_response.lower() for indicator in ["je ne suis pas certain", "je ne peux pas confirmer", "je ne sais pas", "incertain"]):
                final_response = "Je ne peux pas donner une réponse certaine à cette question."
            else:
                # Demander une correction si la réponse n'est pas vérifiée
                correction_prompt = f"""Question: {question}
Réponse initiale: {initial_response}
Résultats de vérification:
{chr(10).join(verification_results)}

IMPORTANT: Réponds uniquement en français.
IMPORTANT: Si la réponse n'est pas vérifiée ou si tu n'es pas certain, réponds "Je ne peux pas donner une réponse certaine à cette question."
IMPORTANT: Ne donne une réponse spécifique QUE si tu es ABSOLUMENT CERTAIN de la réponse.
IMPORTANT: Si tu as le moindre doute, réponds "Je ne peux pas donner une réponse certaine à cette question."
IMPORTANT: Format: Une seule phrase simple.
IMPORTANT: Ne pas utiliser d'anglais."""
                
                final_response = self._call_ollama(correction_prompt, f"correction_{question}")
                
                # Nettoyer la réponse finale
                final_response = final_response.strip()
                if any(word in final_response.lower() for word in ['is', 'the', 'and', 'while', 'therefore']):
                    final_response = "Je ne peux pas donner une réponse certaine à cette question."
                
                # S'assurer que si la réponse n'est pas vérifiée, on ne donne pas de réponse spécifique
                if verification_percentage < 66:
                    final_response = "Je ne peux pas donner une réponse certaine à cette question."
        
        return {
            "initial_response": initial_response.strip(),
            "verification_steps": [step.dict() for step in verification_steps],
            "verification_results": "\n".join(verification_results),
            "final_response": final_response,
            "verification_status": verification_status,
            "verification_percentage": verification_percentage
        } 