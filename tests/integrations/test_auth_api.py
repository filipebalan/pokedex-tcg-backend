import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from src.infrastructure.web.main import app

@pytest.mark.asyncio
async def test_deve_registrar_e_autenticar_usuario_gerando_jwt() -> None:
    unique_email = f"treinador_{uuid4().hex[:6]}@pokemon.com"
    password = "senha_super_segura_123"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Registro
        reg_resp = await client.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        assert reg_resp.status_code == 201
        data_user = reg_resp.json()
        assert data_user["email"] == unique_email

        # 2. Login com sucesso (OAuth2 form-data)
        login_resp = await client.post(
            "/auth/login",
            data={"username": unique_email, "password": password}
        )
        assert login_resp.status_code == 200
        data_token = login_resp.json()
        assert "access_token" in data_token
        assert data_token["token_type"] == "bearer"

        # 3. Login com senha errada deve falhar (401)
        fail_resp = await client.post(
            "/auth/login",
            data={"username": unique_email, "password": "senha_errada_aqui"}
        )
        assert fail_resp.status_code == 401