package util

import (
	// "bytes"
	"log"
	"os/exec"
	// "strings"
)

func Pvesh_get(url string) any {
	// var out bytes.Buffer;

    cmd := exec.Command("pvesh", "get", url, "--output-format", "json")
    out, err := cmd.Output()
    if err != nil {
        log.Fatal("Error Byte : ", err)
    }

    result := ParseJSON_Byte(out)

    return result
}