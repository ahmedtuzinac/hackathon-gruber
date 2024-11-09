import importlib

import pytest
import httpx
from httpx import Response

from typing import Dict, Optional, AnyStr, LiteralString

from config.application import shutdown_event, startup_event, service


class TestBase:

    async def setup(self):
        self.import_modules(['service'])

    def import_modules(self, svcs):
        for svc in svcs:
            importlib.reload(importlib.import_module(svc))

        self.app = service

    @pytest.fixture(autouse=True, scope="function")
    async def setup_fixture(self) -> None:
        """
        Fixture for tests of application.
        It will be executed everytime before each test and after.

        decorator:
            @pytest.fixture(autouse=True, scope="function")
                autouse (bool): If true this fixture will be executed
                                brefore and after every test.
                scope (str): This fixture is meant for function tests.

        :return: None
        """

        await startup_event()
        await self.setup()
        yield
        await shutdown_event()

    async def api(self, _method: AnyStr, _endpoint: AnyStr, _body: Optional[Dict] = None) -> Response | Dict:
        _method = _method.lower()

        params: Dict = {
            'url': _endpoint,
        }
        if _method != 'get':
            params['json'] = _body if _body else {}

        async with httpx.AsyncClient(app=self.app, base_url='https://test') as client:
            func = getattr(client, _method, None)

            response = await func(**params)

        return response
