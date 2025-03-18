import logging
from fastapi import APIRouter, Depends, HTTPException, Form, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from starlette.responses import JSONResponse
from src.database_config import get_db
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/inventory-unreturned-listings")

# ✅ Request model for creating & updating inventory unreturned listings
class InventoryUnreturnedListingSchema(BaseModel):
    listing_id: int
    status: Optional[str] = 'Active'
    create_by: int
    last_updated_by: int

# ✅ Get all inventory unreturned listings
@router.get("/listings")
async def get_all_inventory_unreturned_listings(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT id, listing_id, status, create_by, last_updated_by, create_date, last_updated_date
            FROM inventory_unreturned_listings
        """)
        result = await db.execute(query)
        listings = result.mappings().all()

        def convert_datetime(value):
            return value.isoformat() if isinstance(value, datetime) else value

        # Convert datetime fields to string
        formatted_listings = [{key: convert_datetime(value) for key, value in dict(item).items()} for item in listings]

        return JSONResponse(content={"data": formatted_listings}, status_code=200)

    except Exception as e:
        logging.error("Error: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Create inventory unreturned listing
@router.post("/create-listing")
async def create_inventory_unreturned_listing(
    listing_id: int = Form(...),
    status: Optional[str] = Form("Active"),
    create_by: int = Form(...),
    last_updated_by: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = text("""
            INSERT INTO inventory_unreturned_listings (listing_id, status, create_by, last_updated_by, create_date, last_updated_date)
            VALUES (:listing_id, :status, :create_by, :last_updated_by, NOW(), NOW())
        """)
        await db.execute(query, {
            "listing_id": listing_id,
            "status": status,
            "create_by": create_by,
            "last_updated_by": last_updated_by
        })
        await db.commit()

        return JSONResponse(content={"message": "Inventory unreturned listing created successfully"}, status_code=201)

    except Exception as e:
        logging.error("Error occurred while creating unreturned inventory listing: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Update an inventory unreturned listing
@router.put("/update-listing/{listing_id}")
async def update_inventory_unreturned_listing(
    listing_id: int,
    status: Optional[str] = Form("Active"),
    last_updated_by: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = text("""
            UPDATE inventory_unreturned_listings
            SET status = :status, last_updated_by = :last_updated_by, last_updated_date = NOW()
            WHERE listing_id = :listing_id
        """)
        result = await db.execute(query, {
            "listing_id": listing_id,
            "status": status,
            "last_updated_by": last_updated_by
        })
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

        return JSONResponse(content={"message": "Inventory unreturned listing updated successfully"}, status_code=200)

    except Exception as e:
        logging.error("Error occurred while updating unreturned inventory listing: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Delete an inventory unreturned listing
@router.delete("/delete-listing/{listing_id}")
async def delete_inventory_unreturned_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("DELETE FROM inventory_unreturned_listings WHERE listing_id = :listing_id")
        result = await db.execute(query, {"listing_id": listing_id})
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

        return JSONResponse(content={"message": "Inventory unreturned listing deleted successfully"}, status_code=200)

    except Exception as e:
        logging.error("Error: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")
