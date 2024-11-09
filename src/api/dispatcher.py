from fastapi import APIRouter

from config.application import service
from utils import *
from schemas import DispatchSchema

router: APIRouter = APIRouter(
    tags=['DispatcherBot API']
)


@router.get('/cities')
async def get_cities():
    return await get_available_cities()


@router.post('')
async def start_an_order(payload: DispatchSchema):
    load_city = payload.load_address.city
    load_country = payload.load_address.country

    unload_city = payload.unload_address.city
    unload_country = payload.unload_address.country

    def get_transports_by_supplier(supplier_id, transports):
        return [transport for transport in transports if transport['supplierId'] == supplier_id]

    transport_list: list[dict] = await get_transport_history()
    partner_list: list[dict] = await get_partners()
    partners_string: str = ''
    for partner in partner_list:
        partners_string += (f'Partner(id={partner["id"]}, city={partner["address"]["city"]}, country={partner["address"]["country"]}, latitude={partner["address"]["latitude"]},'
                            f' longitude={partner["address"]["longitude"]}, language={partner["language"]}, name={partner["name"]} | ')

        id_partner = partner['id']
        transports = get_transports_by_supplier(id_partner, transport_list)

        partners_string += f' Transports done by this partner, {transports}'

    response_format: str = (
        "{'partner_name': '...', 'reason': 'Describe why you have choose this partner. Include as much parametars as you can', 'minimum_price': '...', 'direct_message': '...'}"
    )
    prompt: str = (
        'You are a dispatcher for logistics company, '
        'Train yourself with those data: '
        f'Your available partners are (you will have also a transports done by every partner, ({partners_string}),'
        f'Your task is next:'
        f'We have a request to load goods in {load_city}, {load_country} and transport it to {unload_city}, {unload_country},'
        f'find a best suitable partner and price from provided data, '
        f'you have a history of every partner their longitude and latitude and other specific data, '
        f'do the calculations which partner will give a best possible results. '
        f'Also you have to make a direct message to a partner in their language and offer them the job. Price is provided to you, '
        f'but you can calculate minimum price with 5% profit on this job.'
        f'Respond to me in json format: {response_format}'
    )
    response_message = await set_task_gemini(
        message=prompt
    )

    return {
        'work_in_progres': True
    }


service.include_router(router, prefix='/dispatcher')
