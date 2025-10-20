from pydantic import BaseModel
from typing import Dict, Any, Optional

class CaptchaImage(BaseModel):
    """Modelo para la imagen del captcha"""
    base64: str
    content_type: str
    src: str

class CaptchaDiv(BaseModel):
    """Modelo para el div del captcha"""
    html: str
    class_: Optional[list] = None
    id: Optional[str] = None
    
    class Config:
        fields = {'class_': 'class'}

class CaptchaResponse(BaseModel):
    """Modelo para la respuesta completa del captcha"""
    session_id: str
    captcha_image: CaptchaImage
    captcha_div: CaptchaDiv
    hidden_fields: Dict[str, str]
    cookies: Dict[str, str]
    timestamp: Optional[str] = None
    status: str

class CaptchaStatusResponse(BaseModel):
    """Modelo para la respuesta del estado del captcha"""
    status: str
    message: str

    