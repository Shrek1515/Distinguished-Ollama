import requests

def load_list(liste: str, model: str):

    response = requests.post("http://localhost:11434/api/loadlist",
                             json={
                                 "model":model,
                                 "list":liste
                             }
    )
    if response.status_code != 200:
        raise Exception(f"Erreur Ollama: {response.text}")

def add_word(word: str):

    response = requests.post("http://localhost:11434/api/addword",
                             json={
                                "word": word
                             }
                             )
    if response.status_code != 200:
        raise Exception(f"Erreur Ollama: {response.text}")

def remove_word(word: str):

    response = requests.post("http://localhost:11434/api/removeword",
                             json={
                                "word": word
                             }
                             )
    if response.status_code != 200:
        raise Exception(f"Erreur Ollama: {response.text}")