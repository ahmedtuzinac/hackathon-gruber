import json
import uuid

from fastapi import APIRouter, HTTPException

from config.application import service
from models import Conversation
from schemas import DispatchSchema
from utils import *

router: APIRouter = APIRouter(
    tags=['DispatcherBot API']
)


@router.get('/cities')
async def get_cities():
    return await get_available_cities()


def extract_json(response):
    response = response.replace('\n', '')

    json_start = response.index("{")
    json_end = response.rfind("}")
    return json.loads(response[json_start:json_end + 1])


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
    partners: dict = dict()
    for partner in partner_list:
        partners[partner['id']] = {
            'city': partner['address']['city'],
            'country': partner['address']['country'],
            'name': partner['name'],
            'language': partner['language'],
            'transports': [
                {
                    'load_city': transport['loadingAddress']['city'],
                    'load_country': transport['loadingAddress']['country'],
                    'unload_city': transport['unloadingAddress']['city'],
                    'unload_country': transport['unloadingAddress']['country'],
                    'price': transport['price'],
                    'performance_score': transport['performanceScore']
                } for transport in get_transports_by_supplier(partner['id'], transport_list)
            ]
        }

    response_format: str = '{"partner_name": "...", "reason_why_you_choose_this_partner": "...", "minimal_price": "...", "direct_message": "..."}'
    prompt: str = (
        'You are a dispatcher for logistics company "Gruber Logistics"'
        f'Partners data: {partners}\n'

        f'Your task is next:'
        f'We have a request to load goods in {load_city}, {load_country} and transport it to {unload_city}, {unload_country},'
        f'find a best suitable partner and price from provided data, '
        f'you have a history of every partner their longitude and latitude and other specific data, '
        f'do the calculations which partner will give a best possible results. '
        f'Also you have to make a direct message to a partner in their language and offer them the job. Price is provided to you, '
        f'but you can calculate minimum price with 5% profit on this job.'
        f'You have to give thus answers '
        f'partner_name(name of the choosen partner),'
        f'reason_why_you_choose_this_partner(describe by which params you choosed partner),'
        f'minimal_price(minimal price for a job)'
        f'direct_message(direct message to a partner in native language of the partner, which contains job offer)'
        f'Please give an output in JSON format({response_format})'
    )
    response_message = await set_task_gemini(
        message=prompt
    )

    response = extract_json(response_message)

    context = dict()

    context['partner_name'] = response['partner_name']
    context['minimal_price'] = response['minimal_price']
    context['reason_why_you_choose_this_partner'] = response['reason_why_you_choose_this_partner']
    context['direct_message'] = response['direct_message']

    conversation: Conversation = await Conversation.create(
        context=context
    )

    response['id_conversation'] = conversation.id
    return response


@router.patch('')
async def send_message(payload: MessageSchema):
    conversation = await Conversation.filter(id=id_conversation).get_or_none()

    if conversation.number_of_received_messages >= 5:
        raise HTTPException(status_code=406, detail="I'am tired... Please just go away...")

    context = conversation.context




service.include_router(router, prefix='/dispatcher')
