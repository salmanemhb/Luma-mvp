"""
OCR utilities - text extraction from PDFs and images
Uses Tesseract OCR with Spanish optimization
"""

import os
import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

# OCR provider configuration
OCR_PROVIDER = os.getenv("OCR_PROVIDER", "tesseract")  # tesseract | vision


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using multiple methods
    
    1. Try pdftotext (fast, for digital PDFs)
    2. Fall back to Tesseract OCR (for scanned PDFs)
    """
    try:
        # Method 1: Try pdftotext first (works for digital PDFs)
        if _check_command_exists("pdftotext"):
            text = _extract_with_pdftotext(pdf_path)
            if text and len(text.strip()) > 50:  # Minimum threshold
                logger.info(f"✅ Extracted text from PDF using pdftotext: {len(text)} chars")
                return text
        
        # Method 2: Use Tesseract OCR (for scanned documents)
        if OCR_PROVIDER == "tesseract":
            text = _extract_with_tesseract(pdf_path)
            logger.info(f"✅ Extracted text from PDF using Tesseract: {len(text)} chars")
            return text
        
        # Method 3: Google Vision API (optional upgrade)
        elif OCR_PROVIDER == "vision":
            text = _extract_with_vision_api(pdf_path)
            logger.info(f"✅ Extracted text from PDF using Vision API: {len(text)} chars")
            return text
        
        logger.warning("⚠️ No OCR method available")
        return ""
        
    except Exception as e:
        logger.error(f"❌ PDF extraction failed: {str(e)}")
        return ""


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image using OCR
    """
    try:
        if OCR_PROVIDER == "tesseract":
            return _extract_image_with_tesseract(image_path)
        elif OCR_PROVIDER == "vision":
            return _extract_with_vision_api(image_path)
        else:
            logger.warning("⚠️ No OCR provider configured")
            return ""
    except Exception as e:
        logger.error(f"❌ Image extraction failed: {str(e)}")
        return ""


def _check_command_exists(command: str) -> bool:
    """Check if command is available in PATH"""
    try:
        subprocess.run(
            [command, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        return True
    except FileNotFoundError:
        return False


def _extract_with_pdftotext(pdf_path: str) -> str:
    """
    Extract text using pdftotext command
    Install: apt-get install poppler-utils (Linux) or brew install poppler (Mac)
    """
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"pdftotext failed: {e.stderr}")
        return ""
    except FileNotFoundError:
        logger.warning("pdftotext not found. Install poppler-utils.")
        return ""


def _extract_with_tesseract(pdf_path: str) -> str:
    """
    Extract text using Tesseract OCR
    Requires: tesseract-ocr, pdf2image (converts PDF to images first)
    
    Install Tesseract:
    - Linux: apt-get install tesseract-ocr tesseract-ocr-spa
    - Mac: brew install tesseract tesseract-lang
    - Windows: download from https://github.com/UB-Mannheim/tesseract/wiki
    """
    try:
        # Convert PDF to images
        from pdf2image import convert_from_path
        import pytesseract
        
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=300)
        
        # OCR each page with Spanish + English
        text_parts = []
        for i, image in enumerate(images):
            # Use Spanish + English for better accuracy
            text = pytesseract.image_to_string(
                image,
                lang='spa+eng',  # Spanish + English
                config='--psm 6'  # Assume uniform text block
            )
            text_parts.append(text)
            logger.debug(f"OCR page {i+1}/{len(images)}: {len(text)} chars")
        
        full_text = "\n\n".join(text_parts)
        return full_text
        
    except ImportError:
        logger.error("❌ pdf2image or pytesseract not installed. Run: pip install pdf2image pytesseract")
        return ""
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {str(e)}")
        return ""


def _extract_image_with_tesseract(image_path: str) -> str:
    """
    Extract text from image using Tesseract
    """
    try:
        import pytesseract
        from PIL import Image
        
        image = Image.open(image_path)
        text = pytesseract.image_to_string(
            image,
            lang='spa+eng',
            config='--psm 6'
        )
        return text
    except ImportError:
        logger.error("❌ pytesseract or PIL not installed")
        return ""
    except Exception as e:
        logger.error(f"Image OCR failed: {str(e)}")
        return ""


def _extract_with_vision_api(file_path: str) -> str:
    """
    Extract text using Google Cloud Vision API
    
    Setup:
    1. Enable Vision API in Google Cloud Console
    2. Create service account and download credentials JSON
    3. Set GOOGLE_APPLICATION_CREDENTIALS environment variable
    4. pip install google-cloud-vision
    """
    try:
        from google.cloud import vision
        
        client = vision.ImageAnnotatorClient()
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(response.error.message)
        
        texts = response.text_annotations
        if texts:
            return texts[0].description
        
        return ""
        
    except ImportError:
        logger.error("❌ google-cloud-vision not installed. Run: pip install google-cloud-vision")
        return ""
    except Exception as e:
        logger.error(f"Vision API failed: {str(e)}")
        return ""


# Testing utilities
if __name__ == "__main__":
    # Test OCR setup
    print("🔍 Testing OCR configuration...")
    print(f"OCR Provider: {OCR_PROVIDER}")
    print(f"pdftotext available: {_check_command_exists('pdftotext')}")
    print(f"tesseract available: {_check_command_exists('tesseract')}")
    
    try:
        import pytesseract
        print(f"pytesseract installed: ✅")
        print(f"Tesseract version: {pytesseract.get_tesseract_version()}")
    except ImportError:
        print("pytesseract installed: ❌")
