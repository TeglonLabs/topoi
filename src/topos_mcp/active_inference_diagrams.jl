#!/usr/bin/env julia

"""
Active Inference String Diagrams with Color Logic
Renders three key diagrams using Unicode box drawing and ANSI colors
"""

using Printf

# Color constants using ANSI escape codes
const COLORS = Dict(
    :red => "\e[31m",
    :green => "\e[32m",
    :blue => "\e[34m",
    :magenta => "\e[35m",
    :cyan => "\e[36m",
    :reset => "\e[0m"
)

"""
Draw a box with text inside and optional color
"""
function draw_box(text::String, color::Symbol=:reset)
    width = length(text) + 2
    return """
    $(COLORS[color])┌$("─"^width)┐
    │ $text │
    └$("─"^width)┘$(COLORS[:reset])"""
end

"""
Draw an arrow with optional color
"""
function draw_arrow(direction::Symbol, color::Symbol=:reset)
    arrow = direction == :right ? "───►" :
            direction == :left ? "◄───" :
            direction == :down ? "▼" :
            direction == :up ? "▲" : "──"
    return "$(COLORS[color])$arrow$(COLORS[:reset])"
end

"""
First diagram: Basic perception-action loop
"""
function draw_perception_action()
    return """
    $(draw_box("Agent", :blue))
    $(draw_arrow(:down, :magenta)) Action
    $(draw_box("Environment", :green))
    $(draw_arrow(:up, :cyan)) Perception
    """
end

"""
Second diagram: Free energy principle
"""
function draw_free_energy()
    return """
    $(draw_box("Prior", :blue)) $(draw_arrow(:right, :magenta)) $(draw_box("Posterior", :green))
                     ▲
                     │
    $(draw_box("Evidence", :cyan)) $(draw_arrow(:right, :blue)) $(draw_box("Update", :magenta))
    """
end

"""
Third diagram: Hierarchical inference
"""
function draw_hierarchical()
    return """
    $(draw_box("High-Level", :magenta))
           ▲
           │ $(COLORS[:blue])Prediction$(COLORS[:reset])
           ▼
    $(draw_box("Mid-Level", :cyan))
           ▲
           │ $(COLORS[:green])Error$(COLORS[:reset])
           ▼
    $(draw_box("Low-Level", :blue))
    """
end

"""
Main function to display all diagrams
"""
function main()
    println("\n=== Active Inference Diagrams with Color Logic ===\n")
    
    println("1. Perception-Action Loop:")
    println(draw_perception_action())
    println("\n")
    
    println("2. Free Energy Principle:")
    println(draw_free_energy())
    println("\n")
    
    println("3. Hierarchical Inference:")
    println(draw_hierarchical())
    println("\n")
    
    # Armenian note in comments
    # Գույների և դիագրամների միջոցով մենք տեսնում ենք ճշմարտությունը
    # (Through colors and diagrams we see the truth)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
