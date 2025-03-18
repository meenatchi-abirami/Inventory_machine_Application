from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import AsyncGenerator
from datetime import datetime

# Application modules
from src.database_config import get_db
from src.seedwork.models.status_msg_model import StatusMessage

def convert_datetime(value):
    """Convert datetime objects to ISO format strings"""
    if isinstance(value, datetime):
        return value.isoformat()  # Converts to "YYYY-MM-DDTHH:MM:SS"
    return value  # Return other data types as-is

# Get all machines
async def machine_list(db_engine: AsyncGenerator = Depends(get_db)):
    machine_list_query = await db_engine.execute(text("SELECT * FROM machine_listings"))
    machine_list_data = machine_list_query.mappings().all()

    if not machine_list_data:
        raise HTTPException(status_code=404, detail=[{"msg": StatusMessage.s_404}])

    formatted_data = [{key: convert_datetime(value) for key, value in dict(row).items()} for row in machine_list_data]
    return JSONResponse(content={"data": formatted_data}, status_code=200)

# Get a specific machine by ID
async def get_machine(machine_id: int, db_engine: AsyncGenerator = Depends(get_db)):
    query = "SELECT * FROM machine_listings WHERE id = :machine_id"
    machine_query = await db_engine.execute(text(query), {"machine_id": machine_id})
    machine_data = machine_query.mappings().first()

    if not machine_data:
        raise HTTPException(status_code=404, detail=[{"msg": StatusMessage.s_404}])

    formatted_data = {key: convert_datetime(value) for key, value in dict(machine_data).items()}
    return JSONResponse(content={"data": formatted_data}, status_code=200)

# Create a new machine
async def create_machine(
    location_id: int, name: str, status: str, created_by: int, last_updated_by: int,
    db_engine: AsyncGenerator = Depends(get_db)
):
    # Convert status to match ENUM
    valid_statuses = {"Active", "InActive", "Delete"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from {valid_statuses}")

    query = text("""
        INSERT INTO machine_listings (location_id, name, status, created_by, last_updated_by, created_date, last_updated_date)
        VALUES (:location_id, :name, :status, :created_by, :last_updated_by, NOW(), NOW())
    """)
    
    try:
        print(f"Executing Query: {query}")  # Debugging Log
        await db_engine.execute(query, {
            "location_id": location_id,
            "name": name,
            "status": status,
            "created_by": created_by,
            "last_updated_by": last_updated_by
        })
        await db_engine.commit()
        return JSONResponse(content={"message": "Machine created successfully"}, status_code=201)
    except Exception as e:
        print(f"Error: {e}")  # Debugging Log
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Update a machine
async def update_machine(
    machine_id: int, location_id: int, name: str, status: str, last_updated_by: int,
    db_engine: AsyncGenerator = Depends(get_db)
):
    query = text("""
        UPDATE machine_listings 
        SET location_id = :location_id, name = :name, status = :status, last_updated_by = :last_updated_by, last_updated_date = NOW()
        WHERE id = :machine_id
    """)
    await db_engine.execute(query, {
        "location_id": location_id,
        "name": name,
        "status": status,
        "last_updated_by": last_updated_by,
        "machine_id": machine_id
    })
    await db_engine.commit()
    return JSONResponse(content={"message": "Machine updated successfully"}, status_code=200)

# Delete a machine
async def delete_machine(machine_id: int, db_engine: AsyncGenerator = Depends(get_db)):
    query = text("DELETE FROM machine_listings WHERE id = :machine_id")
    await db_engine.execute(query, {"machine_id": machine_id})
    await db_engine.commit()
    return JSONResponse(content={"message": "Machine deleted successfully"}, status_code=200)
