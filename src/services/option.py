from fastapi import Response, HTTPException
from typing import List, Optional, Dict

from models import Option
from schemas import *


class OptionService:
    _model: Option = Option

    async def get(self) -> OptionsResponseModel:
        options: List[Option] = await Option.all()

        return_dict: Dict = {
            'options': [OptionResponseModel(**x.__dict__) for x in options]
        }
        return OptionsResponseModel(**return_dict)

    async def single(self, key: AnyStr, inner: bool = False) -> OptionResponseModel:
        option: Option | None = await Option.get_or_none(key=key)
        if not option:
            raise HTTPException(detail='Option not found', status_code=404)

        if inner:
            return option
        return OptionResponseModel(**option.__dict__)

    async def create(self, option: OptionCreateModel) -> OptionResponseModel:
        option: Option = await Option.create(**option.dict())
        await option.save()

        return OptionResponseModel(**option.__dict__)

    async def update(self, key: AnyStr, option_request: OptionUpdateRequestModel) -> OptionResponseModel:
        option: Option = await self.single(key=key, inner=True)

        if option_request.value != option.value:
            option.value = option_request.value
            await option.save()

        return OptionResponseModel(**option.__dict__)

    async def delete(self, key: AnyStr) -> None:
        option: Option = await self.single(key=key, inner=True)
        await option.delete()

        return
