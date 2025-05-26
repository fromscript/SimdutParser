# 📄 simdutparser

**simdutparser** is a robust PDF parsing tool designed to extract structured data from safety data sheets (SDS), with a special focus on Section 14 and tabular content. It supports both text-based and OCR-based PDF parsing, includes advanced table detection, and is fully configurable via a YAML file.

---

## 🚀 Features

- 🔍 Extracts content from specific sections (e.g., "Section 14") of PDFs.
- 🧠 Smart table detection using regular expressions and delimiters.
- 🧾 Supports both **text-based** and **image-based (OCR)** PDFs.
- ⚙️ Fully configurable via `config/settings.yaml`.
- 📦 Easily installable Python package with CLI interface.
- 🧪 Production-ready structure with support for logging, error handling, and environment overrides.

---

## 🛠 Installation

### 📦 From source

```bash
git clone https://github.com/your-username/simdutparser.git
cd simdutparser
pip install .
```

### 📦 With pip (once published)

```bash
pip install simdutparser
```

---

## 🧑‍💻 Usage

### CLI

```bash
pdf-text-parser path/to/input.pdf
```

This command will:
- Parse the PDF for the configured section (`Section 14` by default).
- Detect tables (if enabled).
- Save structured output to the configured `output_dir`.

---

## 📁 Project Structure

```
simdutparser/
├── src/
│   └── simdutparser/
│       ├── __init__.py
│       ├── parsers/
│       │   ├── __init__.py
│       │   └── text_parser.py
│       └── config/
│           └── settings.yaml
├── setup.py
├── pyproject.toml
├── requirements.txt
├── README.md
```

---

## ⚙️ Configuration

All settings are defined in `config/settings.yaml`. You can adjust:

- Allowed MIME types
- Table detection rules
- OCR options (Tesseract config)
- Input/output paths
- Logging verbosity
- Performance tuning

Example:

```yaml
general:
  section_title: "Section 14"
  max_file_size_mb: 50
  allowed_mime_types:
    - application/pdf
```

You can also override specific settings per environment (e.g., `development`, `production`).

---

## 🔧 Development

### Setup a local dev environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run manually

```bash
python src/simdutparser/parsers/text_parser.py --file ./input/sample.pdf
```

---

## 🧪 Tests

> (Add when tests are available)

```bash
pytest tests/
```

---

## 📝 License

MIT License. See `LICENSE` for details.

---

## 📬 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 🙏 Acknowledgements

- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [PyYAML](https://pyyaml.org/)

---

## 📣 Future Improvements

- OCR parser CLI support
- Structured test suite
- PDF viewer integration
- PDF metadata extraction

---

## 📧 Contact

Created and maintained by [Your Name](mailto:your.email@example.com).
