package plugin_filtre

import (
	"bufio"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/ollama/ollama/llm"
	"os"
	"strings"
)

// Le PLuginManager est responsable de la gestion de la liste dans le serveur,
// c'est là que l'on stocke le chemin de la liste, et que l'on gère le moment où elle doit être tokenisée.
type PluginManager struct {
	List  string // Le chemin de la liste de mots à bannir.
	Reset bool   // Un booléen consulté dans la fonction tokenize pour savoir s'il faut tokenizer la liste ou pas.
}

// Permet d'initialiser un PluginManager
func NewPluginManager() *PluginManager {
	var p PluginManager // Le PluginManager.
	p.List = ""         // Le chemin de la liste, vide car elle n'est pas renseignée ici.
	p.Reset = false     // Le booléen pour controller la tokenisation de la liste.

	return &p
}

// Lit la liste de mots dans son fichier .txt et tokenise son contenu, puis stoque les tokens générés dans un nouveau fichier .txt.
// Paramètres :
// p un pointeur vers un PluginManager.
// runner de type LlamaServer, sert à appeler la méthode Tokenize().
// ctx un pointeur de type gin.Context sert aussi pour la méthode Tokenize().
// model une chaîne de caractère représentant le modèle de langage utilisé pour la tokenisation.
func TokenizeList(p *PluginManager, runner llm.LlamaServer, ctx *gin.Context, model string) int {

	fichier, err := os.Open("ressources/tokens" + model + ".txt")
	if err == nil {
		if p.Reset == false {
			return 0
		}
	}
	defer fichier.Close()

	file, err := os.Open(p.List)
	if err != nil {
		return -1
	}
	defer file.Close()

	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		lines = append(lines, line)
	}

	fichier_tok, err := os.Create("ressources/tokens" + model + ".txt")
	if err != nil {
		return -1
	}
	defer fichier_tok.Close()

	writer := bufio.NewWriter(fichier_tok)
	tokens, err2 := runner.Tokenize(ctx.Request.Context(), strings.Join(lines, " "))

	if err2 != nil {
		return -1
	} else {
		for _, token := range tokens {
			writer.WriteString(fmt.Sprintf("%d", token) + "\n")
		}
	}
	writer.Flush()

	return 0

}

// Permet de renseigner une liste au PluginManager
// Paramètres :
// list de type string, représente le chemin vers la liste de mots bannis.
// p un pointeur de PluginManager qui accueillera la nouvelle liste.
func LoadList(list string, p *PluginManager) int8 {

	fi, err := os.Open(list)
	if err != nil {
		return -1
	}
	defer fi.Close()

	p.List = list
	return 0

}

// Permet d'ajouter un mot à la liste.
// Paramètres :
// p un pointeur de PluginManager, là où se trouve le chemin de la liste à modifier.
// word une chaîne de caractères représentant le mot à ajouter.
func AddWord(p *PluginManager, word string) error {

	fichier, err := os.Open(p.List)
	if err != nil {
		return err
	}
	defer fichier.Close()

	scanner := bufio.NewScanner(fichier)
	for scanner.Scan() {
		line := scanner.Text()
		if line == word {
			return nil
		}
	}

	if err := scanner.Err(); err != nil {
		return err
	}

	fichier, err = os.OpenFile(p.List, os.O_APPEND|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer fichier.Close()

	writer := bufio.NewWriter(fichier)
	writer.WriteString(word + "\n")
	writer.Flush()

	p.Reset = true

	return nil
}

// Permet de supprimer un mot de la liste.
// Paramètres :
// p un pointeur de PluginManager, là où se trouve le chemin de la liste à modifier.
// word une chaîne de caractères représentant le mot à supprimer.
func RemoveWord(p *PluginManager, word string) error {

	if p == nil {
	}
	file, err := os.Open(p.List)
	if err != nil {
		return err
	}
	defer file.Close()

	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		if line != word {
			lines = append(lines, line)
		}
	}

	if err := scanner.Err(); err != nil {
		return err
	}

	file, err = os.Create(p.List)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	for _, line := range lines {
		writer.WriteString(line + "\n")
	}
	writer.Flush()

	p.Reset = true

	//print("suppressed word: " + word)
	return nil

}

// Implémentation de la distance de Levenshtein entre deux mots.
// Retourne le nombre de changements (ajouts/suppressions/permutations) à faire pour que word2 soit égal à word2.
// Paramètres :
// word1 un string représentant un mot.
// word2 un string représentant le mot dont on cherche la distance avec word1.
func Levenshtein(word1, word2 string) int {

	d := make([][]int, len(word1)+1)
	for i := range d {
		d[i] = make([]int, len(word2)+1)
	}

	for i := 0; i <= len(word1); i++ {
		for j := 0; j <= len(word2); j++ {
			if i == 0 {
				d[i][j] = j
			} else {
				if j == 0 {
					d[i][j] = i
				} else {
					if word1[i-1] == word2[j-1] {
						d[i][j] = d[i-1][j-1]
					} else {
						d[i][j] = min(d[i-1][j], d[i][j-1], d[i-1][j-1]) + 1
					}
				}
			}
		}
	}

	return d[len(word1)][len(word2)]

}

// Recherche et destruction d'un mot s'il se trouve dans une liste, basé sur Levenshtein.
// Retourne le mot censuré s'il est dans la liste, retourne juste le mot sinon.
// Paramètres :
// p un pointeur de PluginManager, là où se trouve le chemin de la liste à regarder.
// word1 un string représentant le mot à analyser.
func FuzzyLevenshtein(p *PluginManager, word1 string) (string, error) {

	file, err := os.Open(p.List)
	if err != nil {
		return word1, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	tmp := RemoveAsterisks(word1)
	for scanner.Scan() {
		line := scanner.Text()
		if Levenshtein(line, tmp) <= 2 {
			return "censuré (" + tmp + ")", nil
		}
	}

	return word1, nil
}

// Permet de supprimer les asterisques dans une chaîne de caractères.
func RemoveAsterisks(word string) string {
	mot := word
	if strings.Contains(word, "*") {
		mot = strings.Replace(mot, "*", "", -1)
	}

	if strings.Contains(mot, "\"") {
		mot = strings.Replace(mot, "\"", "", -1)
	}

	return mot
}

// Recherche et destruction de mots dans un texte s'ils se trouvent dans une liste, basé sur Levenshtein.
// Retourne le texte censuré/non censuré si aucun mot ne doit l'être.
// Paramètres :
// p un pointeur de PluginManager, là où se trouve le chemin de la liste à regarder.
// text un string représentant le texte à analyser.
func FuzzyLevenshteinText(p *PluginManager, text string) (string, error) {

	list_word := strings.Split(text, " ")

	file, err := os.Open(p.List)
	if err != nil {
		return text, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		for i := range len(list_word) {
			tmp := RemoveAsterisks(list_word[i])
			if Levenshtein(line, tmp) <= 1 {
				list_word[i] = "censuré (" + tmp + ")"
			}
		}
	}

	return strings.Join(list_word, " "), nil

}
