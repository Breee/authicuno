from sqlalchemy import Column, Integer, String, TypeDecorator, TIMESTAMP, Boolean, UnicodeText, BigInteger
from sqlalchemy.ext.declarative import declarative_base
import json

class Json(TypeDecorator):
    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

Base = declarative_base()

class ServerSetting(Base):
    __tablename__ = 'server_setting'
    # Overall useful information
    id = Column(Integer, primary_key=True)
    server_id = Column(BigInteger, name="server_id")
    prefix = Column(UnicodeText, name="prefix")
    moderator_roles = Column(Json, name="moderator_roles")
