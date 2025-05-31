#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/10/14
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : blob
# @Software: PyCharm
import asyncio
from contextlib import asynccontextmanager, contextmanager
from io import BytesIO
from pathlib import PurePath
from typing import Dict, Any, Generator, BinaryIO

import aiofiles
from pydantic import Field, model_validator, ConfigDict, BaseModel


class Blob(BaseModel):
    id: str | None = None
    filename: str | None = None

    meta: Dict[str, Any] = Field(default_factory=lambda: list)

    data: bytes | str | None = None
    mimetype: str | None = None
    extension: str | None = None
    encoding: str = "utf-8"
    path: str | PurePath | None = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
    )

    @classmethod
    @model_validator(mode="before")
    def check_blob_is_valid(cls, values: dict[str, Any]) -> Any:
        if "data" not in values and "path" not in values:
            msg = "Either data or path must be provided"
            raise ValueError(msg)
        return values

    async def as_string(self) -> str:
        """Read data as a string."""
        if self.data is None and self.path:
            async with aiofiles.open(str(self.path), mode='r', encoding=self.encoding) as f:
                return await f.read()
        elif isinstance(self.data, bytes):
            return self.data.decode(self.encoding)
        elif isinstance(self.data, str):
            return self.data
        else:
            msg = f"Unable to get string for blob {self}"
            raise ValueError(msg)

    def as_bytes(self) -> bytes:
        """Read data as bytes."""
        if isinstance(self.data, bytes):
            return self.data
        elif isinstance(self.data, str):
            return self.data.encode(self.encoding)
        elif self.data is None and self.path:
            with open(str(self.path), "rb") as f:
                return f.read()
        else:
            msg = f"Unable to get bytes for blob {self}"
            raise ValueError(msg)

    @contextmanager
    def as_bytes_io(self) -> Generator[BytesIO | BinaryIO, None, None]:
        """Read data as a byte stream."""
        if isinstance(self.data, bytes):
            yield BytesIO(self.data)
        elif self.data is None and self.path:
            with open(str(self.path), "rb") as f:
                yield f
        else:
            msg = f"Unable to convert blob {self}"
            raise NotImplementedError(msg)

    @asynccontextmanager
    async def as_async_bytes_io(self):
        if isinstance(self.data, bytes):
            reader = asyncio.StreamReader()
            reader.feed_data(self.data)
            reader.feed_eof()
            yield reader
        elif self.data is None and self.path:
            async with aiofiles.open(str(self.path), 'rb') as f:
                yield f
        else:
            msg = f"Unable to convert blob {self}"
            raise NotImplementedError(msg)

    async def write_to_file(self, file, chunks: int = 8192):
        async with self.as_async_bytes_io() as reader:
            if isinstance(reader, asyncio.StreamReader):
                while chunk := await reader.read(chunks):
                    await file.write(chunk)
            else:
                await file.write(await reader.read())

    @classmethod
    def from_path(
            cls,
            path: str | PurePath,
            *,
            encoding: str = "utf-8",
            mimetype: str | None = None,
            extension: str | None = None,
            meta: Dict[str, Any] | None = None,
    ):
        return cls(
            data=None,
            mimetype=mimetype,
            extension=extension,
            encoding=encoding,
            path=path,
            meta=meta if meta is not None else {}
        )

    @classmethod
    def from_data(
            cls,
            data: str | bytes,
            *,
            encoding: str = "utf-8",
            mimetype: str | None = None,
            extension: str | None = None,
            path: str | None = None,
            meta: dict | None = None,
    ):
        return cls(
            data=data,
            mimetype=mimetype,
            extension=extension,
            encoding=encoding,
            path=path,
            meta=meta if meta is not None else {}
        )

    def __repr__(self) -> str:
        str_repr = f"Blob {id(self)}"
        return str_repr
