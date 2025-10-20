import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from main import app

client = TestClient(app)

class TestLoginRoutes:
    """Test class for login routes"""

    @patch('routes.login.requests.Session')
    def test_login_success(self, mock_session):
        """Test successful login and data extraction"""
        # Mock HTML response del login
        mock_login_html = '''
        <html>
            <body>
                <span id="ctl00_leftColumn_LoginUser_FailureText"></span>
            </body>
        </html>
        '''
        
        # Mock HTML response del mapa curricular
        mock_mapa_html = '''
        <html>
            <body>
                <select name="ctl00$mainCopy$Filtro$cboCarrera">
                    <option value="A" selected="selected">ADMINISTRACION INDUSTRIAL</option>
                    <option value="I">INGENIERIA INDUSTRIAL</option>
                </select>
                <select name="ctl00$mainCopy$Filtro$cboPlanEstud">
                    <option value="05">Plan del 1/5/1998</option>
                    <option value="09">Plan del 1/8/2009</option>
                </select>
                <select name="ctl00$mainCopy$Filtro$lsNoPeriodos">
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                </select>
            </body>
        </html>
        '''
        
        # Configure mock session
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock the login response
        mock_login_response = Mock()
        mock_login_response.content = mock_login_html.encode('utf-8')
        mock_login_response.status_code = 200
        
        # Mock the mapa curricular response
        mock_mapa_response = Mock()
        mock_mapa_response.content = mock_mapa_html.encode('utf-8')
        mock_mapa_response.status_code = 200
        
        # Configure session mock to return appropriate responses
        def side_effect(url, **kwargs):
            if 'mapa_curricular' in url:
                return mock_mapa_response
            else:
                return mock_login_response
        
        mock_session_instance.get.side_effect = side_effect
        mock_session_instance.post.return_value = mock_login_response
        
        # Prepare login data
        login_data = {
            "session_id": "test-session-id",
            "boleta": "20231234567",
            "password": "test_password",
            "captcha_code": "ABC123",
            "hidden_fields": {
                "__VIEWSTATE": "test_viewstate",
                "__EVENTVALIDATION": "test_validation"
            },
            "cookies": {
                "ASP.NET_SessionId": "test_cookie"
            }
        }
        
        # Make request
        response = client.post("/login", json=login_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["session_id"] == "test-session-id"
        assert "carrera_info" in data
        
        # Verify carreras
        assert len(data["carrera_info"]["carreras"]) == 2
        assert data["carrera_info"]["carreras"][0]["value"] == "A"
        assert data["carrera_info"]["carreras"][0]["text"] == "ADMINISTRACION INDUSTRIAL"
        
    # Note: Nested planes/periodos are now embedded per carrera/plan; high-level lists removed.

    @patch('routes.login.requests.Session')
    def test_login_failed_credentials(self, mock_session):
        """Test login with wrong credentials"""
        mock_html = '''
        <html>
            <body>
                <span id="ctl00_leftColumn_LoginUser_FailureText">Credenciales incorrectas</span>
            </body>
        </html>
        '''
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.status_code = 200
        
        mock_session_instance.post.return_value = mock_response
        
        login_data = {
            "session_id": "test-session-id",
            "boleta": "20231234567",
            "password": "wrong_password",
            "captcha_code": "WRONG",
            "hidden_fields": {"__VIEWSTATE": "test"},
            "cookies": {"ASP.NET_SessionId": "test"}
        }
        
        response = client.post("/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Credenciales incorrectas" in data["message"]
        assert data["carrera_info"] is None

    @patch('routes.login.requests.Session')
    def test_login_connection_error(self, mock_session):
        """Test login when there's a connection error"""
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Simulate connection error
        mock_session_instance.post.side_effect = Exception("Connection failed")
        
        login_data = {
            "session_id": "test-session-id",
            "boleta": "20231234567",
            "password": "test_password",
            "captcha_code": "ABC123",
            "hidden_fields": {"__VIEWSTATE": "test"},
            "cookies": {"ASP.NET_SessionId": "test"}
        }
        
        response = client.post("/login", json=login_data)
        
        assert response.status_code == 500
        assert "Error interno del servidor" in response.json()["detail"]

    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        incomplete_data = {
            "session_id": "test-session-id",
            "boleta": "20231234567"
            # Missing password, captcha_code, hidden_fields, cookies
        }
        
        response = client.post("/login", json=incomplete_data)
        
        # FastAPI validation should reject this
        assert response.status_code == 422