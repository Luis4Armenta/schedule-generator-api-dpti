from pydantic import BaseModel
from typing import Optional, List, Dict


class CaptchaImage(BaseModel):
    """Modelo para la imagen del captcha"""
    base64: str
    content_type: Optional[str] = None
    src: Optional[str] = None


class CaptchaDiv(BaseModel):
    html: str
    class_field: Optional[List[str]] = None
    id: Optional[str] = None


class CaptchaResponse(BaseModel):
    """Modelo para la respuesta completa del captcha"""
    session_id: str
    captcha_image: CaptchaImage
    captcha_div: Optional[Dict[str, object]] = None
    hidden_fields: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    status: str


class CaptchaStatusResponse(BaseModel):
    """Modelo para la respuesta del estado del captcha"""
    status: str
    message: str

    