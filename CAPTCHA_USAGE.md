# Ejemplo de uso de la API de Captcha

## Instalación de dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar la API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints disponibles

### 1. Obtener captcha del SAES
```
GET /captcha
```

**Respuesta:**
```json
{
  "session_id": "uuid-generado",
  "captcha_image": {
    "base64": "iVBORw0KGgoAAAANSUhEUgAA...", 
    "content_type": "image/png",
    "src": "https://www.saes.upiicsa.ipn.mx/captcha.aspx?id=12345"
  },
  "captcha_div": {
    "html": "<div class=\"LBD_CaptchaImageDiv\" id=\"c_default_ctl00_leftcolumn_loginuser_logincaptcha_CaptchaImageDiv\">...</div>",
    "class": ["LBD_CaptchaImageDiv"],
    "id": "c_default_ctl00_leftcolumn_loginuser_logincaptcha_CaptchaImageDiv"
  },
  "hidden_fields": {
    "__VIEWSTATE": "/wEPDwUKLTY4MDI5...",
    "__EVENTVALIDATION": "/wEWAwKl6s..."
  },
  "cookies": {
    "ASP.NET_SessionId": "2mxkp2..."
  },
  "timestamp": "Sat, 12 Oct 2025 10:00:00 GMT",
  "status": "success"
}
```

### 2. Refrescar captcha
```
GET /captcha/refresh
```

### 3. Estado del servicio
```
GET /captcha/status
```

**Respuesta:**
```json
{
  "status": "online",
  "message": "Servicio SAES disponible"
}
```

### 4. Login y obtener información del mapa curricular
```
POST /login
```

**Cuerpo de la petición:**
```json
{
  "session_id": "uuid-del-captcha",
  "boleta": "20231234567",
  "password": "mi_password",
  "captcha_code": "ABC123",
  "hidden_fields": {
    "__VIEWSTATE": "valor-del-captcha",
    "__EVENTVALIDATION": "valor-del-captcha"
  },
  "cookies": {
    "ASP.NET_SessionId": "valor-del-captcha"
  }
}
```

**Respuesta exitosa:**
```json
{
  "status": "success",
  "message": "Login exitoso y datos del mapa curricular extraídos correctamente",
  "session_id": "uuid-del-captcha",
  "carrera_info": {
    "carreras": [
      {
        "value": "A",
        "text": "ADMINISTRACION INDUSTRIAL",
        "planes": [
          {
            "value": "05",
            "text": "Plan del 1/5/1998",
            "periodos": [
              { "value": "1", "text": "1" },
              { "value": "2", "text": "2" }
            ]
          },
          {
            "value": "09",
            "text": "Plan del 1/8/2009",
            "periodos": [
              { "value": "1", "text": "1" },
              { "value": "2", "text": "2" },
              { "value": "3", "text": "3" }
            ]
          }
        ]
      },
      {
        "value": "I",
        "text": "INGENIERIA INDUSTRIAL",
        "planes": [
          {
            "value": "14",
            "text": "Plan 2014",
            "periodos": [
              { "value": "A", "text": "A" },
              { "value": "B", "text": "B" }
            ]
          }
        ]
      }
    ]
  }
}
```

**Respuesta de error:**
```json
{
  "status": "error",
  "message": "Login fallido: Captcha incorrecto",
  "session_id": "uuid-del-captcha",
  "carrera_info": null
}
```

## Ejemplo de uso en JavaScript (Frontend)

```javascript
// Obtener captcha
async function getCaptcha() {
    try {
        const response = await fetch('http://localhost:8000/captcha');
        const data = await response.json();
        
        // Mostrar imagen del captcha
        const imgElement = document.createElement('img');
        imgElement.src = `data:${data.captcha_image.content_type};base64,${data.captcha_image.base64}`;
        document.getElementById('captcha-container').appendChild(imgElement);
        
        // Guardar información de sesión para envío posterior
        sessionStorage.setItem('captcha_session', JSON.stringify({
            session_id: data.session_id,
            hidden_fields: data.hidden_fields,
            cookies: data.cookies
        }));
        
        return data;
    } catch (error) {
        console.error('Error al obtener captcha:', error);
    }
}

// Verificar estado del servicio
async function checkCaptchaStatus() {
    try {
        const response = await fetch('http://localhost:8000/captcha/status');
        const status = await response.json();
        console.log('Estado del servicio:', status);
        return status;
    } catch (error) {
        console.error('Error al verificar estado:', error);
    }
}
```

## Ejemplo de uso en Python

