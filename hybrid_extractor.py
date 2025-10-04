import logging
from tesseract_extractor import TesseractExtractor
from trocr_extractor import TRoCRExtractor
from preprocessor import ImagePreprocessor
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridInvoiceExtractor:
    def __init__(self):
        logger.info("Initializing Hybrid OCR System...")
        
        # Initialize components
        self.preprocessor = ImagePreprocessor()
        self.tesseract = TesseractExtractor()
        self.trocr_printed = TRoCRExtractor('printed')
        self.trocr_handwritten = TRoCRExtractor('handwritten')
        
        logger.info("Hybrid OCR System initialized successfully")
    
    def extract_text_hybrid(self, image_path):
        """Extract text using all available methods"""
        logger.info(f"Processing: {image_path}")
        
        results = {}
        
        # Method 1: Tesseract with multiple configurations
        logger.info("Running Tesseract OCR...")
        tesseract_results = self.tesseract.extract_with_multiple_configs(image_path)
        results['tesseract'] = tesseract_results
        
        # Method 2: TR-OCR Printed
        logger.info("Running TR-OCR Printed...")
        try:
            trocr_printed_result = self.trocr_printed.extract_with_confidence(image_path)
            results['trocr_printed'] = trocr_printed_result
        except Exception as e:
            logger.error(f"TR-OCR Printed failed: {e}")
            results['trocr_printed'] = {'text': '', 'confidence': 0.0}
        
        # Method 3: TR-OCR Handwritten
        logger.info("Running TR-OCR Handwritten...")
        try:
            trocr_handwritten_result = self.trocr_handwritten.extract_with_confidence(image_path)
            results['trocr_handwritten'] = trocr_handwritten_result
        except Exception as e:
            logger.error(f"TR-OCR Handwritten failed: {e}")
            results['trocr_handwritten'] = {'text': '', 'confidence': 0.0}
        
        # Determine best result
        best_result = self._select_best_result(results)
        
        return {
            'best_result': best_result,
            'all_results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _select_best_result(self, results):
        """Select the best result from all methods"""
        candidates = []
        
        # Tesseract results
        tesseract_text = results['tesseract']['best_text']
        if tesseract_text:
            candidates.append({
                'text': tesseract_text,
                'method': f"tesseract_{results['tesseract']['best_config']}",
                'confidence': 0.8,  # Estimated confidence for Tesseract
                'length': len(tesseract_text)
            })
        
        # TR-OCR Printed results
        trocr_printed = results['trocr_printed']
        if trocr_printed['text']:
            candidates.append({
                'text': trocr_printed['text'],
                'method': 'trocr_printed',
                'confidence': trocr_printed['confidence'],
                'length': len(trocr_printed['text'])
            })
        
        # TR-OCR Handwritten results
        trocr_handwritten = results['trocr_handwritten']
        if trocr_handwritten['text']:
            candidates.append({
                'text': trocr_handwritten['text'],
                'method': 'trocr_handwritten',
                'confidence': trocr_handwritten['confidence'],
                'length': len(trocr_handwritten['text'])
            })
        
        if not candidates:
            return {'text': '', 'method': 'none', 'confidence': 0.0}
        
        # Select best candidate based on confidence and length
        best_candidate = max(candidates, key=lambda x: (x['confidence'] * 0.7 + min(x['length']/100, 1) * 0.3))
        
        return best_candidate
    
    def process_image(self, image_path, output_json=None):
        """Complete processing pipeline for a single image"""
        try:
            # Extract text using hybrid approach
            extraction_results = self.extract_text_hybrid(image_path)
            
            # Prepare output
            output_data = {
                'file_path': image_path,
                'timestamp': extraction_results['timestamp'],
                'best_result': extraction_results['best_result'],
                'all_results': extraction_results['all_results']
            }
            
            # Save to file if requested
            if output_json:
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Results saved to: {output_json}")
            
            return output_data
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {
                'file_path': image_path,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }