from pydantic import BaseModel
from typing import Dict, Any, Optional

class CaptchaImage(BaseModel):
    """Modelo para la imagen del captcha"""
    base64: str

class CaptchaResponse(BaseModel):
    """Modelo para la respuesta completa del captcha"""
    session_id: str
    captcha_image: CaptchaImage
    hidden_fields: Dict[str, str]
    cookies: Dict[str, str]
    status: str

class CaptchaStatusResponse(BaseModel):
    """Modelo para la respuesta del estado del captcha"""
    status: str
    message: str

    