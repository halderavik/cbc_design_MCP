from conjoint_mcp.server import HealthResponse


def test_health_response_model():
    resp = HealthResponse(status="ok", version="0.1.0")
    assert resp.status == "ok"
    assert resp.version == "0.1.0"


