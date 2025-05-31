#!/usr/bin/alias python3
# -*- coding: utf-8 -*-
# @Time    : 2024/07/17
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : setting
# @Software: PyCharm
import os.path
from functools import lru_cache
from typing import Type

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, YamlConfigSettingsSource

from constants.constants import Constants
from domain.emuns.chroma_mode import ChromaMode
from domain.emuns.model_provider import ModelType
from domain.emuns.qdrant_mode import QdrantMode
from domain.emuns.vector_type import VectorType


class ServerSettings(BaseModel):
    host: str = Field('0.0.0.0')
    port: int = Field(8080)
    reload: bool = Field(True)


class LogSettings(BaseModel):
    level: str = Field(default="INFO")
    file: bool = Field(default=False)
    debug: bool = Field(default=False)


class PGVectorSettings(BaseSettings):
    db: str
    host: str
    port: int
    user: str
    password: str


class QdrantDiskSettings(BaseSettings):
    path: str = Field(default=Constants.Path.QDRANT_DEFAULT_DISK_PATH)

    @model_validator(mode='before')
    def handle_path(self):
        if not os.path.isabs(self['path']):
            self['path'] = os.path.join(Constants.Path.ROOT_PATH, self['path'])
        return self


class QdrantRemoteSettings(BaseSettings):
    host: str
    port: int = Field(default=6333)


class QdrantSettings(BaseSettings):
    mode: QdrantMode
    disk: QdrantDiskSettings | None
    remote: QdrantRemoteSettings | None
    memory: None

    @model_validator(mode='before')
    def clear_conflicting_settings(self):
        for key in [member for member in QdrantMode if member != self['mode']]:
            self[key] = None
        return self


class ChromaDiskSettings(BaseSettings):
    path: str = Field(default=Constants.Path.QDRANT_DEFAULT_DISK_PATH)

    @model_validator(mode='before')
    def handle_path(self):
        if not os.path.isabs(self['path']):
            self['path'] = os.path.join(Constants.Path.ROOT_PATH, self['path'])
        return self


class ChromaRemoteSettings(BaseSettings):
    host: str
    port: int = Field(default=6333)
    ssl: bool = Field(default=False)


class ChromaSettings(BaseSettings):
    mode: ChromaMode
    disk: ChromaDiskSettings | None
    remote: ChromaRemoteSettings | None
    memory: None

    @model_validator(mode='before')
    def clear_conflicting_settings(self):
        for key in [member for member in ChromaMode if member != self['mode']]:
            self[key] = None
        return self


class VectorSettings(BaseSettings):
    platform: VectorType
    code2desc: bool = Field(default=False)
    chat_provider: ModelType = Field(default='openai', alias='chat-provider')
    chat_model: str = Field(default='gpt-4o-mini', alias='chat-model')
    embedding_provider: ModelType = Field(default='openai', alias='embedding-provider')
    embedding_model: str = Field(default='text-embedding-3-small', alias='embedding-model')
    pgvector: PGVectorSettings | None
    qdrant: QdrantSettings | None
    chroma: ChromaSettings | None

    @model_validator(mode='before')
    def clear_conflicting_settings(self):
        for key in [member for member in VectorType if member != self['platform']]:
            self[key] = None
        return self


class We0IndexSettings(BaseModel):
    application: str
    log: LogSettings
    server: ServerSettings
    vector: VectorSettings


class AppSettings(BaseSettings):
    we0_index: We0IndexSettings | None = Field(default=None, alias='we0-index')

    model_config = SettingsConfigDict(
        yaml_file=Constants.Path.YAML_FILE_PATH,
        yaml_file_encoding='utf-8',
        extra='ignore'
    )

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache
def get_we0_index_settings() -> We0IndexSettings:
    app_settings = AppSettings()
    return app_settings.we0_index


if __name__ == '__main__':
    settings = get_we0_index_settings()
    print(settings.model_dump_json(indent=4))
