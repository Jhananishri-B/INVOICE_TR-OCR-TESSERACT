import os
import json
import logging
from datetime import datetime
from hybrid_extractor import HybridInvoiceExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchInvoiceProcessor:
    def __init__(self):
        self.extractor = HybridInvoiceExtractor()

    def process_folder(self, input_folder, output_file="batch_results.json"):
        """Process all images in a folder"""
        if not os.path.exists(input_folder):
            logger.error(f"Input folder does not exist: {input_folder}")
            return

        # Supported image formats
        image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')

        # Find all image files
        image_files = []
        for file in os.listdir(input_folder):
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(input_folder, file))

        if not image_files:
            logger.error(f"No image files found in: {input_folder}")
            return

        logger.info(f"Found {len(image_files)} images to process")

        results = {}
        successful = 0
        failed = 0

        for i, image_path in enumerate(image_files, 1):
            logger.info(f"[{i}/{len(image_files)}] Processing: {os.path.basename(image_path)}")

            try:
                # Process image
                result = self.extractor.process_image(image_path)
                results[image_path] = result

                best_text = result.get('best_result', {}).get('text', '')
                if best_text:
                    successful += 1
                    logger.info(f"  ✓ Success - {len(best_text)} characters")
                    # Show preview
                    preview = best_text[:100] + "..." if len(best_text) > 100 else best_text
                    logger.info(f"  Preview: {preview}")
                else:
                    failed += 1
                    logger.warning("  ⚠ No text extracted")

            except Exception as e:
                failed += 1
                logger.error(f"  ✗ Failed: {e}")
                results[image_path] = {
                    'file_path': image_path,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }

        # Prepare final output
        output_data = {
            'metadata': {
                'processing_date': datetime.now().isoformat(),
                'input_folder': input_folder,
                'total_images': len(image_files),
                'successful': successful,
                'failed': failed
            },
            'results': results
        }

        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"\n{'='*60}")
        logger.info("BATCH PROCESSING COMPLETED!")
        logger.info(f"{'='*60}")
        logger.info(f"Input folder: {input_folder}")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Total processed: {len(image_files)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"{'='*60}")

        return output_data


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python batch_processor.py <folder_path> [output_json]")
        print("Example: python batch_processor.py invoice_image batch_results.json")
        sys.exit(1)

    folder_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "batch_results.json"

    processor = BatchInvoiceProcessor()
    processor.process_folder(folder_path, output_file)