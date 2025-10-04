import os
import sys
import json
from datetime import datetime
from PIL import Image

# Add Tesseract to PATH manually
tesseract_paths = [
    r"C:\Program Files\Tesseract-OCR",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
]

for path in tesseract_paths:
    if os.path.exists(path):
        os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
        break

def check_tesseract():
    """Check if Tesseract is available"""
    try:
        import pytesseract
        # Try to find tesseract executable
        tesseract_cmd = None
        for path in tesseract_paths:
            if os.path.isfile(path):
                tesseract_cmd = path
                break
            elif os.path.isdir(path):
                exe_path = os.path.join(path, "tesseract.exe")
                if os.path.isfile(exe_path):
                    tesseract_cmd = exe_path
                    break
        
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            print(f"✅ Tesseract found: {tesseract_cmd}")
            return True
        else:
            print("❌ Tesseract executable not found")
            return False
    except Exception as e:
        print(f"❌ Tesseract check failed: {e}")
        return False

def extract_with_tesseract_fixed(image_path):
    """Extract text using Tesseract with fixed path"""
    try:
        import pytesseract
        
        # Set tesseract path explicitly
        tesseract_cmd = None
        for path in [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Users\JHANANISHRI\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        ]:
            if os.path.exists(path):
                tesseract_cmd = path
                break
        
        if not tesseract_cmd:
            return {"error": "Tesseract not found", "method": "tesseract"}
        
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        image = Image.open(image_path)
        
        # Try multiple configurations
        configs = {
            'printed': '--psm 6 --oem 3',
            'handwritten': '--psm 8 --oem 3', 
            'auto': '--psm 3 --oem 3'
        }
        
        best_text = ""
        best_config = ""
        
        for config_name, config in configs.items():
            try:
                text = pytesseract.image_to_string(image, config=config)
                clean_text = text.strip()
                if len(clean_text) > len(best_text):
                    best_text = clean_text
                    best_config = config_name
            except Exception as e:
                print(f"   Config {config_name} failed: {e}")
                continue
        
        return {
            'text': best_text,
            'config': best_config,
            'length': len(best_text),
            'method': 'tesseract'
        }
        
    except Exception as e:
        return {'error': f"Tesseract extraction failed: {e}", 'method': 'tesseract'}

def extract_with_trocr_simple(image_path, model_type='printed'):
    """Simple TrOCR extraction without complex dependencies"""
    try:
        # Import only what we need
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        import torch
        
        print(f"   Loading TrOCR {model_type} model...")
        
        if model_type == 'printed':
            processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
            model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
        else:
            processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
            model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        
        image = Image.open(image_path).convert('RGB')
        
        # Process and generate
        pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
        
        with torch.no_grad():
            generated_ids = model.generate(
                pixel_values,
                max_length=512,
                num_beams=4,
                early_stopping=True
            )
        
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return {
            'text': text.strip(),
            'length': len(text.strip()),
            'method': f'trocr_{model_type}',
            'confidence': 0.8
        }
        
    except Exception as e:
        print(f"   TrOCR {model_type} failed: {e}")
        return {'error': f"TrOCR {model_type} failed", 'method': f'trocr_{model_type}'}

def main():
    image_path = "invoice_image/invoice6.jpeg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print("🧾 INVOICE TEXT EXTRACTION")
    print("=" * 60)
    
    # Check available methods
    tesseract_available = check_tesseract()
    
    # Process with available methods
    all_results = {}
    
    # Tesseract extraction
    if tesseract_available:
        print("\n📸 Extracting with Tesseract...")
        tesseract_result = extract_with_tesseract_fixed(image_path)
        all_results['tesseract'] = tesseract_result
        
        if 'text' in tesseract_result and tesseract_result['text']:
            print(f"   ✅ Tesseract found {tesseract_result['length']} characters")
        else:
            print("   ❌ Tesseract found no text")
    
    # Try TrOCR if Tesseract fails or for additional extraction
    print("\n🤖 Trying TrOCR models...")
    try:
        trocr_printed_result = extract_with_trocr_simple(image_path, 'printed')
        all_results['trocr_printed'] = trocr_printed_result
        
        if 'text' in trocr_printed_result and trocr_printed_result['text']:
            print(f"   ✅ TrOCR Printed found {trocr_printed_result['length']} characters")
        
        trocr_handwritten_result = extract_with_trocr_simple(image_path, 'handwritten')
        all_results['trocr_handwritten'] = trocr_handwritten_result
        
        if 'text' in trocr_handwritten_result and trocr_handwritten_result['text']:
            print(f"   ✅ TrOCR Handwritten found {trocr_handwritten_result['length']} characters")
            
    except Exception as e:
        print(f"   ❌ TrOCR failed: {e}")
    
    # Select best result
    candidates = []
    
    for method, result in all_results.items():
        if 'text' in result and result['text'] and len(result['text']) > 10:
            candidates.append({
                'text': result['text'],
                'method': result['method'],
                'length': result['length'],
                'confidence': result.get('confidence', 0.7)
            })
    
    if candidates:
        # Select by length and confidence
        best_candidate = max(candidates, key=lambda x: x['length'])
        print(f"\n🏆 BEST RESULT: {best_candidate['method']}")
        print(f"📏 Text Length: {best_candidate['length']} characters")
    else:
        best_candidate = {'text': 'No text extracted', 'method': 'none', 'length': 0}
        print("\n❌ No text extracted from any method")
    
    # Display results
    print("\n" + "=" * 60)
    print("📄 EXTRACTED TEXT:")
    print("=" * 60)
    print(best_candidate['text'])
    print("=" * 60)
    
    # Save results
    output_data = {
        'file_path': image_path,
        'timestamp': datetime.now().isoformat(),
        'best_result': best_candidate,
        'all_results': all_results
    }
    
    output_file = "invoice6_final_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Save text file
    os.makedirs("extracted_texts", exist_ok=True)
    text_file = "extracted_texts/invoice6_extracted.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(f"Source: {image_path}\n")
        f.write(f"Method: {best_candidate['method']}\n")
        f.write(f"Length: {best_candidate['length']} characters\n")
        f.write("=" * 50 + "\n")
        f.write(best_candidate['text'])
    
    print(f"📝 Text saved to: {text_file}")
    
    # Show method comparison
    if len(all_results) > 1:
        print("\n🔬 METHOD COMPARISON:")
        for method, result in all_results.items():
            if 'text' in result and result['text']:
                print(f"  {result['method']}: {result['length']} chars")

if __name__ == "__main__":
    main()