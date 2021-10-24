from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class InventoryItem(Base):
    __tablename__ = 'inventory_item'

    id = Column(UUID, primary_key=True)
    name = Column(String(250))
    code = Column(String(250), nullable=False, unique=True)
    vendor = Column(String(250))
    contact = Column(String(250))
    description = Column(String(500))


class InventoryItemVarient(Base):
    __tablename__ = 'inventory_item_varient'

    id = Column(UUID, primary_key=True)
    inventory_item_id = Column(ForeignKey('inventory_item.id'), nullable=False)
    version = Column(String(250), nullable=False)
    notes = Column(String(500))
    configured_resource_id = Column(UUID)

    inventory_item = relationship('InventoryItem')