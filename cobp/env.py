import logging
import sys

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from cobp import paths

LOGGING_LEVEL_TO_VALUE = {
    "INFO": 20,
    "DEBUG": 10,
}


class Env(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="COBP_",
        env_file=paths.DOTENV.as_posix(),
    )

    LOGGING_LEVEL: str = Field(default="INFO")
    GAME_ID: str | None = Field(default=None)
    TEAM: str | None = Field(default=None)
    YEAR: int | None = Field(default=None)
    ONLY_INNING: int | None = Field(default=None)


ENV = Env()
print("Environment:")
print(ENV.model_dump())

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(module)s:%(lineno)d - %(message)s",
    level=LOGGING_LEVEL_TO_VALUE[ENV.LOGGING_LEVEL.upper()],
    stream=sys.stdout,
)
