package util

import (
	"bytes"
	"encoding/json"
)

func ParseJSON(in bytes.Buffer) []map[string]interface{} {

	var out []map[string]interface{}
	json.Unmarshal(in.Bytes(), &out)

	return out

}