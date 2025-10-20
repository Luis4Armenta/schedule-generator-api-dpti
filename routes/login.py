import time
import requests
from fastapi import APIRouter, HTTPException
from bs4 import BeautifulSoup
from typing import Dict

from schemas.login import (
    LoginRequest,
    LoginResponse,
    CarreraInfo,
    CarreraOption,
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login_saes(login_data: LoginRequest) -> LoginResponse:
    """
    Realiza el login en el SAES usando la información del captcha y credenciales del usuario,
    luego extrae la información del mapa curricular (carreras, planes de estudio, periodos).
    """
    try:
        session = requests.Session()

        # Restaurar cookies previas del captcha
        for cookie_name, cookie_value in login_data.cookies.items():
            session.cookies.set(cookie_name, cookie_value)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.saes.upiicsa.ipn.mx',
            'Connection': 'keep-alive',
            'Referer': 'https://www.saes.upiicsa.ipn.mx/',
            'Upgrade-Insecure-Requests': '1',
        }

        form_data = {
            'ctl00$leftColumn$LoginUser$UserName': login_data.boleta,
            'ctl00$leftColumn$LoginUser$Password': login_data.password,
            'ctl00$leftColumn$LoginUser$CaptchaCodeTextBox': login_data.captcha_code,
            'ctl00$leftColumn$LoginUser$LoginButton': 'Entrar',
        }
        form_data.update(login_data.hidden_fields)

        login_url = "https://www.saes.upiicsa.ipn.mx/default.aspx"
        login_response = session.post(login_url, data=form_data, headers=headers, timeout=15, allow_redirects=True)

        if login_response.status_code != 200:
            raise HTTPException(status_code=401, detail=f"Error en el login: código de estado {login_response.status_code}")

        soup_login = BeautifulSoup(login_response.content, 'html.parser')
        error_message = soup_login.find('span', {'id': 'ctl00_leftColumn_LoginUser_FailureText'})
        if error_message and error_message.text.strip():
            return LoginResponse(
                status="error",
                message=f"Login fallido: {error_message.text.strip()}",
                session_id=login_data.session_id,
                carrera_info=None,
            )

        mapa_curricular_url = "https://www.saes.upiicsa.ipn.mx/Academica/mapa_curricular.aspx"
        mapa_response = session.get(mapa_curricular_url, headers=headers, timeout=15)
        if mapa_response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Error al acceder al mapa curricular: código {mapa_response.status_code}")

        soup = BeautifulSoup(mapa_response.content, 'html.parser')

        select_carrera = soup.find('select', {'name': 'ctl00$mainCopy$Filtro$cboCarrera'})
        if not select_carrera:
            raise HTTPException(status_code=404, detail="No se encontró el select de carreras")

        def extract_hidden_fields(soup_doc: BeautifulSoup) -> Dict[str, str]:
            fields: Dict[str, str] = {}
            for input_tag in soup_doc.find_all('input', {'type': 'hidden'}):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    fields[name] = value
            return fields

        current_hidden = extract_hidden_fields(soup)
        carrera_select_name = 'ctl00$mainCopy$Filtro$cboCarrera'
        plan_select_name = 'ctl00$mainCopy$Filtro$cboPlanEstud'
        periodo_select_name = 'ctl00$mainCopy$Filtro$lsNoPeriodos'

        carreras = []
        for option in select_carrera.find_all('option'):
            carrera_value = option.get('value', '')
            carrera_text = option.text.strip()
            if not carrera_value or not carrera_text:
                continue
            planes = []
            try:
                post_data = {
                    **current_hidden,
                    '__EVENTTARGET': carrera_select_name,
                    '__EVENTARGUMENT': '',
                    carrera_select_name: carrera_value,
                }
                resp_carrera = session.post(mapa_curricular_url, data=post_data, headers=headers, timeout=15, allow_redirects=True)
                if resp_carrera.status_code != 200:
                    carreras.append({'value': carrera_value, 'text': carrera_text, 'planes': []})
                    continue
                soup_carrera = BeautifulSoup(resp_carrera.content, 'html.parser')
                current_hidden = extract_hidden_fields(soup_carrera)
                time.sleep(0.2)

                select_plan = soup_carrera.find('select', {'name': plan_select_name})
                if select_plan:
                    for plan_option in select_plan.find_all('option'):
                        plan_value = plan_option.get('value', '')
                        plan_text = plan_option.text.strip()
                        if not plan_value or not plan_text:
                            continue
                        periodos = []
                        try:
                            post_data_plan = {
                                **current_hidden,
                                '__EVENTTARGET': plan_select_name,
                                '__EVENTARGUMENT': '',
                                carrera_select_name: carrera_value,
                                plan_select_name: plan_value,
                            }
                            resp_plan = session.post(mapa_curricular_url, data=post_data_plan, headers=headers, timeout=15, allow_redirects=True)
                            if resp_plan.status_code == 200:
                                soup_plan = BeautifulSoup(resp_plan.content, 'html.parser')
                                select_periodo = soup_plan.find('select', {'name': periodo_select_name})
                                if select_periodo:
                                    for per_option in select_periodo.find_all('option'):
                                        per_value = per_option.get('value', '')
                                        per_text = per_option.text.strip()
                                        if per_value and per_text:
                                            periodos.append({'value': per_value, 'text': per_text})
                                time.sleep(0.15)
                        except requests.RequestException:
                            pass
                        planes.append({'value': plan_value, 'text': plan_text, 'periodos': periodos})
            except requests.RequestException:
                pass
            carreras.append({'value': carrera_value, 'text': carrera_text, 'planes': planes})

        carrera_info = CarreraInfo(carreras=[CarreraOption(**c) for c in carreras])

        return LoginResponse(
            status="success",
            message="Login exitoso y datos del mapa curricular extraídos correctamente",
            session_id=login_data.session_id,
            carrera_info=carrera_info,
        )

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error de conexión con SAES: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
