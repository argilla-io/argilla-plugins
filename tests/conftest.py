import httpx
import pytest
from _pytest.logging import LogCaptureFixture
from argilla import app
from argilla.client.api import active_api
from argilla.client.sdk.users import api as users_api
from argilla.server.commons import telemetry
from starlette.testclient import TestClient

from .helpers import SecuredClient


@pytest.fixture
def telemetry_track_data(mocker):
    client = telemetry._TelemetryClient.get()
    if client:
        # Disable sending data for tests
        client.client = telemetry._configure_analytics(disable_send=True)
        spy = mocker.spy(client, "track_data")

        return spy


@pytest.fixture
def mocked_client(
    monkeypatch,
    telemetry_track_data,
) -> SecuredClient:
    with TestClient(app, raise_server_exceptions=False) as _client:
        client_ = SecuredClient(_client)

        real_whoami = users_api.whoami

        def whoami_mocked(client):
            monkeypatch.setattr(client, "__httpx__", client_)
            return real_whoami(client)

        monkeypatch.setattr(users_api, "whoami", whoami_mocked)

        monkeypatch.setattr(httpx, "post", client_.post)
        monkeypatch.setattr(httpx, "patch", client_.patch)
        monkeypatch.setattr(httpx.AsyncClient, "post", client_.post_async)
        monkeypatch.setattr(httpx, "get", client_.get)
        monkeypatch.setattr(httpx, "delete", client_.delete)
        monkeypatch.setattr(httpx, "put", client_.put)
        monkeypatch.setattr(httpx, "stream", client_.stream)

        rb_api = active_api()
        monkeypatch.setattr(rb_api._client, "__httpx__", client_)

        yield client_
