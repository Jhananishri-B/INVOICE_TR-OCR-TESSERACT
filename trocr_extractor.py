import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import logging
import numpy as np
from config import TROCR_MODELS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TRoCRExtractor:
    def __init__(self, model_type='printed'):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        self.model_type = model_type
        self.model_name = TROCR_MODELS.get(model_type, TROCR_MODELS['printed'])
        
        self.load_model()
    
    def load_model(self):
        """Load TR-OCR model"""
        try:
            logger.info(f"Loading TR-OCR model: {self.model_name}")
            self.processor = TrOCRProcessor.from_pretrained(self.model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("TR-OCR model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading TR-OCR model: {e}")
            raise
    
    def extract_text(self, image):
        """Extract text using TR-OCR"""
        try:
            if isinstance(image, str):
                # Image path provided
                image_obj = Image.open(image).convert('RGB')
            elif isinstance(image, np.ndarray):
                # numpy array provided
                image_obj = Image.fromarray(image)
            else:
                # PIL Image provided
                image_obj = image.convert('RGB')
            
            # Preprocess for TR-OCR
            pixel_values = self.processor(images=image_obj, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)
            
            # Generate text
            with torch.no_grad():
                generated_ids = self.model.generate(
                    pixel_values,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=2
                )
            
            extracted_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"TR-OCR extraction failed: {e}")
            return ""
    
    def extract_with_confidence(self, image):
        """Extract text with confidence scores"""
        try:
            if isinstance(image, str):
                image_obj = Image.open(image).convert('RGB')
            else:
                image_obj = image.convert('RGB')
            
            pixel_values = self.processor(images=image_obj, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)
            
            with torch.no_grad():
                generated_output = self.model.generate(
                    pixel_values,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                    return_dict_in_generate=True,
                    output_scores=True
                )
            
            # Decode text
            text = self.processor.batch_decode(generated_output.sequences, skip_special_tokens=True)[0]
            
            # Calculate confidence
            confidence = 0.0
            if hasattr(generated_output, 'scores') and generated_output.scores:
                scores = generated_output.scores
                probs = [torch.nn.functional.softmax(score, dim=-1) for score in scores]
                max_probs = [torch.max(prob, dim=-1)[0] for prob in probs]
                confidence = torch.stack(max_probs).mean().item()
            
            return {
                'text': text.strip(),
                'confidence': confidence,
                'model': self.model_name
            }
            
        except Exception as e:
            logger.error(f"TR-OCR confidence extraction failed: {e}")
            return {'text': '', 'confidence': 0.0, 'model': self.model_name}