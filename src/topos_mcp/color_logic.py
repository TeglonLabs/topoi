"""
Color Logic implementation for the entropy tensor visualization.
Based on concepts from color-logic.io
"""
from dataclasses import dataclass
from typing import TypeVar, Generic, Tuple
import numpy as np
from rich.color import Color as RichColor

# Type variables for our dependent type system
T = TypeVar('T')
U = TypeVar('U')

@dataclass
class Color(Generic[T]):
    """A color in our type system"""
    hue: float        # 0-360
    saturation: float # 0-1
    lightness: float  # 0-1
    
    def to_rich_color(self) -> RichColor:
        """Convert to rich's color format for display"""
        # Convert HSL to RGB (simplified)
        h, s, l = self.hue/360, self.saturation, self.lightness
        
        def hue_to_rgb(p: float, q: float, t: float) -> float:
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p
            
        if s == 0:
            r = g = b = l
        else:
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
            
        return RichColor.from_rgb(
            int(r * 255),
            int(g * 255),
            int(b * 255)
        )

class ColorLogic:
    """Implementation of color-logic.io concepts"""
    
    @staticmethod
    def mix(c1: Color[T], c2: Color[U]) -> Color[Tuple[T, U]]:
        """Mix two colors (type intersection)"""
        return Color(
            hue=(c1.hue + c2.hue) / 2,
            saturation=(c1.saturation + c2.saturation) / 2,
            lightness=(c1.lightness + c2.lightness) / 2
        )
    
    @staticmethod
    def complement(c: Color[T]) -> Color[T]:
        """Get complementary color"""
        return Color(
            hue=(c.hue + 180) % 360,
            saturation=c.saturation,
            lightness=c.lightness
        )

def entropy_to_color(entropy: float, axis_position: Tuple[int, int, int]) -> Color[float]:
    """Map entropy value and tensor position to a color"""
    # Abstraction axis affects temperature (hue)
    hue = 240 - (axis_position[0] * 120)  # Blue -> Red
    
    # Interaction axis affects saturation
    saturation = 0.3 + (axis_position[1] * 0.3)
    
    # Entropy axis and value affect lightness
    lightness = 0.2 + (axis_position[2] * 0.2) + (entropy * 0.3)
    
    return Color(
        hue=hue,
        saturation=saturation,
        lightness=lightness
    )

def get_harmony_colors(base_color: Color[T], n: int = 3) -> list[Color[T]]:
    """Generate n harmonious colors based on color theory"""
    colors = [base_color]
    
    # Add complementary and split complementary colors
    angle = 180 / (n-1)
    for i in range(1, n):
        colors.append(Color(
            hue=(base_color.hue + (angle * i)) % 360,
            saturation=base_color.saturation,
            lightness=base_color.lightness
        ))
    
    return colors

# Armenian note:
# Գույների ներդաշնակությունը մեր տեսության հիմքն է
# (Color harmony is the foundation of our theory)
