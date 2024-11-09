from tortoise import fields
from tortoise.models import Model


class Base:
    """
    A base model class that includes common fields for all models.
    """

    id = fields.UUIDField(pk=True)
    created = fields.DatetimeField(auto_now=True)
    last_updated = fields.DatetimeField(auto_now_add=True)


class Conversation(Base, Model):
    context = fields.JSONField(null=True)
    number_of_received_messages = fields.IntField(default=0)

    class Meta:
        table = 'conversations'
