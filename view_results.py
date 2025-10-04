import json
import os

def view_extracted_text(results_file):
    """Display extracted text from results file in a clean format"""
    
    if not os.path.exists(results_file):
        print(f"Error: Results file '{results_file}' not found")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("EXTRACTED INVOICE TEXT RESULTS")
    print("=" * 80)
    
    # Display metadata
    metadata = data.get('metadata', {})
    print(f"Processing Date: {metadata.get('processing_date', 'N/A')}")
    print(f"Total Images: {metadata.get('total_images', 0)}")
    print(f"Successful: {metadata.get('successful', 0)}")
    print(f"Failed: {metadata.get('failed', 0)}")
    print("=" * 80)
    
    # Display results for each file
    results = data.get('results', {})
    
    for file_path, result in results.items():
        filename = os.path.basename(file_path)
        print(f"\n📄 FILE: {filename}")
        print("-" * 80)
        
        best_result = result.get('best_result', {})
        extracted_text = best_result.get('text', '')
        method = best_result.get('method', 'N/A')
        confidence = best_result.get('confidence', 0)
        
        print(f"Method: {method} | Confidence: {confidence:.3f} | Length: {len(extracted_text)} chars")
        print("-" * 80)
        
        if extracted_text:
            print(extracted_text)
        else:
            print("❌ No text extracted")
        
        print("-" * 80)

def save_text_to_files(results_file, output_dir="extracted_texts"):
    """Save each invoice's text to individual text files"""
    
    if not os.path.exists(results_file):
        print(f"Error: Results file '{results_file}' not found")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    results = data.get('results', {})
    saved_files = []
    
    for file_path, result in results.items():
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        output_file = os.path.join(output_dir, f"{base_name}_extracted.txt")
        
        best_result = result.get('best_result', {})
        extracted_text = best_result.get('text', '')
        
        # Add metadata to the text file
        method = best_result.get('method', 'N/A')
        confidence = best_result.get('confidence', 0)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Source: {filename}\n")
            f.write(f"Extraction Method: {method}\n")
            f.write(f"Confidence: {confidence:.3f}\n")
            f.write(f"Text Length: {len(extracted_text)} characters\n")
            f.write("=" * 50 + "\n")
            f.write(extracted_text)
        
        saved_files.append(output_file)
        print(f"✓ Saved: {output_file}")
    
    return saved_files

def view_all_methods(results_file, specific_file=None):
    """View results from all OCR methods for comparison"""
    
    if not os.path.exists(results_file):
        print(f"Error: Results file '{results_file}' not found")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get('results', {})
    
    for file_path, result in results.items():
        filename = os.path.basename(file_path)
        
        # If specific file is requested, skip others
        if specific_file and specific_file not in filename:
            continue
        
        print(f"\n🔍 COMPARISON FOR: {filename}")
        print("=" * 80)
        
        all_results = result.get('all_results', {})
        
        # Tesseract results
        tesseract_results = all_results.get('tesseract', {})
        print("📊 TESSERACT RESULTS:")
        for config, text in tesseract_results.get('all_results', {}).items():
            if text:
                print(f"  {config}: {len(text)} chars - {text[:50]}...")
        
        # TR-OCR Printed results
        trocr_printed = all_results.get('trocr_printed', {})
        if trocr_printed.get('text'):
            print(f"🤖 TR-OCR PRINTED: {len(trocr_printed['text'])} chars")
            print(f"  Confidence: {trocr_printed.get('confidence', 0):.3f}")
            print(f"  Text: {trocr_printed['text'][:50]}...")
        
        # TR-OCR Handwritten results
        trocr_handwritten = all_results.get('trocr_handwritten', {})
        if trocr_handwritten.get('text'):
            print(f"✍️ TR-OCR HANDWRITTEN: {len(trocr_handwritten['text'])} chars")
            print(f"  Confidence: {trocr_handwritten.get('confidence', 0):.3f}")
            print(f"  Text: {trocr_handwritten['text'][:50]}...")
        
        # Best result
        best_result = result.get('best_result', {})
        print(f"\n🏆 BEST RESULT ({best_result.get('method', 'N/A')}):")
        print(f"  Confidence: {best_result.get('confidence', 0):.3f}")
        print(f"  Full Text: {best_result.get('text', '')}")
        
        print("=" * 80)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="View extracted invoice text results")
    parser.add_argument("results_file", help="Path to results JSON file", default="batch_results.json", nargs='?')
    parser.add_argument("--view", "-v", action="store_true", help="View extracted text")
    parser.add_argument("--save", "-s", action="store_true", help="Save to individual text files")
    parser.add_argument("--compare", "-c", action="store_true", help="Compare all methods")
    parser.add_argument("--file", "-f", help="Specific file to analyze")
    
    args = parser.parse_args()
    
    if not any([args.view, args.save, args.compare]):
        args.view = True  # Default to view if no option specified
    
    if args.view:
        view_extracted_text(args.results_file)
    
    if args.save:
        saved_files = save_text_to_files(args.results_file)
        print(f"\n🎉 Saved {len(saved_files)} text files to 'extracted_texts' folder")
    
    if args.compare:
        view_all_methods(args.results_file, args.file)

if __name__ == "__main__":
    main()