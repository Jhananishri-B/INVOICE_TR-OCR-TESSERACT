import json
import os
from datetime import datetime

def analyze_quality(results_file):
    """Analyze the quality of extracted text"""
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get('results', {})
    
    print("📈 EXTRACTION QUALITY ANALYSIS")
    print("=" * 60)
    
    total_chars = 0
    file_count = 0
    confidence_scores = []
    
    for file_path, result in results.items():
        filename = os.path.basename(file_path)
        best_result = result.get('best_result', {})
        text = best_result.get('text', '')
        confidence = best_result.get('confidence', 0)
        method = best_result.get('method', 'N/A')
        
        if text:
            total_chars += len(text)
            file_count += 1
            confidence_scores.append(confidence)
            
            print(f"\n📊 {filename}:")
            print(f"  Method: {method}")
            print(f"  Confidence: {confidence:.3f}")
            print(f"  Text Length: {len(text)} chars")
            print(f"  Preview: {text[:80]}...")
    
    if file_count > 0:
        avg_chars = total_chars / file_count
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        print(f"\n📈 SUMMARY:")
        print(f"  Files with text: {file_count}/{len(results)}")
        print(f"  Average text length: {avg_chars:.1f} chars")
        print(f"  Average confidence: {avg_confidence:.3f}")
        print(f"  Total characters extracted: {total_chars}")

def export_to_csv(results_file, output_csv="extracted_results.csv"):
    """Export results to CSV format"""
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    import csv
    
    results = data.get('results', {})
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['File', 'Method', 'Confidence', 'Text Length', 'Extracted Text'])
        
        for file_path, result in results.items():
            filename = os.path.basename(file_path)
            best_result = result.get('best_result', {})
            text = best_result.get('text', '')
            confidence = best_result.get('confidence', 0)
            method = best_result.get('method', 'N/A')
            
            # Clean text for CSV (remove newlines)
            clean_text = text.replace('\n', ' ').replace('\r', ' ')
            
            writer.writerow([filename, method, f"{confidence:.3f}", len(text), clean_text])
    
    print(f"✓ Results exported to: {output_csv}")

if __name__ == "__main__":
    analyze_quality("batch_results.json")
    export_to_csv("batch_results.json")