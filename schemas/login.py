from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class LoginRequest(BaseModel):
    """Modelo para la solicitud de login."""
    session_id: str
    boleta: str
    password: str
    captcha_code: str


class PeriodoOption(BaseModel):
    value: str
    text: str


class PlanOption(BaseModel):
    value: str
    text: str
    periodos: Optional[List[PeriodoOption]] = None


class CarreraOption(BaseModel):
    value: str
    text: str
    planes: Optional[List[PlanOption]] = None


class CarreraInfo(BaseModel):
    """Modelo para información de carrera"""
    carreras: List[CarreraOption]


class LoginResponse(BaseModel):
    """Modelo para la respuesta del login"""
    status: str
    message: str
    session_id: str
    carrera_info: Optional[CarreraInfo] = None
    # Cookies de autenticación (ASP.NET_SessionId y .ASPXFORMSAUTH)
    cookies: Optional[Dict[str, str]] = None
