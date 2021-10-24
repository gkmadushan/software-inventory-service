from datetime import time
from pydantic import BaseModel, Field
from typing import List, Optional

class CreateInventory(BaseModel):
    id: Optional[str]
    name: str
    code: str
    vendor: Optional[str]
    contact: Optional[str]
    description: Optional[str]

class CreateVarient(BaseModel):
    id: Optional[str]
    inventory_item: str
    version: str
    notes: str
    configured_resource_id: str