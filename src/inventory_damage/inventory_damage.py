# from fastapi import Depends, Query, HTTPException
# from fastapi.responses import JSONResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import text
# from typing import AsyncGenerator
# from datetime import datetime

# # Application modules
# from src.database_config import get_db
# from src.seedwork.models.status_msg_model import StatusMessage

# def convert_datetime(value):
#     """Convert datetime objects to ISO format strings"""
#     if isinstance(value, datetime):
#         return value.isoformat()  # Converts to "YYYY-MM-DDTHH:MM:SS"
#     return value  # Return other data types as-is

# # Get all damaged listings
# async def damaged_listing_list(db_engine: AsyncGenerator = Depends(get_db)):
#     query = text("""
#         SELECT id, listing_id, status, create_by, last_updated_by, create_date, last_updated_date 
#         FROM inventory_damaged_listings
#     """)
#     result = await db_engine.execute(query)
#     listings = result.mappings().all()

#     if len(listings) == 0:
#         raise HTTPException(status_code=404, detail=[{"msg": StatusMessage.s_404}])

#     formatted_listings = [{key: convert_datetime(value) for key, value in dict(item).items()} for item in listings]
#     return JSONResponse(content={"data": formatted_listings}, status_code=200)

# # Get a specific damaged listing by ID
# async def get_damaged_listing(listing_id: int = Query(default=None), db_engine: AsyncGenerator = Depends(get_db)):
#     query = text("""
#         SELECT id, listing_id, status, create_by, last_updated_by, create_date, last_updated_date 
#         FROM inventory_damaged_listings WHERE id = :listing_id
#     """)
#     result = await db_engine.execute(query, {"listing_id": listing_id})
#     listing = result.mappings().first()

#     if not listing:
#         raise HTTPException(status_code=404, detail=[{"msg": StatusMessage.s_404}])

#     formatted_listing = {key: convert_datetime(value) for key, value in dict(listing).items()}
#     return JSONResponse(content={"data": formatted_listing}, status_code=200)

# # Create a new damaged listing
# async def create_damaged_listing(
#     listing_id: int, status: str, create_by: int, last_updated_by: int,
#     db_engine: AsyncGenerator = Depends(get_db)
# ):
#     query = text("""
#         INSERT INTO inventory_damaged_listings (listing_id, status, create_by, last_updated_by, create_date, last_updated_date)
#         VALUES (:listing_id, :status, :create_by, :last_updated_by, NOW(), NOW())
#     """)
#     await db_engine.execute(query, {
#         "listing_id": listing_id,
#         "status": status,
#         "create_by": create_by,
#         "last_updated_by": last_updated_by
#     })
#     await db_engine.commit()

#     return JSONResponse(content={"message": "Damaged listing created successfully"}, status_code=201)

# # Update a damaged listing
# async def update_damaged_listing(
#     listing_id: int, status: str, last_updated_by: int, db_engine: AsyncGenerator = Depends(get_db)
# ):
#     query = text("""
#         UPDATE inventory_damaged_listings 
#         SET status = :status, last_updated_by = :last_updated_by, last_updated_date = NOW()
#         WHERE id = :listing_id
#     """)
#     result = await db_engine.execute(query, {
#         "listing_id": listing_id,
#         "status": status,
#         "last_updated_by": last_updated_by
#     })
#     await db_engine.commit()

#     if result.rowcount == 0:
#         raise HTTPException(status_code=404, detail=[{"msg": StatusMessage.s_404}])

#     return JSONResponse(content={"message": "Damaged listing updated successfully"}, status_code=200)

# # Delete a damaged listing
# async def delete_damaged_listing(listing_id: int, db_engine: AsyncGenerator = Depends(get_db)):
#     query = text("""
#         DELETE FROM inventory_damaged_listings WHERE id = :listing_id
#     """)
#     result = await db_engine.execute(query, {"listing_id": listing_id})
#     await db_engine.commit()

