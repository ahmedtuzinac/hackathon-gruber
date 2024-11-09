from tortoise import Tortoise
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f'postgres://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},

    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

print(TORTOISE_ORM)


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
