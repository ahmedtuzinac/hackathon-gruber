from tortoise import fields

from .base import Base
from tortoise.models import Model


class Option(Model, Base):
    key = fields.CharField(max_length=255, unique=True)
    value = fields.JSONField(null=True)

    class Meta:
        table = 'options'
