import json
import uuid

from fastapi import APIRouter, HTTPException

from config.application import service
from models import Conversation
from schemas import DispatchSchema, MessageSchema
from utils import *

router: APIRouter = APIRouter(
    tags=['Knowledge API']
)


@router.get('/init')
async def init_knowledge():
    ...


service.include_router(router, prefix='/api/knowledge')
