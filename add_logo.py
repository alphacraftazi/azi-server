from PIL import Image
import os

def add_logo(base_image_path, logo_path, output_path, scale_percent=15, padding=30):
    try:
        # Open the images
        base_image = Image.open(base_image_path).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")

        # Calculate new logo size
        base_width, base_height = base_image.size
        logo_width, logo_height = logo.size

        # Scale logo to be scale_percent of the base image width
        new_logo_width = int(base_width * (scale_percent / 100))
        aspect_ratio = logo_height / logo_width
        new_logo_height = int(new_logo_width * aspect_ratio)

        logo = logo.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)

        # Calculate position (Top Right)
        x_position = base_width - new_logo_width - padding
        y_position = padding

        # Create a transparent layer for the logo
        transparent_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        transparent_layer.paste(logo, (x_position, y_position), mask=logo)

        # Composite the images
        final_image = Image.alpha_composite(base_image, transparent_layer)

        # Save the result
        final_image.save(output_path, format="PNG")
        print(f"Success: Image saved to {output_path}")

    except Exception as e:
        print(f"Error: {e}")

# Paths
base_dir = r"C:\Users\alpay\.gemini\antigravity\brain\f22e87e4-7ff6-4c52-9680-f3881ca466f0"
base_img = os.path.join(base_dir, "post1_general_automation_1769804218939.png")
logo_img = os.path.join(base_dir, "uploaded_media_1769804178537.png")
output_img = os.path.join(base_dir, "post1_with_logo.png")

add_logo(base_img, logo_img, output_img)
