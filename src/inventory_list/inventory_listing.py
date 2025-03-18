# import logging
# from fastapi import APIRouter, Depends, HTTPException, Form, File
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.sql import text
# from starlette.responses import JSONResponse
# from src.database_config import get_db
# from datetime import datetime
# from typing import Optional
# from pydantic import BaseModel

# router = APIRouter(prefix="/inventory-listings")

# # ✅ Request model for creating & updating inventory listings
# class InventoryListingSchema(BaseModel):
#     inventory_id: int
#     reasons: Optional[str] = None
#     status: str
#     create_by: int
#     last_updated_by: int
#     is_damaged: bool
#     emp_id: int

# # ✅ Get all inventory listings
# @router.get("/listings")
# async def get_all_inventory_listings(db: AsyncSession = Depends(get_db)):
#     try:
#         query = text("""
#             SELECT id, inventory_id, reasons, status, create_by, last_updated_by, 
#                    create_date, last_updated_date, is_damaged, emp_id 
#             FROM inventory_listings
#         """)
#         result = await db.execute(query)
#         listings = result.mappings().all()

#         def convert_datetime(value):
#             return value.isoformat() if isinstance(value, datetime) else value

#         # Convert datetime fields to string
#         formatted_listings = [{key: convert_datetime(value) for key, value in dict(item).items()} for item in listings]

#         return JSONResponse(content={"data": formatted_listings}, status_code=200)

#     except Exception as e:
#         print("Error:", str(e))
#         raise HTTPException(status_code=500, detail="Database error")

# # ✅ Get inventory listing by ID
# @router.get("/get-listing/{listing_id}")
# async def get_inventory_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
#     try:
#         query = text("""
#             SELECT id, inventory_id, reasons, status, create_by, last_updated_by, 
#                    create_date, last_updated_date, is_damaged, emp_id
#             FROM inventory_listings WHERE id = :listing_id
#         """)
#         result = await db.execute(query, {"listing_id": listing_id})
#         listing = result.mappings().first()

#         if not listing:
#             raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

#         return JSONResponse(content={"data": dict(listing)}, status_code=200)

#     except Exception as e:
#         print("Error:", str(e))
#         raise HTTPException(status_code=500, detail="Database error")

# @router.post("/create-listing")
# async def create_inventory_listing(
#     inventory_id: int = Form(...),
#     reasons: Optional[str] = Form(None),
#     status: str = Form(...),
#     create_by: int = Form(...),
#     last_updated_by: int = Form(...),
#     is_damaged: bool = Form(...),
#     emp_id: int = Form(...),
#     file: Optional[bytes] = File(None),  # Optional file upload
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         # Log incoming data
#         logging.debug("Received form data: %s", {
#             "inventory_id": inventory_id,
#             "reasons": reasons,
#             "status": status,
#             "create_by": create_by,
#             "last_updated_by": last_updated_by,
#             "is_damaged": is_damaged,
#             "emp_id": emp_id
#         })

#         # If there's a file, you can process it as needed
#         if file:
#             # Log file size (in bytes)
#             logging.debug(f"Received file with size {len(file)} bytes")
#             # You could save the file or process it as needed
#             pass

#         query = text("""
#             INSERT INTO inventory_listings (inventory_id, reasons, status, create_by, last_updated_by, 
#                                             create_date, last_updated_date, is_damaged, emp_id)
#             VALUES (:inventory_id, :reasons, :status, :create_by, :last_updated_by, 
#                     NOW(), NOW(), :is_damaged, :emp_id)
#         """)
#         await db.execute(query, {
#             "inventory_id": inventory_id,
#             "reasons": reasons,
#             "status": status,
#             "create_by": create_by,
#             "last_updated_by": last_updated_by,
#             "is_damaged": is_damaged,
#             "emp_id": emp_id,
#         })
#         await db.commit()

#         return JSONResponse(content={"message": "Inventory listing created successfully"}, status_code=201)

#     except Exception as e:
#         logging.error("Error occurred while creating inventory listing: %s", str(e))
#         raise HTTPException(status_code=500, detail="Database error")

