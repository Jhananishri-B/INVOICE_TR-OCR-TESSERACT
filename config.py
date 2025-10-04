import os

# Tesseract configuration
TESSERACT_CONFIGS = {
    'printed': '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$/-()@& ',
    'handwritten': '--psm 8 --oem 3',
    'auto': '--psm 6 --oem 3',
    'single_line': '--psm 8 --oem 3',
    'single_word': '--psm 13 --oem 3'
}

# TR-OCR model names
TROCR_MODELS = {
    'printed': 'microsoft/trocr-base-printed',
    'handwritten': 'microsoft/trocr-base-handwritten'
}

# Image preprocessing settings
PREPROCESS_SETTINGS = {
    'min_width': 512,
    'min_height': 512,
    'max_width': 2048,
    'max_height': 2048,
    'target_dpi': 300
}

# Set Tesseract path (Windows - update this path after installation)
TESSERACT_PATHS = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Default installation path
    r'C:\Users\JHANANISHRI\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
]