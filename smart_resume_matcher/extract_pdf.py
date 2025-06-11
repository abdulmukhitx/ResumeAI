#!/usr/bin/env python
"""
PDF Text Extraction Utility

This script extracts text from a PDF file using multiple methods (PyPDF2, pdfminer, etc.)
to ensure the best possible text extraction.

Usage:
python extract_pdf.py /path/to/your/resume.pdf
"""

import os
import sys
import argparse
from pathlib import Path

# Setup for PDF extraction methods
def extract_with_pypdf2(file_path):
    """Extract text using PyPDF2"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"PyPDF2 extraction failed: {str(e)}")
        return ""

def extract_with_pdfminer(file_path):
    """Extract text using pdfminer.six"""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(file_path)
        return text.strip()
    except Exception as e:
        print(f"pdfminer.six extraction failed: {str(e)}")
        return ""

def extract_with_pdfplumber(file_path):
    """Extract text using pdfplumber"""
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"pdfplumber extraction failed: {str(e)}")
        return ""

def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF using multiple methods')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"File not found: {args.pdf_path}")
        return 1
    
    print(f"Extracting text from: {args.pdf_path}")
    
    # Try multiple extraction methods
    methods = [
        ("PyPDF2", extract_with_pypdf2),
        ("pdfminer.six", extract_with_pdfminer),
        ("pdfplumber", extract_with_pdfplumber)
    ]
    
    for method_name, extract_func in methods:
        print(f"\n=== Using {method_name} ===")
        text = extract_func(args.pdf_path)
        
        if text:
            print(f"Successfully extracted {len(text)} characters")
            print("\nFirst 500 characters:")
            print(text[:500] + "..." if len(text) > 500 else text)
        else:
            print("Extraction failed or returned empty text")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