# # ✅ Update an inventory listing (Multipart)
# @router.put("/update-listing/{listing_id}")
# async def update_inventory_listing(
#     listing_id: int,
#     inventory_id: int = Form(...),
#     reasons: Optional[str] = Form(None),
#     status: str = Form(...),
#     last_updated_by: int = Form(...),
#     is_damaged: bool = Form(...),
#     emp_id: int = Form(...),
#     file: Optional[bytes] = File(None),  # Optional file upload
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         # If there's a file, process or save it
#         if file:
#             # You can save the file or process it as needed
#             pass

#         query = text("""
#             UPDATE inventory_listings
#             SET inventory_id = :inventory_id, reasons = :reasons, status = :status, 
#                 last_updated_by = :last_updated_by, last_updated_date = NOW(), 
#                 is_damaged = :is_damaged, emp_id = :emp_id
#             WHERE id = :listing_id
#         """)
#         result = await db.execute(query, {
#             "listing_id": listing_id,
#             "inventory_id": inventory_id,
#             "reasons": reasons,
#             "status": status,
#             "last_updated_by": last_updated_by,
#             "is_damaged": is_damaged,
#             "emp_id": emp_id,
#         })
#         await db.commit()

#         if result.rowcount == 0:
#             raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

#         return JSONResponse(content={"message": "Inventory listing updated successfully"}, status_code=200)

#     except Exception as e:
#         print("Error:", str(e))
#         raise HTTPException(status_code=500, detail="Database error")
    
# # ✅ Delete an inventory listing
# @router.delete("/delete-listing/{listing_id}")
# async def delete_inventory_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
#     try:
#         query = text("DELETE FROM inventory_listings WHERE id = :listing_id")
#         result = await db.execute(query, {"listing_id": listing_id})
#         await db.commit()

#         if result.rowcount == 0:
#             raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

#         return JSONResponse(content={"message": "Inventory listing deleted successfully"}, status_code=200)

#     except Exception as e:
#         print("Error:", str(e))
#         raise HTTPException(status_code=500, detail="Database error")

import logging
from fastapi import APIRouter, Depends, HTTPException, Form, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from starlette.responses import JSONResponse
from src.database_config import get_db
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/inventory-listings")

# ✅ Request model for creating & updating inventory listings
class InventoryListingSchema(BaseModel):
    inventory_id: int
    reasons: Optional[str] = None
    status: str
    create_by: int
    last_updated_by: int
    is_damaged: bool
    emp_id: int

# ✅ Get all inventory listings
# @router.get("/listings")
# async def get_all_inventory_listings(db: AsyncSession = Depends(get_db)):
#     try:
#         query = text("""
#             SELECT id, inventory_id, reasons, status, create_by, last_updated_by, 
#                    create_date, last_updated_date, is_damaged, emp_id 
#             FROM inventory_listings
#         """)
#         result = await db.execute(query)
#         listings = result.mappings().all()

#         def convert_datetime(value):
#             return value.isoformat() if isinstance(value, datetime) else value

#         # Convert datetime fields to string
#         formatted_listings = [{key: convert_datetime(value) for key, value in dict(item).items()} for item in listings]

#         return JSONResponse(content={"data": formatted_listings}, status_code=200)

#     except Exception as e:
#         logging.error("Error occurred while fetching all inventory listings: %s", str(e))
#         raise HTTPException(status_code=500, detail="Database error")


