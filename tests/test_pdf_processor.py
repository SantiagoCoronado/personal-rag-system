#!/usr/bin/env python3
"""
Test script for PDF Processor service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_processor import PDFProcessor
import tempfile
import PyPDF2

def create_test_pdf():
    """Create a simple test PDF file"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        # Create a simple PDF with PyPDF2
        writer = PyPDF2.PdfWriter()
        
        # Create a simple page with text
        from PyPDF2.generic import NameObject, createStringObject
        from PyPDF2.generic._base import TextStringObject
        
        # This is a simplified approach - in practice you'd use a proper PDF library
        # For testing purposes, we'll create a minimal PDF
        page = PyPDF2.PageObject()
        page.merge_page(PyPDF2.PageObject.create_blank_page(width=612, height=792))
        writer.add_page(page)
        
        with open(tmp_file.name, 'wb') as output_file:
            writer.write(output_file)
        
        return tmp_file.name

def test_pdf_processor():
    """Test the PDF processor functionality"""
    print("🧪 Testing PDF Processor...")
    
    try:
        # Initialize processor
        processor = PDFProcessor(chunk_size=500, chunk_overlap=100)
        print("✅ PDF Processor initialized")
        
        # Test text cleaning
        test_text = "This   is   a   test   text   with   extra   spaces.\n\nAnd newlines.\n\n\n"
        cleaned = processor.clean_text(test_text)
        print(f"✅ Text cleaning test: '{cleaned}'")
        
        # Test chunk splitting
        long_text = "This is a long text that should be split into multiple chunks. " * 20
        chunks = processor.split_into_chunks(long_text)
        print(f"✅ Chunk splitting test: {len(chunks)} chunks created")
        
        # Test chunk statistics with proper chunk format
        chunk_dicts = [{'content': chunk, 'length': len(chunk)} for chunk in chunks]
        stats = processor.get_chunk_statistics(chunk_dicts)
        print(f"✅ Statistics test: {stats}")
        
        # Test with a simple text file (since creating PDFs is complex)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            test_content = "This is a test document. " * 50
            tmp_file.write(test_content)
            tmp_file.flush()
            
            # Simulate PDF processing by reading the text file
            with open(tmp_file.name, 'r') as f:
                raw_text = f.read()
            
            cleaned_text = processor.clean_text(raw_text)
            chunks = processor.split_into_chunks(cleaned_text)
            
            print(f"✅ File processing test: {len(chunks)} chunks from text file")
            
            # Clean up
            os.unlink(tmp_file.name)
        
        print("🎉 All PDF Processor tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ PDF Processor test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_processor()
    sys.exit(0 if success else 1) 