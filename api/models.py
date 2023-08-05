from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)


class Data(Base):
    __tablename__ = "datas"

    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    data_id = Column(Integer, primary_key=True, nullable=False)
