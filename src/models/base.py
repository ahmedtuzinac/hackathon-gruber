from tortoise import fields


class Base:
    """
    A base model class that includes common fields for all models.
    """

    id = fields.UUIDField(pk=True)
    created = fields.DatetimeField(auto_now=True)
    last_updated = fields.DatetimeField(auto_now_add=True)


class Conversation(Base):
    ...
