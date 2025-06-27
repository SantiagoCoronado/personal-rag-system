import PyPDF2
import re
from typing import List, Dict, Any
from ..config import settings

class PDFProcessor:
    """Service for processing PDF files and extracting text chunks"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize PDF processor with configurable chunk settings
        
        Args:
            chunk_size: Size of each text chunk in characters (default from settings)
            chunk_overlap: Overlap between chunks in characters (default from settings)
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file using PyPDF2
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
                return text
                
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and special characters
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace (multiple spaces, tabs, newlines)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Clean text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters of the chunk
                search_start = max(start, end - 100)
                search_text = text[search_start:end]
                
                # Find the last sentence ending
                sentence_endings = ['.', '!', '?', '\n']
                last_ending = -1
                
                for ending in sentence_endings:
                    pos = search_text.rfind(ending)
                    if pos > last_ending:
                        last_ending = pos
                
                # If we found a sentence ending, use it as the chunk boundary
                if last_ending != -1:
                    end = search_start + last_ending + 1
            
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position for next chunk (with overlap)
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Complete PDF processing pipeline
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing chunks with metadata
        """
        # Extract text from PDF
        raw_text = self.extract_text_from_pdf(file_path)
        
        # Clean the text
        cleaned_text = self.clean_text(raw_text)
        
        # Split into chunks
        chunks = self.split_into_chunks(cleaned_text)
        
        # Create metadata for each chunk
        processed_chunks = []
        total_chars_so_far = 0
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'chunk_index': i,
                'content': chunk,
                'length': len(chunk),
                'start_char': total_chars_so_far,
                'end_char': total_chars_so_far + len(chunk)
            }
            processed_chunks.append(chunk_data)
            total_chars_so_far += len(chunk)
        
        return processed_chunks
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the processed chunks
        
        Args:
            chunks: List of processed chunks
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_characters': 0,
                'average_chunk_size': 0,
                'min_chunk_size': 0,
                'max_chunk_size': 0
            }
        
        total_chars = sum(chunk['length'] for chunk in chunks)
        chunk_sizes = [chunk['length'] for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_characters': total_chars,
            'average_chunk_size': total_chars / len(chunks),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes)
        } 