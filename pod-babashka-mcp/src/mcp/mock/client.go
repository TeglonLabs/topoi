package mock

import (
	"encoding/json"
	"fmt"
)

// MockClient implements a test version of the MCP client
type MockClient struct {
	Connected bool
}

type Message struct {
	Method string          `json:"method"`
	Params json.RawMessage `json:"params"`
}

func (c *MockClient) Connect() error {
	c.Connected = true
	return nil
}

func (c *MockClient) Disconnect() error {
	c.Connected = false
	return nil
}

func (c *MockClient) SendMessage(msg []byte) error {
	if !c.Connected {
		return fmt.Errorf("not connected")
	}
	return nil
}

func (c *MockClient) ReadMessage() ([]byte, error) {
	if !c.Connected {
		return nil, fmt.Errorf("not connected")
	}
	return []byte(`{"result": {"status": "ok"}}`), nil
}

func NewMockClient() *MockClient {
	return &MockClient{}
}
