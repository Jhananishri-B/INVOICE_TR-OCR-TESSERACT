import os
import sys
import subprocess

def install_tesseract_windows():
    """Install Tesseract OCR on Windows"""
    print("Installing Tesseract OCR for Windows...")
    
    try:
        # Try to install via pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytesseract"])
        print("✓ pytesseract installed successfully")
        
        # Download Tesseract installer
        download_url = "https://github.com/UB-Mannheim/tesseract/wiki"
        
        print("Please download and install Tesseract OCR manually:")
        print(f"1. Go to: {download_url}")
        print("2. Download the Windows installer (tesseract-ocr-w64-setup-5.3.3.20231005.exe)")
        print("3. Run the installer")
        print("4. Add Tesseract to your PATH")
        print("\nAfter installation, update the path in config.py if needed")
        
        return True
        
    except Exception as e:
        print(f"Error installing Tesseract: {e}")
        return False

def check_tesseract_installation():
    """Check if Tesseract is properly installed"""
    try:
        import pytesseract
        # Try to get version
        try:
            version = subprocess.check_output(['tesseract', '--version'], 
                                            stderr=subprocess.STDOUT, 
                                            text=True)
            print(f"✓ Tesseract found: {version.splitlines()[0]}")
            return True
        except:
            print("⚠ Tesseract engine not found in PATH")
            print("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    except ImportError:
        print("✗ pytesseract not installed")
        return False

if __name__ == "__main__":
    print("Tesseract OCR Installation Helper")
    print("=" * 50)
    
    if os.name == 'nt':  # Windows
        install_tesseract_windows()
    else:  # Linux/Mac
        print("For Linux/Mac, install Tesseract using:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  Mac: brew install tesseract")
        print("Then: pip install pytesseract")
    
    check_tesseract_installation()