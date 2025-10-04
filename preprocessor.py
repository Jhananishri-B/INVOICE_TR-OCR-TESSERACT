import cv2
import numpy as np
from PIL import Image, ImageEnhance
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImagePreprocessor:
    def __init__(self):
        self.min_width = 512
        self.min_height = 512
        self.max_width = 2048
        self.max_height = 2048
    
    def load_image(self, image_path):
        """Load image from path"""
        try:
            if isinstance(image_path, str):
                image = Image.open(image_path).convert('RGB')
            else:
                image = image_path.convert('RGB')
            return np.array(image)
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise
    
    def resize_image(self, image, target_size=None):
        """Resize image while maintaining aspect ratio"""
        if target_size is None:
            target_size = (1024, 1024)
            
        h, w = image.shape[:2]
        
        # Don't resize if within acceptable range
        if (self.min_width <= w <= self.max_width and 
            self.min_height <= h <= self.max_height):
            return image
        
        # Calculate scaling factors
        scale_x = target_size[0] / w
        scale_y = target_size[1] / h
        scale = min(scale_x, scale_y)
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        logger.info(f"Resized image from {w}x{h} to {new_w}x{new_h}")
        return resized
    
    def enhance_contrast(self, image):
        """Enhance image contrast using CLAHE"""
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        else:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(image)
        return enhanced
    
    def remove_noise(self, image):
        """Remove noise while preserving text"""
        if len(image.shape) == 3:
            denoised = cv2.fastNlMeansDenoisingColored(
                image, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
            )
        else:
            denoised = cv2.fastNlMeansDenoising(image, h=10, templateWindowSize=7, searchWindowSize=21)
        return denoised
    
    def sharpen_image(self, image):
        """Sharpen image to enhance text edges"""
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened
    
    def binarize_image(self, image, method='adaptive'):
        """Convert image to binary for better OCR"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        if method == 'adaptive':
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
        else:  # otsu
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def preprocess_for_tesseract(self, image_path):
        """Preprocessing optimized for Tesseract"""
        image = self.load_image(image_path)
        
        # Resize if needed
        image = self.resize_image(image)
        
        # Enhance contrast
        image = self.enhance_contrast(image)
        
        # Remove noise
        image = self.remove_noise(image)
        
        # Sharpen
        image = self.sharpen_image(image)
        
        # Convert to binary
        binary_image = self.binarize_image(image, method='adaptive')
        
        return Image.fromarray(binary_image)
    
    def preprocess_for_trocr(self, image_path):
        """Preprocessing optimized for TR-OCR"""
        image = self.load_image(image_path)
        
        # Resize if needed
        image = self.resize_image(image)
        
        # Enhance contrast
        image = self.enhance_contrast(image)
        
        # Remove noise
        image = self.remove_noise(image)
        
        return Image.fromarray(image)