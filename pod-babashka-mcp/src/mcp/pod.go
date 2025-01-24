package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strconv"

	"github.com/babashka/pod-babashka-mcp/src/mcp/mock"
)

type podRequest struct {
	Op      string          `json:"op"`
	ID      string          `json:"id"`
	Var     string          `json:"var"`
	Args    []interface{}   `json:"args,omitempty"`
	Session json.RawMessage `json:"session,omitempty"`
}

type podResponse struct {
	ID     string      `json:"id"`
	Value  interface{} `json:"value,omitempty"`
	Status []string    `json:"status,omitempty"`
	Error  string      `json:"error,omitempty"`
}

func writeNetstring(data []byte) error {
	length := len(data)
	_, err := fmt.Fprintf(os.Stdout, "%d:%s,", length, data)
	return err
}

func writeResponse(resp podResponse) error {
	bytes, err := json.Marshal(resp)
	if err != nil {
		return err
	}
	return writeNetstring(bytes)
}

func readNetstring() ([]byte, error) {
	// Read until we find a colon
	var lengthBytes []byte
	for {
		b := make([]byte, 1)
		_, err := os.Stdin.Read(b)
		if err != nil {
			return nil, err
		}
		if b[0] == ':' {
			break
		}
		if b[0] < '0' || b[0] > '9' {
			return nil, fmt.Errorf("invalid length character: %c", b[0])
		}
		lengthBytes = append(lengthBytes, b[0])
	}

	// Parse length
	length, err := strconv.Atoi(string(lengthBytes))
	if err != nil {
		return nil, fmt.Errorf("invalid length: %s", err)
	}

	// Read exactly length bytes
	data := make([]byte, length)
	n, err := io.ReadFull(os.Stdin, data)
	if err != nil {
		return nil, fmt.Errorf("error reading data: %s (read %d of %d bytes)", err, n, length)
	}

	// Read trailing comma
	b := make([]byte, 1)
	_, err = os.Stdin.Read(b)
	if err != nil {
		return nil, fmt.Errorf("error reading comma: %s", err)
	}
	if b[0] != ',' {
		return nil, fmt.Errorf("expected comma, got %c", b[0])
	}

	return data, nil
}

func handleDescribe() error {
	resp := podResponse{
		ID: "describe",
		Value: map[string]interface{}{
			"format": "json",
			"namespaces": []map[string]interface{}{
				{
					"name": "pod.babashka.mcp",
					"vars": []map[string]interface{}{
						{
							"name": "connect",
							"code": "(defn connect [opts] ...)",
						},
						{
							"name": "disconnect",
							"code": "(defn disconnect [session] ...)",
						},
						{
							"name": "list-tools",
							"code": "(defn list-tools [session] ...)",
						},
						{
							"name": "call-tool",
							"code": "(defn call-tool [session name args] ...)",
						},
						{
							"name": "subscribe",
							"code": "(defn subscribe [session uri callback] ...)",
						},
					},
				},
			},
		},
	}
	return writeResponse(resp)
}

func handleConnect(args []interface{}) (interface{}, error) {
	if len(args) != 1 {
		return nil, fmt.Errorf("connect expects 1 argument, got %d", len(args))
	}

	_, ok := args[0].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("connect expects a map argument")
	}

	client := mock.NewMockClient()
	err := client.Connect()
	if err != nil {
		return nil, err
	}

	return client, nil
}

func handleRequest(req podRequest) error {
	switch req.Op {
	case "describe":
		return handleDescribe()

	case "invoke":
		var result interface{}
		var err error

		switch req.Var {
		case "pod.babashka.mcp/connect":
			result, err = handleConnect(req.Args)
		default:
			err = fmt.Errorf("unknown var: %s", req.Var)
		}

		if err != nil {
			return writeResponse(podResponse{
				ID:    req.ID,
				Error: err.Error(),
			})
		}

		return writeResponse(podResponse{
			ID:    req.ID,
			Value: result,
		})

	default:
		return fmt.Errorf("unknown op: %s", req.Op)
	}
}

func main() {
	// Write initial describe response
	if err := handleDescribe(); err != nil {
		fmt.Fprintf(os.Stderr, "Error writing describe response: %v\n", err)
		os.Exit(1)
	}

	// Flush stdout to ensure describe response is sent
	if err := os.Stdout.Sync(); err != nil {
		fmt.Fprintf(os.Stderr, "Error flushing stdout: %v\n", err)
		os.Exit(1)
	}

	// Handle subsequent requests
	for {
		data, err := readNetstring()
		if err != nil {
			if err == io.EOF {
				break
			}
			fmt.Fprintf(os.Stderr, "Error reading request: %v\n", err)
			os.Exit(1)
		}

		var req podRequest
		if err := json.Unmarshal(data, &req); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing request: %v\n", err)
			os.Exit(1)
		}

		if err := handleRequest(req); err != nil {
			fmt.Fprintf(os.Stderr, "Error handling request: %v\n", err)
			os.Exit(1)
		}

		// Flush stdout after each response
		if err := os.Stdout.Sync(); err != nil {
			fmt.Fprintf(os.Stderr, "Error flushing stdout: %v\n", err)
			os.Exit(1)
		}
	}
}
