package plugin_filtre

import (
	"bufio"
	"os"
	"strings"
)

func ExpressionsFilter(p *PluginManager, response string) (string, error) {

	file, err := os.Open(p.List)
	if err != nil {
		return "erreur fichier expression filter", err
	}
	defer file.Close()

	var lines []string
	scanner := bufio.NewScanner(file)

	var verif = false
	for scanner.Scan() {

		line := scanner.Text()
		if verif == true {

			lines = append(lines, line)
		}
		if line == "expressions" {
			verif = true
		}
	}

	if err := scanner.Err(); err != nil {
		return "erreur scanner expressionfilter", err
	}

	for _, line := range lines {
		if strings.Contains(response, line) {
			strings.ReplaceAll(response, line, "")
		}
	}

	return response, nil
}
