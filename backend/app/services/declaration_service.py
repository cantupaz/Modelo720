"""Business logic for Modelo 720 declaration operations."""
import sys
import os
from typing import List, Literal
import tempfile

# Add parent directory to path to import Modelo720 library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from Modelo720 import Parser, DeclarationValidationError
from Modelo720.declaracion import Declaration


class DeclarationService:
    """Service for handling Modelo 720 declaration operations."""
    
    def __init__(self):
        self.parser = Parser()
    
    def parse_file(self, file_path: str, format: Literal["720", "csv"]) -> Declaration:
        """
        Parse a Modelo 720 file.
        
        Args:
            file_path: Path to the file to parse
            format: File format ('720' or 'csv')
        
        Returns:
            Parsed Declaration object
        """
        if format == "720":
            return self.parser.read_fixed_width(file_path)
        elif format == "csv":
            return self.parser.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def validate_declaration(self, declaration: Declaration) -> List[str]:
        """
        Validate a declaration and return any errors.
        
        Args:
            declaration: Declaration to validate
        
        Returns:
            List of error messages (empty if valid)
        """
        try:
            declaration.validate()
            return []
        except DeclarationValidationError as e:
            return [str(e)]
        except Exception as e:
            return [f"Validation error: {str(e)}"]
    
    def convert_to_format(self, declaration: Declaration, format: Literal["720", "csv"]) -> str:
        """
        Convert a declaration to the specified format.
        
        Args:
            declaration: Declaration to convert
            format: Target format ('720' or 'csv')
        
        Returns:
            String content in the target format
        """
        # Use temporary file since Parser requires file paths
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{format}') as tmp:
            tmp_path = tmp.name
        
        try:
            if format == "720":
                self.parser.write_fixed_width(declaration, tmp_path)
            elif format == "csv":
                self.parser.write_csv(declaration, tmp_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Read the generated file
            with open(tmp_path, 'r', encoding='utf-8') as f:
                return f.read()
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
