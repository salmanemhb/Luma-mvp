"""
Utils package
"""

from utils.ocr import extract_text_from_pdf, extract_text_from_image
from utils.parser import parse_csv, parse_xlsx, parse_text
from utils.calculator import calculate_emissions
from utils.report_generator import generate_pdf_report, generate_excel_report
from utils.audit import log_event, log_upload, log_analyze, log_report_generated, log_login

__all__ = [
    "extract_text_from_pdf",
    "extract_text_from_image",
    "parse_csv",
    "parse_xlsx",
    "parse_text",
    "calculate_emissions",
    "generate_pdf_report",
    "generate_excel_report",
    "log_event",
    "log_upload",
    "log_analyze",
    "log_report_generated",
    "log_login",
]
