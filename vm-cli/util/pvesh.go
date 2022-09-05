package util

import (
	"bytes"
	"log"
	"os/exec"
	"strings"
)

func Pvesh_get(url string) []map[string]interface{} {
	var out bytes.Buffer

    cmd := exec.Command("pvesh", "get", url, "--output-format", "json")
    cmd.Stdin = strings.NewReader("a")
    cmd.Stdout = &out
    err := cmd.Run()
    if err != nil {
        log.Fatal(err)
    }

    result := ParseJSON(out)

    return result
}