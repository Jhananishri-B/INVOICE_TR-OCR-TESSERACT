import pytesseract
import cv2
import numpy as np
from PIL import Image
import logging
from config import TESSERACT_CONFIGS, TESSERACT_PATHS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TesseractExtractor:
    def __init__(self):
        self.setup_tesseract()
        logger.info("Tesseract OCR initialized")
    
    def setup_tesseract(self):
        """Setup Tesseract path"""
        for path in TESSERACT_PATHS:
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                # Test the installation
                pytesseract.get_tesseract_version()
                logger.info(f"Tesseract found at: {path}")
                return
            except:
                continue
        logger.warning("Tesseract not found in standard paths. Please set the path manually.")
    
    def extract_text(self, image, config_name='auto'):
        """Extract text using Tesseract"""
        try:
            if isinstance(image, str):
                # Image path provided
                image_obj = Image.open(image)
            elif isinstance(image, np.ndarray):
                # numpy array provided
                image_obj = Image.fromarray(image)
            else:
                # PIL Image provided
                image_obj = image
            
            config = TESSERACT_CONFIGS.get(config_name, TESSERACT_CONFIGS['auto'])
            
            # Extract text
            text = pytesseract.image_to_string(image_obj, config=config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return ""
    
    def extract_with_multiple_configs(self, image):
        """Try multiple Tesseract configurations"""
        results = {}
        
        for config_name in TESSERACT_CONFIGS.keys():
            try:
                text = self.extract_text(image, config_name)
                results[config_name] = text
                if text:
                    logger.info(f"Tesseract ({config_name}): Found {len(text)} characters")
            except Exception as e:
                logger.error(f"Tesseract ({config_name}) failed: {e}")
                results[config_name] = ""
        
        # Find the best result (most text)
        best_text = ""
        best_config = ""
        
        for config, text in results.items():
            if len(text) > len(best_text):
                best_text = text
                best_config = config
        
        return {
            'best_text': best_text,
            'best_config': best_config,
            'all_results': results
        }