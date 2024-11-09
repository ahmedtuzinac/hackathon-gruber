import httpx
from httpx import Response
from typing import Dict, List, AnyStr, Optional
import pprint

from .test_base import TestBase
from .assets import *
from schemas import *


class TestTenderAIBot(TestBase):

    async def test_get_available_cities(self):
        response = await self.api('GET', '/dispatcher/cities')
        assert response.status_code == 200
        pprint.pprint(response.json())

    async def test_start_conversation(self):
        response = await self.api('GET', '/dispatcher/cities')
        assert response.status_code == 200
        len_of_cities: int = len(response.json())
        import random
        idx = random.randint(0, len_of_cities - 1)
        load_address = response.json()[idx]
        response.json().pop(idx)
        idx = random.randint(0, len_of_cities - 2)
        unload_address = response.json()[idx]

        schema: DispatchSchema = DispatchSchema(
            load_address=AddressSchema(
                city=load_address['city'],
                country=load_address['country']
            ),
            unload_address=AddressSchema(
                city=unload_address['city'],
                country=unload_address['country']
            ),
            price=2000.0
        )
        response = await self.api('POST', '/dispatcher', _body=schema.dict())

        id_conversation = response.json()['id_conversation']

        async with httpx.AsyncClient(app=self.app, base_url='http://test') as client:
            response = await client.patch(
                '/dispatcher',
                json={
                    'id_conversation': id_conversation,
                    'message': 'Can we go a little bit lower with price?'
                }
            )
        ...

