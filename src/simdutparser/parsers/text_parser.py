import argparse
import csv
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import pymupdf
import yaml

from simdutparser.utils.logger import configure_logger

configure_logger()
logger = logging.getLogger(__name__)


class TextPDFParser:
    """A sophisticated PDF parser for extracting structured data from specific sections."""

    def __init__(self, config: Dict):
        self.config = config
        self.section_title = config.get('section_title', 'Section 14')
        self._compiled_patterns = {
            'section': self._compile_pattern(self.section_title),
            'base_section': self._compile_pattern("section")
        }

    def _compile_pattern(self, text: str) -> re.Pattern:
        """Compile case-insensitive regex pattern with caching."""
        return re.compile(re.escape(text.strip()), flags=re.IGNORECASE)

    def _clean_table_cell(self, cell: str) -> str:
        """Normalize table cell content."""
        return re.sub(r'\s+', ' ', cell).strip()

    def _process_table(self, table: pymupdf.table) -> Dict[str, List[str]]:
        """Process a single table into structured data."""
        try:
            data = table.extract()
            if len(data) < 2:
                return {}

            headers = [self._clean_table_cell(str(cell)) for cell in data[0]]
            columns = list(zip(*data[1:]))

            return {
                header: [self._clean_table_cell(str(cell)) for cell in column] for header, column in zip(headers, columns) if header
            }
        except (TypeError, IndexError) as e:
            logger.warning(f"Table processing error: {str(e)}")
            return {}

    def _process_text_block(self, text: str) -> Dict[str, str]:
        """Convert multi-line text blocks into multiple key-value pairs."""
        processed = {}
        # Split into lines and clean
        lines = [re.sub(r'\s+', ' ', line.strip()) for line in text.split('\n')]
        lines = [line for line in lines if line]  # Remove empty lines

        current_key = None
        for i, line in enumerate(lines):
            if i % 2 == 0:  # Even index lines are keys
                current_key = line
            else:  # Odd index lines are values
                if current_key:
                    processed[current_key] = line
                    current_key = None

        # Handle case with odd number of lines
        if current_key is not None and current_key not in processed:
            processed[current_key] = ''

        return processed

    def _find_section_boundaries(self, page: pymupdf.Page) -> Optional[Dict[str, str]]:
        """Locate section boundaries using advanced pattern matching."""
        text = page.get_text("text")
        boundaries = {}

        lines = (line.strip() for line in text.split('\n'))

        for line in lines:
            if self._compiled_patterns['section'].search(line):
                boundaries["start_marker"] = line
                boundaries["stop_marker"] = next(
                    (l for l in lines if self._compiled_patterns['base_section'].search(l)),
                    None
                )
                break
        return boundaries if boundaries else None


    def _calculate_subsection_bbox(self, page: pymupdf.Page, markers: Dict[str, str]) -> Optional[pymupdf.Rect]:
        """Calculate bounding box for target subsection."""
        try:
            start_rects = page.search_for(markers["start_marker"])
            stop_rects = page.search_for(markers["stop_marker"])

            if not start_rects or not stop_rects:
                return None

            return pymupdf.Rect(
                0,  # Full page width
                start_rects[0].y1,
                page.rect.width,
                stop_rects[0].y0
            )
        except KeyError:
            return None


    def _merge_data(self, existing: Dict, new: Dict) -> Dict:
        """Smart data merging with conflict resolution."""
        for key, value in new.items():
            if key in existing:
                # Handle key conflicts
                if isinstance(existing[key], list) and isinstance(value, list):
                    existing[key].extend(value)
                elif isinstance(existing[key], list):
                    existing[key].append(value)
                else:
                    existing[f"{key}_conflict"] = value
            else:
                existing[key] = value
        return existing


    def extract_section(self, pdf_path: Path) -> Dict:
        """Main extraction workflow with error handling."""
        doc = pymupdf.open(pdf_path)
        result = {"name": doc.name.replace('.pdf', '')}
        try:
            for page in doc:
                if not self._compiled_patterns['section'].search(page.get_text()):
                    continue

                markers = self._find_section_boundaries(page)
                if not markers:
                    continue

                bbox = self._calculate_subsection_bbox(page, markers)
                if not bbox:
                    continue

                # Process page content
                page_result = self._process_page_content(page, bbox)
                result = self._merge_data(result, page_result)

        finally:
            doc.close()

        return result


    def _process_page_content(self, page: pymupdf.Page, bbox: pymupdf.Rect) -> Dict:
        """Process all content within a page subsection."""
        content = {}
        exclusion_zones = []

        # Process tables first
        for table in page.find_tables(clip=bbox):
            table_data = self._process_table(table)
            content = self._merge_data(content, table_data)
            exclusion_zones.append(table.bbox)

        # Process text blocks
        for block in page.get_text("blocks", clip=bbox):
            rect = pymupdf.Rect(block[:4])
            text = block[4]

            if not text.strip() or any(rect.intersects(zone) for zone in exclusion_zones):
                continue

            text_data = self._process_text_block(text)
            content = self._merge_data(content, text_data)

        return content


    def export_to_csv(self, data: Dict, output_path: Path) -> None:
        """Optimized CSV export with type handling."""
        if not data:
            logger.warning("No data to export")
            return

        # Prepare matrix structure
        headers = list(data.keys())
        max_rows = max((len(v) if isinstance(v, list) else 1 for v in data.values()))
        rows = []

        for row_idx in range(max_rows):
            row = []
            for header in headers:
                value = data[header]
                try:
                    entry = value[row_idx] if isinstance(value, list) else (value if row_idx == 0 else '')
                except IndexError:
                    entry = ''
                row.append(str(entry))
            rows.append(row)

        # Write CSV with efficient single write
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)
            writer.writerows(rows)

        logger.info(f"Successfully exported {len(rows)} rows to {output_path}")


def main():
    """Enhanced CLI with better error handling."""
    configure_logger()
    parser = argparse.ArgumentParser(description='PDF Section Extractor')
    parser.add_argument('-i', '--input', type=Path, required=True)
    parser.add_argument('-o', '--output', type=Path, default=Path('output.csv'))
    parser.add_argument('-c', '--config', type=Path, default=Path('config.yaml'))

    try:
        args = parser.parse_args()
        config = yaml.safe_load(args.config.read_text())

        parser = TextPDFParser(config)
        data = parser.extract_section(args.input)

        if data:
            parser.export_to_csv(data, args.output)
            logger.info("Processing completed successfully")
        else:
            logger.error("No data extracted from PDF")
            raise SystemExit(1)

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
