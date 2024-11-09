from pydantic import BaseModel


class AddressSchema(BaseModel):
    city: str
    country: str
class DispatchSchema(BaseModel):
    load_address: AddressSchema
    unload_address: AddressSchema



