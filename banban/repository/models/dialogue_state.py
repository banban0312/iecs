from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column

# orm映射 Object Relation-ship Mapping 对象关系映射
class Base(DeclarativeBase):
    pass

class DialogueStateRecord( Base ):

    __tablename__ = 'dialogue_states'

    sender_id : Mapped[str] = mapped_column(String(255), primary_key=True)
    state_json : Mapped[str] = mapped_column(Text, nullable=False, default="{}")