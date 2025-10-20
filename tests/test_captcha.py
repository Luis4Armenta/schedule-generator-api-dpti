import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
import base64

from main import app

client = TestClient(app)

class TestCaptchaRoutes:
    """Test class for captcha routes"""

    @patch('routes.captcha.requests.Session')
    def test_get_captcha_success(self, mock_session):
        """Test successful captcha extraction"""
        # Mock HTML response with captcha div
        mock_html = '''
        <html>
            <body>
                <div class="LBD_CaptchaImageDiv" id="c_default_ctl00_leftcolumn_loginuser_logincaptcha_CaptchaImageDiv">
                    <img src="/captcha.aspx?id=12345" alt="captcha" />
                </div>
                <input type="hidden" name="__VIEWSTATE" value="test_viewstate" />
                <input type="hidden" name="__EVENTVALIDATION" value="test_validation" />
            </body>
        </html>
        '''
        
        # Mock image response
        mock_image_data = b'fake_image_data'
        
        # Configure mock session
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock the main page response
        mock_main_response = Mock()
        mock_main_response.content = mock_html.encode('utf-8')
        mock_main_response.status_code = 200
        mock_main_response.headers = {'date': '2025-10-12T10:00:00Z'}
        
        # Mock the image response
        mock_img_response = Mock()
        mock_img_response.content = mock_image_data
        mock_img_response.status_code = 200
        mock_img_response.headers = {'content-type': 'image/png'}
        
        # Configure session mock to return appropriate responses
        def side_effect(url, **kwargs):
            if 'captcha.aspx' in url:
                return mock_img_response
            else:
                return mock_main_response
        
        mock_session_instance.get.side_effect = side_effect
        mock_session_instance.cookies = {'session': 'test_cookie'}
        
        # Make request
        response = client.get("/captcha")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "captcha_image" in data
        assert "captcha_div" in data
        assert "hidden_fields" in data
        assert "cookies" in data
        assert data["status"] == "success"
        
        # Check captcha image
        assert data["captcha_image"]["base64"] == base64.b64encode(mock_image_data).decode('utf-8')
        assert data["captcha_image"]["content_type"] == "image/png"
        assert "captcha.aspx" in data["captcha_image"]["src"]
        
        # Check hidden fields
        assert data["hidden_fields"]["__VIEWSTATE"] == "test_viewstate"
        assert data["hidden_fields"]["__EVENTVALIDATION"] == "test_validation"
        
        # Check cookies
        assert data["cookies"]["session"] == "test_cookie"

    @patch('routes.captcha.requests.Session')
    def test_get_captcha_no_div_found(self, mock_session):
        """Test when captcha div is not found"""
        mock_html = '<html><body><div>No captcha here</div></body></html>'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.status_code = 200
        mock_session_instance.get.return_value = mock_response
        
        response = client.get("/captcha")
        
        assert response.status_code == 404
        assert "No se pudo encontrar el div del captcha" in response.json()["detail"]

    @patch('routes.captcha.requests.Session')
    def test_get_captcha_connection_error(self, mock_session):
        """Test when there's a connection error to SAES"""
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Simulate connection error
        mock_session_instance.get.side_effect = Exception("Connection failed")
        
        response = client.get("/captcha")
        
        assert response.status_code == 500
        assert "Error interno del servidor" in response.json()["detail"]

    def test_refresh_captcha(self):
        """Test captcha refresh endpoint"""
        with patch('routes.captcha.get_captcha') as mock_get_captcha:
            mock_response = {
                "session_id": "test_session",
                "captcha_image": {
                    "base64": "test_base64",
                    "content_type": "image/png",
                    "src": "test_src"
                },
                "captcha_div": {
                    "html": "<div>test</div>",
                    "class": ["LBD_CaptchaImageDiv"],
                    "id": "test_id"
                },
                "hidden_fields": {},
                "cookies": {},
                "status": "success"
            }
            mock_get_captcha.return_value = mock_response
            
            response = client.get("/captcha/refresh")
            
            assert response.status_code == 200
            mock_get_captcha.assert_called_once()

    @patch('routes.captcha.requests.get')
    def test_captcha_status_online(self, mock_get):
        """Test captcha status when SAES is online"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        response = client.get("/captcha/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "disponible" in data["message"]

    @patch('routes.captcha.requests.get')
    def test_captcha_status_offline(self, mock_get):
        """Test captcha status when SAES is offline"""
        mock_get.side_effect = Exception("Connection failed")
        
        response = client.get("/captcha/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "offline"
        assert "No se pudo conectar" in data["message"]