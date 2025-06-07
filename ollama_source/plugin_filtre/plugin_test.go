package plugin_filtre

import (
	"bufio"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/ollama/ollama/api"
	"github.com/ollama/ollama/discover"
	"github.com/ollama/ollama/fs/ggml"
	"github.com/ollama/ollama/llm"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
)

func createTestContext() *gin.Context {
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest("GET", "/?prompt=hello", nil)
	return c
}

func TestTokenizeList(t *testing.T) {

	gpus := discover.GpuInfoList{}
	model := "mistral"
	ggml := &ggml.GGML{}
	adapters := []string{}
	projectors := []string{}
	opts := api.Options{}
	p := NewPluginManager()

	runner, err := llm.NewLlamaServer(gpus, model, ggml, adapters, projectors, opts, 1)
	if err != nil {
		t.Fatalf("Échec de la création du runner : %v", err)
	}

	ctx := createTestContext()
	TokenizeList(p, runner, ctx, model)

	fichier, err := os.Open("ressources/tokens" + model + ".txt")
	if err != nil {
		t.Errorf("La liste n'a pas été tokenizée : %v", err)
	}
	defer fichier.Close()

}

func TestLoadList(t *testing.T) {

	name := "listofwords.txt"

	fichier_tok, err := os.Create(name)
	if err != nil {
		t.Errorf("Failed to create file: %v", err)
	}
	defer fichier_tok.Close()

	p := PluginManager{}
	ans := LoadList(name, &p)
	if ans != 0 {
		t.Errorf("LoadList(\"%v\") = %d; want 0", name, ans)
	}

}

func TestAddWord(t *testing.T) {

	name := "listofwords.txt"

	fichier_tok, err := os.Create(name)
	if err != nil {
		t.Errorf("Failed to create file: %v", err)
	}
	defer fichier_tok.Close()

	writer := bufio.NewWriter(fichier_tok)
	for i := range 5 {
		writer.WriteString(fmt.Sprintf("mot%d", i) + "\n")
	}
	writer.Flush()

	p := PluginManager{}
	ans := LoadList(name, &p)
	if ans != 0 {
		t.Errorf("LoadList(\"%v\") = %d; want 0", name, ans)
	}

	err = AddWord(&p, "mot_test")
	if err != nil {
		t.Errorf("AddWord(\"mot_test\") = %v; want nil", err)
	}

	fichier_tok, err = os.Open(name)
	if err != nil {
		t.Errorf("Failed to open file: %v", err)
	}
	defer fichier_tok.Close()

	scanner := bufio.NewScanner(fichier_tok)
	verif := false
	for scanner.Scan() {
		line := scanner.Text()
		if line == "mot_test" {
			verif = true
			break
		}
	}
	if !verif {
		t.Errorf("LoadList(\"mot_test\") = %v; want true", verif)
	}

}

func TestRemoveWord(t *testing.T) {

	name := "listofwords.txt"

	fichier_tok, err := os.Create(name)
	if err != nil {
		t.Errorf("Failed to create file: %v", err)
	}
	defer fichier_tok.Close()

	writer := bufio.NewWriter(fichier_tok)
	for i := range 5 {
		writer.WriteString(fmt.Sprintf("mot%d", i) + "\n")
	}
	writer.WriteString("mot_test\n")
	writer.Flush()

	p := PluginManager{}
	ans := LoadList(name, &p)
	if ans != 0 {
		t.Errorf("LoadList(\"%v\") = %d; want 0", name, ans)
	}

	err = RemoveWord(&p, "mot_test")
	if err != nil {
		t.Errorf("AddWord(\"mot_test\") = %v; want nil", err)
	}

	fichier_tok, err = os.Open(name)
	if err != nil {
		t.Errorf("Failed to open file: %v", err)
	}
	defer fichier_tok.Close()

	scanner := bufio.NewScanner(fichier_tok)
	verif := false
	for scanner.Scan() {
		line := scanner.Text()
		if line == "mot_test" {
			verif = true
			break
		}
	}
	if verif {
		t.Errorf("LoadList(\"mot_test\") = %v; want false", verif)
	}

}

func TestRemoveAsterisks(t *testing.T) {

	str := "**test**"
	ans := RemoveAsterisks(str)
	boolean := strings.Contains(ans, "*")
	if boolean {
		t.Errorf("RemoveAsterisks(\"%v\") = %v; want \"test\"", str, ans)
	}

}

func TestLevenshtein(t *testing.T) {
	ans := Levenshtein("oui", "oui")
	if ans != 0 {
		t.Errorf("Levenshtein(\"oui\",\"oui\") = %d; want 0", ans)
	}

}

func TestLevenshtein2(t *testing.T) {
	ans := Levenshtein("oui", "non")
	if ans == 0 {
		t.Errorf("Levenshtein(\"oui\",\"non\") = %d; want 3", ans)
	}

}

func TestFuzzyLevenshtein(t *testing.T) {

	mot := "mot_test"

	name := "listofwords.txt"

	fichier_tok, err := os.Create(name)
	if err != nil {
		t.Errorf("Failed to create file: %v", err)
	}
	defer fichier_tok.Close()

	writer := bufio.NewWriter(fichier_tok)
	for i := range 5 {
		writer.WriteString(fmt.Sprintf("mot%d", i) + "\n")
	}
	writer.WriteString("mot_test\n")
	writer.Flush()

	p := PluginManager{}
	ans := LoadList(name, &p)
	if ans != 0 {
		t.Errorf("LoadList(\"%v\") = %d; want 0", name, ans)
	}

	str, e := FuzzyLevenshtein(&p, mot)
	if e != nil {
		t.Errorf("Erreur lors du test de FuzzyLevenshtein: %v", e)
	}
	if !strings.Contains(str, "censuré") {
		t.Errorf("FuzzeLevenshtein(&p, \"mot_test\") = %v; want censuré (...)", str)
	}

}

func TestFuzzyLevenshteinText(t *testing.T) {

	mot := "mot_test aa bb cc dd ee ff gg hh ii jj kk ll ll mm nn"

	name := "listofwords.txt"

	fichier_tok, err := os.Create(name)
	if err != nil {
		t.Errorf("Failed to create file: %v", err)
	}
	defer fichier_tok.Close()

	writer := bufio.NewWriter(fichier_tok)
	for i := range 5 {
		writer.WriteString(fmt.Sprintf("mot%d", i) + "\n")
	}
	writer.WriteString("mot_test\n")
	writer.Flush()

	p := PluginManager{}
	ans := LoadList(name, &p)
	if ans != 0 {
		t.Errorf("LoadList(\"%v\") = %d; want 0", name, ans)
	}

	str, e := FuzzyLevenshteinText(&p, mot)
	if e != nil {
		t.Errorf("Erreur lors du test de FuzzyLevenshtein: %v", e)
	}
	if !strings.Contains(str, "censuré") {
		t.Errorf("FuzzeLevenshtein(&p, \"mot_test\") = %v; want censuré (...)", str)
	}
}
