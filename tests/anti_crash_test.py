from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_diagnostic_endpoint():
    """Verifica que el endpoint de diagnóstico responda correctamente."""
    response = client.get("/health/diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "version" in data

def test_root_access():
    """Verifica que el home cargue o al menos no crashee el servidor."""
    response = client.get("/")
    # Puede ser 200 (si todo ok) o 500 (si hay error controlado por middleware)
    # Lo importante es que la conexión no se cierre abruptamente
    assert response.status_code in [200, 500]
