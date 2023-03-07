package util

import (
	// "bytes"
	"log"
	"os/exec"
	// "strings"
)

func Pvesh_get(url string) (any, bool) {
	// var out bytes.Buffer;

    cmd := exec.Command("pvesh", "get", url, "--output-format", "json")
    out, err := cmd.Output()
    if err != nil {
        log.Fatal("Pvesh_get | Error : ", err)
		return nil, false
    }

    result := ParseJSON_Byte(out)

    return result, true
}

func Pvesh_post(url string, outputType string) (any, bool) {
	// var out bytes.Buffer;

    cmd := exec.Command("pvesh", "create", url, "--output-format", "json")
    out, err := cmd.Output()
    if err != nil {
        log.Fatal("Pvesh_post | Error : ", err)
		return nil, false
    }

    var result any

    if outputType == "string" {
        result = string(out)
    }

    if outputType == "json" {

        result = ParseJSON_Byte(out)

    }

    return result, true
}