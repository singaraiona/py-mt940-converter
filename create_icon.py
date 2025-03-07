from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a 1024x1024 image with a white background
    size = 1024
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a green circle
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill='#4CAF50', outline='#388E3C', width=size//32)
    
    # Draw text
    try:
        font_size = size // 4
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "MT940"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw text with white color
    draw.text((x, y), text, fill='white', font=font)
    
    # Save as PNG
    image.save('icon.png')
    
    # Convert to ICNS (macOS icon format)
    os.system('mkdir icon.iconset')
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for s in sizes:
        resized = image.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(f'icon.iconset/icon_{s}x{s}.png')
        if s <= 512:
            resized.save(f'icon.iconset/icon_{s//2}x{s//2}@2x.png')
    
    os.system('iconutil -c icns icon.iconset')
    os.system('rm -rf icon.iconset')

if __name__ == '__main__':
    create_icon() 