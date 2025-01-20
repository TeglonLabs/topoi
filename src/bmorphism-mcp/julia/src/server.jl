using .BmorphismMcp
using JSON
using UUIDs

# Global state
const bridges = Dict{String, LanguageBridge}()

function handle_message(msg::String)
    try
        data = JSON.parse(msg)
        method = get(data, "method", "")
        
        if method == "create_bridge"
            params = data["params"]
            source = Symbol(params["source_lang"])
            target = Symbol(params["target_lang"])
            bridge_id = string(uuid4())
            bridges[bridge_id] = create_bridge(source, target)
            return JSON.json(Dict(
                "status" => "success",
                "bridge_id" => bridge_id
            ))
        elseif method == "transform"
            params = data["params"]
            bridge_id = params["bridge_id"]
            expr = params["expression"]
            
            if !haskey(bridges, bridge_id)
                return JSON.json(Dict(
                    "status" => "error",
                    "message" => "Bridge not found"
                ))
            end
            
            bridge = bridges[bridge_id]
            result = handle_transform(bridge, expr)
            return JSON.json(result)
        else
            return JSON.json(Dict(
                "status" => "error",
                "message" => "Unknown method: $method"
            ))
        end
    catch e
        return JSON.json(Dict(
            "status" => "error",
            "message" => "Internal error: $(sprint(showerror, e))"
        ))
    end
end

# MCP Server main loop
function run_server()
    println(stderr, "Julia MCP server starting...")
    
    while !eof(stdin)
        line = readline(stdin)
        if isempty(line)
            continue
        end
        
        response = handle_message(line)
        println(stdout, response)
        flush(stdout)
    end
end

# Start server when run directly
if abspath(PROGRAM_FILE) == @__FILE__
    run_server()
end
