# MCP Server Configuration Patterns

## EDN to JSON Translation

1. Key Mapping
```clojure
;; EDN (pod-config.edn)
{:mcp-servers {"example-server"
               {:command "python"
                :args ["server.py"]
                :env {"DEBUG" "1"}
                :disabled false
                :auto-approve []}}

;; JSON (cline_mcp_settings.json)
{
  "mcpServers": {
    "example-server": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "DEBUG": "1"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

2. Configuration Structure
- Use kebab-case in EDN
- Use camelCase in JSON
- Maintain consistent key names
- Preserve value types

## Common Patterns

1. Server Configuration
```clojure
{:command "node"              ; Command to execute
 :args ["/path/to/server.js"] ; Command arguments
 :env {"API_KEY" "..."        ; Environment variables
       "DEBUG" "1"}
 :disabled false             ; Server status
 :auto-approve []}          ; Auto-approved tools
```

2. Tool Configuration
```clojure
{:tools [{:name "example_tool"
          :description "Tool description"
          :input-schema {:type "object"
                        :properties {...}
                        :required [...]}}]}
```

3. Resource Configuration
```clojure
{:resources [{:uri "resource://example"
             :name "Example Resource"
             :mime-type "application/json"
             :description "Resource description"}]}
```

## Best Practices

1. Configuration Management
- Store sensitive data in environment variables
- Use relative paths where possible
- Enable/disable servers explicitly
- Document all configuration options

2. Tool Configuration
- Provide clear descriptions
- Define input schemas
- List required parameters
- Include usage examples

3. Resource Configuration
- Use consistent URI schemes
- Specify MIME types
- Include resource metadata
- Document access patterns

4. Security Considerations
- Never commit sensitive data
- Use environment variables
- Enable auto-approve selectively
- Document security implications

## Integration with Babashka

1. Configuration Loading
```clojure
(defn load-config [path]
  (-> (slurp path)
      (edn/read-string)
      (validate-config)
      (transform-keys)))

(defn config->json [config]
  (-> config
      (update-keys camel-case)
      (json/generate-string)))
```

2. Environment Variables
```clojure
(defn resolve-env [config]
  (walk/postwalk
    (fn [x]
      (if (env-var? x)
        (System/getenv (env-var-name x))
        x))
    config))
```

3. Validation
```clojure
(defn validate-server-config [config]
  (when-not (and (:command config)
                 (sequential? (:args config)))
    (throw (ex-info "Invalid server config" 
                   {:config config}))))
```

## Example Configurations

1. Basic Server
```clojure
{:mcp-servers
 {"simple-server"
  {:command "python"
   :args ["server.py"]
   :env {"DEBUG" "1"}
   :disabled false
   :auto-approve []}}}
```

2. Complex Server
```clojure
{:mcp-servers
 {"advanced-server"
  {:command "node"
   :args ["/path/to/server.js"]
   :env {"API_KEY" #env "SERVER_API_KEY"
         "PORT" "8080"
         "HOST" "localhost"}
   :disabled false
   :auto-approve ["safe_tool"]
   :tools [{:name "example_tool"
            :description "Example tool"
            :input-schema {...}}]
   :resources [{:uri "resource://example"
               :name "Example Resource"}]}}}
```

## Migration Guide

1. From JSON to EDN
- Convert camelCase to kebab-case
- Preserve data types
- Validate structure
- Test configuration

2. From EDN to JSON
- Convert kebab-case to camelCase
- Ensure type compatibility
- Validate against schema
- Test integration

## References

1. Example Implementations
- Claude Desktop config
- Cline VSCode config
- Babashka pod configs

2. Documentation
- MCP Protocol Specification
- Babashka Pod Protocol
- Configuration Schemas
