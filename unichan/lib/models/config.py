from sqlalchemy import Column, Integer, String

from unichan.database import ModelBase


class Config(ModelBase):
    __tablename__ = 'config'

    id = Column(Integer(), primary_key=True)
    type = Column(String())
    config = Column(String(), nullable=False, default='{}')