```python
import requests
import base64
from PIL import Image
from io import BytesIO

def get_captcha():
    """Obtiene el captcha del SAES"""
    try:
        response = requests.get('http://localhost:8000/captcha')
        response.raise_for_status()
        data = response.json()
        
        # Decodificar imagen base64
        img_data = base64.b64decode(data['captcha_image']['base64'])
        img = Image.open(BytesIO(img_data))
        
        # Guardar imagen localmente (opcional)
        img.save(f"captcha_{data['session_id']}.png")
        
        print(f"Captcha obtenido con ID de sesión: {data['session_id']}")
        return data
        
    except requests.RequestException as e:
        print(f"Error al obtener captcha: {e}")
        return None

# Usar la función
captcha_data = get_captcha()
if captcha_data:
    print("Campos ocultos encontrados:", captcha_data['hidden_fields'].keys())
    print("Cookies de sesión:", captcha_data['cookies'].keys())
```

## Ejemplo completo: Flujo de Login

```javascript
// 1. Obtener el captcha
async function obtenerCaptcha() {
    const response = await fetch('http://localhost:3000/captcha');
    const captchaData = await response.json();
    
    // Mostrar imagen
    document.getElementById('captcha-img').src = 
        `data:${captchaData.captcha_image.content_type};base64,${captchaData.captcha_image.base64}`;
    
    // Guardar datos para el login
    localStorage.setItem('captcha_data', JSON.stringify(captchaData));
    
    return captchaData;
}

// 2. Realizar login con los datos del captcha
async function realizarLogin(boleta, password, captchaCode) {
    const captchaData = JSON.parse(localStorage.getItem('captcha_data'));
    
    const loginRequest = {
        session_id: captchaData.session_id,
        boleta: boleta,
        password: password,
        captcha_code: captchaCode,
        hidden_fields: captchaData.hidden_fields,
        cookies: captchaData.cookies
    };
    
  const response = await fetch('http://localhost:3000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(loginRequest)
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
        console.log('Login exitoso!');
        console.log('Carreras disponibles:', result.carrera_info.carreras);
        console.log('Planes de estudio:', result.carrera_info.planes_estudio);
        console.log('Periodos:', result.carrera_info.periodos);
        
        // Guardar información del usuario
        localStorage.setItem('user_carrera_info', JSON.stringify(result.carrera_info));
        
        return result;
    } else {
        console.error('Login fallido:', result.message);
        // Refrescar captcha si falló
        await obtenerCaptcha();
        return null;
    }
}

// 3. Uso completo
async function loginCompleto() {
    // Paso 1: Obtener captcha
    await obtenerCaptcha();
    
    // Paso 2: Usuario ingresa sus datos y resuelve captcha
    const boleta = document.getElementById('boleta').value;
    const password = document.getElementById('password').value;
    const captchaCode = document.getElementById('captcha-code').value;
    
    // Paso 3: Realizar login
    const resultado = await realizarLogin(boleta, password, captchaCode);
    
    if (resultado) {
        // Paso 4: Usar la información obtenida
        const carreraInfo = resultado.carrera_info;
        
        // Llenar select de carreras
        const selectCarrera = document.getElementById('select-carrera');
        carreraInfo.carreras.forEach(carrera => {
            const option = document.createElement('option');
            option.value = carrera.value;
            option.text = carrera.text;
            selectCarrera.appendChild(option);
        });
        
        // Llenar select de planes de estudio
        const selectPlan = document.getElementById('select-plan');
        carreraInfo.planes_estudio.forEach(plan => {
            const option = document.createElement('option');
            option.value = plan.value;
            option.text = plan.text;
            selectPlan.appendChild(option);
        });
        
        // Llenar select de periodos
        const selectPeriodo = document.getElementById('select-periodo');
        carreraInfo.periodos.forEach(periodo => {
            const option = document.createElement('option');
            option.value = periodo.value;
            option.text = periodo.text;
            selectPeriodo.appendChild(option);
        });
    }
}
```

## Notas importantes

1. **Sesión única**: Cada llamada genera un nuevo `session_id` único para rastrear la sesión del captcha.

2. **Campos ocultos**: La respuesta incluye campos como `__VIEWSTATE` y `__EVENTVALIDATION` que son necesarios para enviar formularios al SAES.

3. **Cookies**: Se incluyen las cookies de sesión necesarias para mantener el estado con el servidor del SAES.

4. **Imagen en Base64**: La imagen del captcha se devuelve codificada en Base64 para facilitar su uso en frontends web.

5. **Timeout**: Las peticiones tienen un timeout de 10-15 segundos para evitar bloqueos.

6. **Manejo de errores**: La API incluye manejo robusto de errores con códigos HTTP apropiados.

7. **Flujo completo**: Debes obtener el captcha ANTES de hacer login, y usar el mismo `session_id`, `hidden_fields` y `cookies` en ambas peticiones.