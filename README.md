A hybrid OCR system for extracting text from invoices using both Tesseract and TrOCR (Transformer-based OCR).

## Features
- **Hybrid OCR**: Combines Tesseract and TrOCR for better accuracy
- **Multiple Models**: TrOCR for printed and handwritten text
- **Batch Processing**: Process multiple invoices at once
- **JSON Output**: Structured results with confidence scores

## Installation
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage
\`\`\`bash
# Single image
python run_pipeline.py path/to/invoice.jpg

# Batch processing
python batch_processor.py path/to/invoice/folder

# View results
python view_results.py results.json
\`\`\`

## Project Structure
- \`hybrid_extractor.py\` - Main OCR engine
- \`tesseract_extractor.py\` - Tesseract OCR wrapper
- \`trocr_extractor.py\` - TrOCR wrapper
- \`run_pipeline.py\` - Single image processor
- \`batch_processor.py\` - Batch processor
- \`view_results.py\` - Results viewer

## Requirements
- Python 3.8+
- Tesseract OCR
- PyTorch
- Transformers
- OpenCV
- Pillow"
