from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.exc import IntegrityError
from starlette.responses import Response
from fastapi import APIRouter, Depends, HTTPException, Request
from dependencies import common_params, get_db, get_secret_random
from schemas import CreateInventory, CreateVarient
from sqlalchemy.orm import Session
from typing import Optional
from models import InventoryItem, InventoryItemVarient
from dependencies import get_token_header
import uuid
from datetime import datetime
from exceptions import username_already_exists
from sqlalchemy import over
from sqlalchemy import engine_from_config, and_, func, literal_column, case
from sqlalchemy_filters import apply_pagination
import time
import os
import uuid
from sqlalchemy.dialects import postgresql

page_size = os.getenv('PAGE_SIZE')


router = APIRouter(
    prefix="/v1/inventory",
    tags=["SoftwareInventoryAPIs"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("")
def create(details: CreateInventory, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    # generate token
    id = details.id or uuid.uuid4().hex

    item = InventoryItem(
        id=id,
        name=details.name,
        code=details.code,
        vendor=details.vendor,
        contact=details.contact,
        description=details.description
    )

    # commiting data to db
    try:
        db.add(item)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=422, detail="Unable to create new inventory item")
    return {
        "success": True,
    }


@router.post("/varients")
def create(details: CreateVarient, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    # generate token
    id = details.id or uuid.uuid4().hex
    item = db.query(InventoryItem).get(details.inventory_item.strip())

    varient = InventoryItemVarient(
        id=id,
        inventory_item=item,
        version=details.version,
        notes=details.notes,
        configured_resource_id=details.configured_resource_id
    )

    # commiting data to db
    try:
        db.add(varient)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=422, detail="Unable to create new inventory item")
    return {
        "success": True
    }


@router.get("/varients")
def get_by_filter(page: Optional[str] = 1, limit: Optional[int] = page_size, commons: dict = Depends(common_params), db: Session = Depends(get_db), id: Optional[str] = None, name: Optional[str] = None, vendor: Optional[str] = None, code: Optional[str] = None, item_id: Optional[str] = None):
    filters = []

    if(item_id):
        filters.append(InventoryItemVarient.inventory_item_id == item_id)

    if(name):
        filters.append(InventoryItem.name.ilike(name+'%'))
    else:
        filters.append(InventoryItem.name.ilike('%'))

    if(vendor):
        filters.append(InventoryItem.vendor.ilike(vendor+'%'))

    if(code):
        filters.append(InventoryItem.code.ilike(code+'%'))

    query = db.query(
        over(func.row_number(), order_by=InventoryItem.name).label('index'),
        InventoryItemVarient.id,
        InventoryItemVarient.version,
        InventoryItemVarient.notes,
        InventoryItemVarient.configured_resource_id
    )

    query, pagination = apply_pagination(query.join(InventoryItemVarient.inventory_item).where(
        and_(*filters)).order_by(InventoryItem.name.asc()), page_number=int(page), page_size=int(limit))

    response = {
        "data": query.all(),
        "meta": {
            "total_records": pagination.total_results,
            "limit": pagination.page_size,
            "num_pages": pagination.num_pages,
            "current_page": pagination.page_number
        }
    }

    return response


@router.get("")
def get_by_filter(page: Optional[str] = 1, limit: Optional[int] = page_size, commons: dict = Depends(common_params), db: Session = Depends(get_db), id: Optional[str] = None, name: Optional[str] = None, vendor: Optional[str] = None, code: Optional[str] = None):
    filters = []

    if(name):
        filters.append(InventoryItem.name.ilike(name+'%'))
    else:
        filters.append(InventoryItem.name.ilike('%'))

    if(vendor):
        filters.append(InventoryItem.vendor.ilike(vendor+'%'))

    if(code):
        filters.append(InventoryItem.code.ilike(code+'%'))

    query = db.query(
        over(func.row_number(), order_by=InventoryItem.name).label('index'),
        InventoryItem.id,
        InventoryItem.name,
        InventoryItem.code,
        InventoryItem.description,
        InventoryItem.vendor,
        InventoryItem.contact
    )

    query, pagination = apply_pagination(query.where(
        and_(*filters)).order_by(InventoryItem.name.asc()), page_number=int(page), page_size=int(limit))

    response = {
        "data": query.all(),
        "meta": {
            "total_records": pagination.total_results,
            "limit": pagination.page_size,
            "num_pages": pagination.num_pages,
            "current_page": pagination.page_number
        }
    }

    return response


@router.delete("/varients/{id}")
def delete_by_id(id: str, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    varient = db.query(InventoryItemVarient).get(id.strip())
    db.delete(varient)
    db.commit()
    return Response(status_code=204)


@router.delete("/{id}")
def delete_by_id(id: str, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    item = db.query(InventoryItem).get(id.strip())
    db.delete(item)
    db.commit()
    return Response(status_code=204)


@router.get("/varients/{id}")
def get_by_id(id: str, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    varient = db.query(InventoryItemVarient).get(id.strip())
    if varient == None:
        raise HTTPException(status_code=404, detail="Item not found")
    response = {
        "data": varient
    }
    return response


@router.get("/{id}")
def get_by_id(id: str, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    item = db.query(InventoryItem).get(id.strip())
    if item == None:
        raise HTTPException(status_code=404, detail="Item not found")
    response = {
        "data": item
    }
    return response


@router.put("/{id}")
def update(id: str, details: CreateInventory, commons: dict = Depends(common_params), db: Session = Depends(get_db)):
    # Set user entity
    item = db.query(InventoryItem).get(id)

    item.name = details.name
    item.description = details.description
    item.code = details.code
    item.vendor = details.vendor
    item.contact = details.contact

    # commiting data to db
    try:
        db.add(item)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=422, detail=username_already_exists)
    return {
        "success": True
    }
