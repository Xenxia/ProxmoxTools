package util

import (
	"bytes"
	"encoding/json"
	"log"
)

func ParseJSON_Buffer(in bytes.Buffer) any {

	var out any
	err := json.Unmarshal(in.Bytes(), &out)

	if err != nil {
		log.Fatal("ParseJSON_Byte error : ", err)
	}

	return out

}

func ParseJSON_Byte(in []byte) any {

	var out any
	err := json.Unmarshal(in, &out)

	if err != nil {
		log.Fatal("ParseJSON_Byte error : ", err)
	}

	return out

}