@router.get("/listings")
async def get_all_inventory_listings(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT 
                il.id, 
                ic.item_code,  -- Fetching item_code instead of inventory_id
                il.reasons, 
                il.status, 
                il.create_by, 
                il.last_updated_by, 
                il.create_date, 
                il.last_updated_date, 
                il.is_damaged, 
                uc.emp_code,  -- Fetching emp_code instead of emp_id
                uc.first_name AS user_name  -- Using 'first_name' instead of 'name'
            FROM inventory_listings il
            JOIN user_config uc ON il.emp_id = uc.id
            JOIN inventory_config ic ON il.inventory_id = ic.id
        """)
        result = await db.execute(query)
        listings = result.mappings().all()

        def convert_datetime(value):
            return value.isoformat() if isinstance(value, datetime) else value

        formatted_listings = [{key: convert_datetime(value) for key, value in dict(item).items()} for item in listings]

        return JSONResponse(content={"data": formatted_listings}, status_code=200)

    except Exception as e:
        logging.error("Error occurred while fetching all inventory listings: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Get inventory listing by ID
@router.get("/get-listing/{listing_id}")
async def get_inventory_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT id, inventory_id, reasons, status, create_by, last_updated_by, 
                   create_date, last_updated_date, is_damaged, emp_id
            FROM inventory_listings WHERE id = :listing_id
        """)
        result = await db.execute(query, {"listing_id": listing_id})
        listing = result.mappings().first()

        if not listing:
            raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

        return JSONResponse(content={"data": dict(listing)}, status_code=200)

    except Exception as e:
        logging.error("Error occurred while fetching listing by ID: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Create a new inventory listing
@router.post("/create-listing")
async def create_inventory_listing(
    inventory_id: int = Form(...),
    reasons: Optional[str] = Form(None),
    status: str = Form(...),
    create_by: int = Form(...),
    last_updated_by: int = Form(...),
    is_damaged: bool = Form(...),
    emp_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Log incoming data
        logging.debug("Received form data: %s", {
            "inventory_id": inventory_id,
            "reasons": reasons,
            "status": status,
            "create_by": create_by,
            "last_updated_by": last_updated_by,
            "is_damaged": is_damaged,
            "emp_id": emp_id
        })

        query = text("""
            INSERT INTO inventory_listings (inventory_id, reasons, status, create_by, last_updated_by, 
                                            create_date, last_updated_date, is_damaged, emp_id)
            VALUES (:inventory_id, :reasons, :status, :create_by, :last_updated_by, 
                    NOW(), NOW(), :is_damaged, :emp_id)
        """)
        await db.execute(query, {
            "inventory_id": inventory_id,
            "reasons": reasons,
            "status": status,
            "create_by": create_by,
            "last_updated_by": last_updated_by,
            "is_damaged": is_damaged,
            "emp_id": emp_id,
        })
        await db.commit()

        return JSONResponse(content={"message": "Inventory listing created successfully"}, status_code=201)

    except Exception as e:
        logging.error("Error occurred while creating inventory listing: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Update an inventory listing (Multipart)
@router.put("/update-listing/{listing_id}")
async def update_inventory_listing(
    listing_id: int,
    inventory_id: int = Form(...),
    reasons: Optional[str] = Form(None),
    status: str = Form(...),
    last_updated_by: int = Form(...),
    is_damaged: bool = Form(...),
    emp_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = text("""
            UPDATE inventory_listings
            SET inventory_id = :inventory_id, reasons = :reasons, status = :status, 
                last_updated_by = :last_updated_by, last_updated_date = NOW(), 
                is_damaged = :is_damaged, emp_id = :emp_id
            WHERE id = :listing_id
        """)
        result = await db.execute(query, {
            "listing_id": listing_id,
            "inventory_id": inventory_id,
            "reasons": reasons,
            "status": status,
            "last_updated_by": last_updated_by,
            "is_damaged": is_damaged,
            "emp_id": emp_id,
        })
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

        return JSONResponse(content={"message": "Inventory listing updated successfully"}, status_code=200)

    except Exception as e:
        logging.error("Error occurred while updating inventory listing: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ Delete an inventory listing
@router.delete("/delete-listing/{listing_id}")
async def delete_inventory_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("DELETE FROM inventory_listings WHERE id = :listing_id")
        result = await db.execute(query, {"listing_id": listing_id})
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

        return JSONResponse(content={"message": "Inventory listing deleted successfully"}, status_code=200)

    except Exception as e:
        logging.error("Error occurred while deleting inventory listing: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# @router.delete("/delete-listing/{listing_id}")
# async def delete_inventory_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
#     try:
#         # Step 1: Delete records from related tables first
#         await db.execute(
#             text("DELETE FROM inventory_damaged_listings WHERE inventory_listing_id = :listing_id"),
#             {"listing_id": listing_id}
#         )
#         await db.execute(
#             text("DELETE FROM inventory_unreturned_listings WHERE inventory_listing_id = :listing_id"),
#             {"listing_id": listing_id}
#         )

#         # Step 2: Delete from inventory_listings
#         result = await db.execute(
#             text("DELETE FROM inventory_listings WHERE id = :listing_id"),
#             {"listing_id": listing_id}
#         )
#         await db.commit()

#         if result.rowcount == 0:
#             raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")

#         return JSONResponse(content={"message": "Inventory listing and related records deleted successfully"}, status_code=200)

#     except Exception as e:
#         logging.error("Error occurred while deleting inventory listing: %s", str(e))
#         raise HTTPException(status_code=500, detail="Database error")
