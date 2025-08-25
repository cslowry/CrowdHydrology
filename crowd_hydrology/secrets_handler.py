import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields

import yaml
from dotenv import load_dotenv


@dataclass
class AbstractSecretsHandler(ABC):
    """
    Abstract class for handling secrets and environment variables.

    Extend this class to implement a different secrets handler in the future.
    """

    DJANGO_SECRET_KEY: str = field(init=False)  # Django secret key
    DEBUG_MODE: bool = field(init=False)  # Django debug mode
    ALLOWED_HOSTS: list[str] = field(init=False)

    # Twilio credentials
    TWILIO_ACCOUNT_SID: str = field(init=False)
    TWILIO_AUTH_TOKEN: str = field(init=False)

    # Plotly credentials
    PLOTLY_USERNAME: str = field(init=False)
    PLOTLY_API_KEY: str = field(init=False)

    # Database
    DB_NAME: str = field(init=False)

    # Gemini
    GEMINI_API_KEY: str = field(init=False)

    # REDIS
    CONTRIBUTION_OTP_TTL: str = field(
        init=True, default=86400
    )  # time to live for contribution OTP | default: 24 hrs

    def __init__(self):
        self._obtain_all_secrets()

    @abstractmethod
    def _obtain_all_secrets(self):
        raise NotImplementedError()

    @abstractmethod
    def get_secret(self, key: str):
        return self.__getattribute__(key)


@dataclass
class DotEnvSecretsHandler(AbstractSecretsHandler):
    """
    Environment variable handler through .env
    """

    def __init__(self):
        load_dotenv()
        super().__init__()

    def _obtain_all_secrets(self):
        for fld in fields(self):
            self.__setattr__(
                fld.name, fld.type(os.environ.get(fld.name))
            )  # parse and set

    def get_secret(self, key):
        return super().get_secret(key)


@dataclass
class YamlEnvSecretsHandler(AbstractSecretsHandler):
    """
    Environment variable handler through YAML file
    """

    def __init__(self, yaml_file_path: str):
        self.yaml_file_path = yaml_file_path
        super().__init__()

    def _obtain_all_secrets(self):
        with open(self.yaml_file_path, "r") as file:
            secrets = yaml.safe_load(file)
            for fld in fields(self):
                if fld.name in secrets:
                    self.__setattr__(fld.name, fld.type(secrets[fld.name]))

    def get_secret(self, key):
        return super().get_secret(key)


if __name__ == "__main__":
    handler = DotEnvSecretsHandler()
