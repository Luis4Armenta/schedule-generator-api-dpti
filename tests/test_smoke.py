def test_home_message():
    # Importar la función que sirve la ruta '/' sin ejecutar eventos de startup
    from main import message
    resp = message()
    # HTMLResponse tiene .body que es bytes
    body = resp.body.decode('utf-8') if hasattr(resp, 'body') else str(resp)
    assert 'Profesores API' in body
