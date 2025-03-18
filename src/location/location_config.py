from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from src.database_config import get_db

router = APIRouter(prefix="/location-handler")

def convert_datetime(value):
    """Convert datetime objects to ISO format strings"""
    if isinstance(value, datetime):
        return value.isoformat()  # Converts to "YYYY-MM-DDTHH:MM:SS"
    return value  # Return other data types as-is

# Create Location
@router.post("/create-location")
async def create_location(name: str, status: str, created_by: int, last_updated_by: int, db: AsyncSession = Depends(get_db)):
    try:
        # Check if created_by exists
        user_query = text("SELECT id FROM user_config WHERE id = :user_id")
        user_result = await db.execute(user_query, {"user_id": created_by})
        user = user_result.fetchone()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid created_by. User does not exist.")

        # Check if last_updated_by exists
        user_result = await db.execute(user_query, {"user_id": last_updated_by})
        user = user_result.fetchone()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid last_updated_by. User does not exist.")

        # Insert location data
        query = text("""
            INSERT INTO location_config (name, status, created_by, last_updated_by, created_date, last_updated_date)
            VALUES (:name, :status, :created_by, :last_updated_by, NOW(), NOW())
        """)
        await db.execute(query, {
            "name": name,
            "status": status,
            "created_by": created_by,
            "last_updated_by": last_updated_by
        })
        await db.commit()
        return JSONResponse(content={"message": "Location created successfully"}, status_code=201)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# Get All Locations
@router.get("/get-locations")
async def get_locations(db: AsyncSession = Depends(get_db)):
    try:
        query = text("SELECT * FROM location_config")
        result = await db.execute(query)
        locations = result.mappings().all()

        # Convert RowMapping to list of dictionaries
        location_list = [{key: convert_datetime(value) for key, value in dict(row).items()} for row in locations]

        return JSONResponse(content={"data": location_list}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# Get Location by ID
@router.get("/get-location/{location_id}")
async def get_location(location_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("SELECT * FROM location_config WHERE id = :location_id")
        result = await db.execute(query, {"location_id": location_id})
        location = result.mappings().first()

        if not location:
            raise HTTPException(status_code=404, detail=f"Location with ID {location_id} not found")

        location_dict = {key: convert_datetime(value) for key, value in dict(location).items()}

        return JSONResponse(content={"data": location_dict}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# Update Location
@router.put("/update-location/{location_id}")
async def update_location(location_id: int, name: str, status: str, last_updated_by: int, db: AsyncSession = Depends(get_db)):
    try:
        # Check if last_updated_by exists
        user_query = text("SELECT id FROM user_config WHERE id = :user_id")
        user_result = await db.execute(user_query, {"user_id": last_updated_by})
        user = user_result.fetchone()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid last_updated_by. User does not exist.")

        query = text("""
            UPDATE location_config 
            SET name = :name, status = :status, last_updated_by = :last_updated_by, last_updated_date = NOW()
            WHERE id = :location_id
        """)
        await db.execute(query, {
            "name": name,
            "status": status,
            "last_updated_by": last_updated_by,
            "location_id": location_id
        })
        await db.commit()
        return JSONResponse(content={"message": "Location updated successfully"}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# Delete Location
@router.delete("/delete-location/{location_id}")
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("DELETE FROM location_config WHERE id = :location_id")
        await db.execute(query, {"location_id": location_id})
        await db.commit()
        return JSONResponse(content={"message": "Location deleted successfully"}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")
