#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/20
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : repository
# @Software: PyCharm
from datetime import datetime

from sqlalchemy import UUID, String, DateTime, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from domain.model.base import Base


class Repository(Base):
    __tablename__ = 'repository_info'
    id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
    )
    embedding_model: Mapped[str] = mapped_column(String, nullable=True)
    embedding_model_provider: Mapped[str] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_by: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
