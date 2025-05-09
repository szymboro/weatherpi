#!/usr/bin/python3
from PIL import Image, ImageDraw, ImageFont
import os

# Katalog z ikonami
icon_dir = "icons"
os.makedirs(icon_dir, exist_ok=True)

# Funkcja tworząca podstawową ikonę pogodową
def create_icon(name, text, size=(64, 64)):
    image = Image.new('1', size, 255)  # biały
    draw = ImageDraw.Draw(image)
    
    # Dodanie obramowania
    draw.rectangle([(0, 0), (size[0]-1, size[1]-1)], outline=0)
    
    # Dodanie tekstu
    try:
        font = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
        
    # Rysowanie tekstu na środku
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill=0, font=font)
    
    # Zapisanie ikony
    image.save(os.path.join(icon_dir, f"{name}.bmp"))
    print(f"Utworzono ikonę: {name}.bmp")

# Tworzenie podstawowych ikon
icons = {
    'sunny': 'S',
    'partly_sunny': 'PS',
    'partly_cloudy': 'PC',
    'cloudy': 'C',
    'rain': 'R',
    'thunderstorm': 'T',
    'snow': 'SN',
    'fog': 'F',
    'windy': 'W',
    'ice': 'I',
    'sleet': 'SL',
    'hot': 'H',
    'cold': 'CL',
    'clear': 'CL',
    'partly_clear': 'PCL',
    'unknown': '?'
}

for name, symbol in icons.items():
    create_icon(name, symbol)

print("Ukończono tworzenie ikon!")
