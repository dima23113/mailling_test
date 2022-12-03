from dataclasses import dataclass

from environs import Env


@dataclass
class DjangoSettings:
    secret_key: str
    celery_broker: str
    celery_result: str


@dataclass
class Config:
    django: DjangoSettings


def load_config(path):
    env = Env()
    env.read_env(path)
    return Config(
        django=DjangoSettings(
            secret_key=env.str('SECRET_KEY'),
            celery_broker=env.str('CELERY_BROKER_URL'),
            celery_result=env.str('CELERY_RESULT_BACKEND')
        )
    )
