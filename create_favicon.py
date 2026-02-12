
from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon():
    # Create a 64x64 transparent image
    size = (64, 64)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a background circle with the cyan border color style
    # Fill with dark blue/black
    draw.ellipse([2, 2, 62, 62], fill=(5, 5, 16, 255), outline=(34, 211, 238, 255), width=2)

    # Draw the "A" text
    # Since we might not have the exact font, we'll draw a simple polygon for "A" or use a default font
    # Let's draw a stylistic "A" using lines to look like the logo
    
    # "A" coordinates
    # Apex: 32, 12
    # Bottom Left: 14, 52
    # Bottom Right: 50, 52
    # Crossbar Left: 22, 36
    # Crossbar Right: 42, 36
    
    # Draw legs
    draw.line([(32, 12), (14, 52)], fill=(255, 255, 255, 255), width=3)
    draw.line([(32, 12), (50, 52)], fill=(255, 255, 255, 255), width=3)
    
    # Draw crossbar (Cyan glow color)
    draw.line([(20, 38), (44, 38)], fill=(34, 211, 238, 255), width=3)

    output_path = r"c:\Users\alpay\.gemini\antigravity\scratch\alphacraft_website\favicon.png"
    img.save(output_path)
    print(f"Favicon saved to {output_path}")

if __name__ == "__main__":
    create_favicon()
