"""API models for Modelo 720 declarations.

Since the Modelo720 library now uses Pydantic BaseModel, we can use those
classes directly in the API without creating duplicate wrapper models.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from pydantic import BaseModel, Field
from typing import List

# Re-export library classes for use in API
from Modelo720.declaracion import (
    Declaration,
    Header720,
    Detalle720,
    Valoracion,
    ClaveBien,
    Origen,
    DeclarationValidationError
)

# Alias for backward compatibility with existing API code
DeclarationResponse = Declaration
HeaderModel = Header720
DetalleModel = Detalle720
ValoracionModel = Valoracion


class ValidationResponse(BaseModel):
    """Response model for validation results."""
    valid: bool
    errors: List[str] = Field(default_factory=list)

