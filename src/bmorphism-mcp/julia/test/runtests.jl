using Test
using JSON
using BmorphismMcp

@testset "BmorphismMcp.jl" begin
    @testset "Bridge Creation" begin
        bridge = create_bridge(:lisp, :python)
        @test bridge.source_lang == :lisp
        @test bridge.target_lang == :python
        @test bridge.parser isa LispParser
    end

    @testset "Lisp Parsing" begin
        parser = LispParser(:lisp)
        ast = parse_lisp(parser, "(+ 1 2)")
        @test !isnothing(ast)
        
        # Test invalid expression
        ast_invalid = parse_lisp(parser, "(+ 1 2")
        @test isnothing(ast_invalid)
    end

    @testset "Expression Mapping" begin
        bridge = create_bridge(:lisp, :python)
        result = handle_transform(bridge, "(+ 1 2)")
        @test result["status"] == "success"
        @test haskey(result, "ast")
        @test haskey(result, "mapping_id")
        
        # Verify mapping structure
        mapping = bridge.mapping
        @test nv(mapping, :Language) == 3  # Initial languages
        @test nv(mapping, :Expression) == 1  # One expression added
        @test nv(mapping, :AST) == 1  # One AST node
    end
end

@testset "MCP Protocol" begin
    include("../src/server.jl")  # Load server implementation
    
    @testset "Create Bridge" begin
        msg = JSON.json(Dict(
            "method" => "create_bridge",
            "params" => Dict(
                "source_lang" => "lisp",
                "target_lang" => "python"
            )
        ))
        
        response = JSON.parse(handle_message(msg))
        @test response["status"] == "success"
        @test haskey(response, "bridge_id")
        bridge_id = response["bridge_id"]
        
        # Test transform using created bridge
        transform_msg = JSON.json(Dict(
            "method" => "transform",
            "params" => Dict(
                "bridge_id" => bridge_id,
                "expression" => "(+ 1 2)"
            )
        ))
        
        transform_response = JSON.parse(handle_message(transform_msg))
        @test transform_response["status"] == "success"
        @test haskey(transform_response, "ast")
    end
    
    @testset "Error Handling" begin
        # Test invalid method
        msg = JSON.json(Dict(
            "method" => "invalid_method"
        ))
        response = JSON.parse(handle_message(msg))
        @test response["status"] == "error"
        
        # Test invalid bridge ID
        msg = JSON.json(Dict(
            "method" => "transform",
            "params" => Dict(
                "bridge_id" => "nonexistent",
                "expression" => "(+ 1 2)"
            )
        ))
        response = JSON.parse(handle_message(msg))
        @test response["status"] == "error"
        
        # Test invalid JSON
        response = JSON.parse(handle_message("invalid json"))
        @test response["status"] == "error"
    end
end