#     if result.rowcount == 0:
#         raise HTTPException(status_code=404, detail=[{"msg": StatusMessage.s_404}])

#     return JSONResponse(content={"message": "Damaged listing deleted successfully"}, status_code=200)


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from src.database_config import get_db
from pydantic import BaseModel
from typing import List

router = APIRouter()

### ✅ Pydantic Model for Request Body ###
class DamagedListingRequest(BaseModel):
    listing_id: int
    create_by: int

class UpdateDamagedStatusRequest(BaseModel):
    status: str

### ✅ 1️⃣ Create a New Damaged Listing (INSERT) ###
@router.post("/damaged-listings/")
async def create_damaged_listing(request: DamagedListingRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Check if the listing exists
        listing_check_query = text("SELECT id FROM inventory_listings WHERE id = :listing_id")
        result = await db.execute(listing_check_query, {"listing_id": request.listing_id})
        listing = result.fetchone()

        if not listing:
            raise HTTPException(status_code=404, detail="Inventory listing not found")

        # Insert into inventory_damaged_listings
        insert_query = text("""
            INSERT INTO inventory_damaged_listings (listing_id, create_by, last_updated_by)
            VALUES (:listing_id, :create_by, :create_by)
        """)
        await db.execute(insert_query, {"listing_id": request.listing_id, "create_by": request.create_by})

        await db.commit()
        return {"message": "Damaged listing recorded successfully!"}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

### ✅ 2️⃣ Get All Damaged Listings (SELECT) ###
@router.get("/damaged-listings/", response_model=List[dict])
async def get_all_damaged_listings(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT id, listing_id, status, create_by, last_updated_by, create_date, last_updated_date
            FROM inventory_damaged_listings
        """)
        result = await db.execute(query)
        rows = result.fetchall()

        return [dict(row._mapping) for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

### ✅ 3️⃣ Get a Damaged Listing by ID (SELECT) ###
@router.get("/damaged-listings/{damaged_id}", response_model=dict)
async def get_damaged_listing(damaged_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT id, listing_id, status, create_by, last_updated_by, create_date, last_updated_date
            FROM inventory_damaged_listings WHERE id = :damaged_id
        """)
        result = await db.execute(query, {"damaged_id": damaged_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Damaged listing not found")

        return dict(row._mapping)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

### ✅ 4️⃣ Update Damaged Listing Status (UPDATE) ###
@router.put("/damaged-listings/{damaged_id}")
async def update_damaged_listing_status(damaged_id: int, request: UpdateDamagedStatusRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Check if the damaged listing exists
        check_query = text("SELECT id FROM inventory_damaged_listings WHERE id = :damaged_id")
        result = await db.execute(check_query, {"damaged_id": damaged_id})
        damaged_entry = result.fetchone()

        if not damaged_entry:
            raise HTTPException(status_code=404, detail="Damaged listing not found")

        # Update status
        update_query = text("""
            UPDATE inventory_damaged_listings
            SET status = :status, last_updated_date = CURRENT_TIMESTAMP()
            WHERE id = :damaged_id
        """)
        await db.execute(update_query, {"status": request.status, "damaged_id": damaged_id})
        await db.commit()

        return {"message": "Damaged listing status updated successfully!"}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

### ✅ 5️⃣ Delete a Damaged Listing (DELETE) ###
@router.delete("/damaged-listings/{damaged_id}")
async def delete_damaged_listing(damaged_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Check if the damaged listing exists
        check_query = text("SELECT id FROM inventory_damaged_listings WHERE id = :damaged_id")
        result = await db.execute(check_query, {"damaged_id": damaged_id})
        damaged_entry = result.fetchone()

        if not damaged_entry:
            raise HTTPException(status_code=404, detail="Damaged listing not found")

        # Delete the damaged listing
        delete_query = text("DELETE FROM inventory_damaged_listings WHERE id = :damaged_id")
        await db.execute(delete_query, {"damaged_id": damaged_id})
        await db.commit()

        return {"message": "Damaged listing deleted successfully!"}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
