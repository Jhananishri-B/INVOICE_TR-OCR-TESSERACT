import argparse
import os
import sys
from hybrid_extractor import HybridInvoiceExtractor

def main():
    parser = argparse.ArgumentParser(description="Invoice Text Extraction Pipeline")
    parser.add_argument("input_path", help="Path to input image or folder")
    parser.add_argument("--output", "-o", help="Output JSON file", default="extraction_results.json")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_path):
        print(f"Error: Input path '{args.input_path}' does not exist")
        return
    
    print("Invoice OCR Pipeline")
    print("=" * 50)
    
    if os.path.isfile(args.input_path):
        # Single image processing
        print(f"Processing single image: {args.input_path}")
        extractor = HybridInvoiceExtractor()
        result = extractor.process_image(args.input_path, args.output)
        
        best_result = result.get('best_result', {})
        print(f"\nBest Result:")
        print(f"Method: {best_result.get('method', 'N/A')}")
        print(f"Confidence: {best_result.get('confidence', 0):.3f}")
        print(f"Text Length: {len(best_result.get('text', ''))} characters")
        print(f"\nExtracted Text:")
        print("=" * 50)
        print(best_result.get('text', 'No text extracted'))
        print("=" * 50)
        
    elif os.path.isdir(args.input_path):
        # Batch processing
        print(f"Processing folder: {args.input_path}")
        
        from batch_processor import BatchInvoiceProcessor
        processor = BatchInvoiceProcessor()
        processor.process_folder(args.input_path, args.output)
        
    else:
        print("Error: Invalid input path")
        return

if __name__ == "__main__":
    main()