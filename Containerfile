FROM python:3.11-slim

WORKDIR /app

# System dependencies for OCR + PDF
# - poppler-utils: for PDF tools
# - tesseract-ocr: OCR engine
# - tesseract-ocr-eng: English
# - tesseract-ocr-chi-tra: Traditional Chinese
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-chi-tra \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Run as non-root (best practice)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "web_app.py"]