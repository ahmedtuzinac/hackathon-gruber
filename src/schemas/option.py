from pydantic import BaseModel
from typing import List, Dict, Optional, AnyStr


class OptionCreateModel(BaseModel):
    key: AnyStr
    value: Dict


class OptionResponseModel(BaseModel):
    key: AnyStr
    value: Dict


class OptionsResponseModel(BaseModel):
    options: List[OptionResponseModel]


class OptionUpdateRequestModel(BaseModel):
    value: Dict
