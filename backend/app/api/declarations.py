"""API endpoints for Modelo 720 declarations."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import Literal
import io
import tempfile
import os

from app.services.declaration_service import DeclarationService
from app.models.declaration_models import DeclarationResponse, ValidationResponse

router = APIRouter()
service = DeclarationService()


@router.post("/parse", response_model=DeclarationResponse)
async def parse_declaration(
    file: UploadFile = File(...),
    format: Literal["720", "csv"] = "720"
):
    """
    Parse a Modelo 720 file (either .720 fixed-width or .csv format).
    
    Args:
        file: The file to parse
        format: File format ('720' for fixed-width, 'csv' for CSV)
    
    Returns:
        Parsed declaration as JSON
    """
    try:
        content = await file.read()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=f'.{format}') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Parser returns Declaration which is already a Pydantic model
            declaration = service.parse_file(tmp_path, format)
            return declaration
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")


@router.post("/validate", response_model=ValidationResponse)
async def validate_declaration(declaration: DeclarationResponse):
    """
    Validate a Modelo 720 declaration.
    
    Args:
        declaration: Declaration data to validate
    
    Returns:
        Validation result with any errors
    """
    try:
        # DeclarationResponse is now just an alias for Declaration
        # No conversion needed - validation happens automatically via Pydantic
        errors = service.validate_declaration(declaration)
        
        return ValidationResponse(
            valid=len(errors) == 0,
            errors=errors
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")


@router.post("/convert")
async def convert_format(
    file: UploadFile = File(...),
    source_format: Literal["720", "csv"] = "720",
    target_format: Literal["720", "csv"] = "csv"
):
    """
    Convert between Modelo 720 formats.
    
    Args:
        file: Source file to convert
        source_format: Source file format ('720' or 'csv')
        target_format: Target file format ('720' or 'csv')
    
    Returns:
        Converted file
    """
    if source_format == target_format:
        raise HTTPException(status_code=400, detail="Source and target formats must be different")
    
    try:
        content = await file.read()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=f'.{source_format}') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Parse source file
            declaration = service.parse_file(tmp_path, source_format)
            
            # Convert to target format
            output = service.convert_to_format(declaration, target_format)
            
            # Return as downloadable file
            filename = f"converted.{target_format}"
            media_type = "text/csv" if target_format == "csv" else "text/plain"
            
            return StreamingResponse(
                io.BytesIO(output.encode('utf-8')),
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion failed: {str(e)}")


@router.post("/export")
async def export_declaration(
    declaration: DeclarationResponse,
    format: Literal["720", "csv"] = "720"
):
    """
    Export a declaration to the specified format.
    
    Args:
        declaration: Declaration data to export
        format: Target format ('720' or 'csv')
    
    Returns:
        File in requested format
    """
    try:
        # DeclarationResponse is now just an alias for Declaration - no conversion needed
        output = service.convert_to_format(declaration, format)
        
        filename = f"modelo720.{format}"
        media_type = "text/csv" if format == "csv" else "text/plain"
        
        return StreamingResponse(
            io.BytesIO(output.encode('utf-8')),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Export failed: {str(e)}")
