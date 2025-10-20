import requests
import base64
from fastapi import APIRouter, HTTPException
from bs4 import BeautifulSoup
import json
import uuid
from typing import Dict, Any
from schemas.captcha import CaptchaResponse, CaptchaStatusResponse

router = APIRouter()

@router.get("/captcha", response_model=CaptchaResponse)
async def get_captcha() -> CaptchaResponse:
    """
    Extrae el captcha de la página del SAES y devuelve la información necesaria
    junto con el contenido del div en formato JSON.
    """
    try:
        # URL del SAES
        saes_url = "https://www.saes.upiicsa.ipn.mx/"
        
        # Crear una sesión para mantener cookies
        session = requests.Session()
        
        # Headers para simular un navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Realizar petición GET a la página principal
        response = session.get(saes_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parsear el HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar el div del captcha
        captcha_div = soup.find('div', {
            'class': 'LBD_CaptchaImageDiv',
            'id': 'c_default_ctl00_leftcolumn_loginuser_logincaptcha_CaptchaImageDiv'
        })
        
        if not captcha_div:
            raise HTTPException(status_code=404, detail="No se pudo encontrar el div del captcha")
        
        # Buscar la imagen del captcha dentro del div
        captcha_img = captcha_div.find('img')
        if not captcha_img:
            raise HTTPException(status_code=404, detail="No se pudo encontrar la imagen del captcha")
        
        # Obtener la URL de la imagen del captcha
        img_src = captcha_img.get('src')
        if not img_src:
            raise HTTPException(status_code=404, detail="No se pudo obtener la URL de la imagen del captcha")
        
        # Si la URL es relativa, convertirla a absoluta
        if img_src.startswith('/'):
            img_src = f"https://www.saes.upiicsa.ipn.mx{img_src}"
        elif img_src.startswith('./'):
            img_src = f"https://www.saes.upiicsa.ipn.mx/{img_src[2:]}"
        elif not img_src.startswith('http'):
            img_src = f"https://www.saes.upiicsa.ipn.mx/{img_src}"
        
        # Descargar la imagen del captcha
        img_response = session.get(img_src, headers=headers, timeout=10)
        img_response.raise_for_status()
        
        # Convertir la imagen a base64
        img_base64 = base64.b64encode(img_response.content).decode('utf-8')
        
        # Obtener el content-type de la imagen
        content_type = img_response.headers.get('content-type', 'image/png')
        
        # Generar un ID único para esta sesión de captcha
        session_id = str(uuid.uuid4())
        
        # Buscar campos ocultos importantes (como ViewState, EventValidation, etc.)
        hidden_fields = {}
        for input_tag in soup.find_all('input', {'type': 'hidden'}):
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            if name:
                hidden_fields[name] = value
        
        # Preparar la respuesta
        captcha_data = {
            "session_id": session_id,
            "captcha_image": {
                "base64": img_base64,
                "content_type": content_type,
                "src": img_src
            },
            "captcha_div": {
                "html": str(captcha_div),
                "class": captcha_div.get('class'),
                "id": captcha_div.get('id')
            },
            "hidden_fields": hidden_fields,
            "cookies": dict(session.cookies),
            "timestamp": response.headers.get('date'),
            "status": "success"
        }
        
        return captcha_data
        
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error al conectar con SAES: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/captcha/refresh", response_model=CaptchaResponse)
async def refresh_captcha() -> CaptchaResponse:
    """
    Refresca el captcha obteniendo uno nuevo desde el SAES.
    Esta función es útil cuando el captcha actual ha expirado o no es legible.
    """
    return await get_captcha()


@router.get("/captcha/status", response_model=CaptchaStatusResponse)
async def captcha_status() -> CaptchaStatusResponse:
    """
    Endpoint para verificar el estado del servicio de captcha.
    """
    try:
        # Realizar una petición simple para verificar que SAES está disponible
        response = requests.get("https://www.saes.upiicsa.ipn.mx/", timeout=5)
        if response.status_code == 200:
            return {"status": "online", "message": "Servicio SAES disponible"}
        else:
            return {"status": "unavailable", "message": f"SAES respondió con código {response.status_code}"}
    except requests.RequestException:
        return {"status": "offline", "message": "No se pudo conectar con SAES"}


    