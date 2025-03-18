from fastapi import Depends, Query, HTTPException
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

# Get all roles
async def role_list(db_engine: AsyncGenerator = Depends(get_db)):
    role_list_query = await db_engine.execute(text("SELECT * FROM role_config"))
    role_list_data = role_list_query.mappings().all()

    if len(role_list_data) == 0:
        raise HTTPException(status_code=404, detail=[{"msg": StatusMessage.s_404}])

    formatted_data = [{key: convert_datetime(value) for key, value in dict(row).items()} for row in role_list_data]
    return JSONResponse(content={"data": formatted_data}, status_code=200)

# Get a specific role by ID
async def get_role(role_id: int = Query(default=None), db_engine: AsyncGenerator = Depends(get_db)):
    query = "SELECT * FROM role_config WHERE id = :role_id"
    role_query = await db_engine.execute(text(query), {"role_id": role_id})
    role_data = role_query.mappings().first()

    if not role_data:
        raise HTTPException(status_code=404, detail=[{"msg": StatusMessage.s_404}])

    formatted_data = {key: convert_datetime(value) for key, value in dict(role_data).items()}
    return JSONResponse(content={"data": formatted_data}, status_code=200)

# Create a new role
async def create_role(
    role_name: str, role_access: str, status: str, create_by: str, updated_by: str,
    db_engine: AsyncGenerator = Depends(get_db)
):
    query = text("""
        INSERT INTO role_config (role_name, role_access, status, create_by, updated_by, create_date, last_updated_date)
        VALUES (:role_name, :role_access, :status, :create_by, :updated_by, NOW(), NOW())
    """)
    await db_engine.execute(query, {
        "role_name": role_name,
        "role_access": role_access,
        "status": status,
        "create_by": create_by,
        "updated_by": updated_by
    })
    await db_engine.commit()
    return JSONResponse(content={"message": "Role created successfully"}, status_code=201)

# Update a role
async def update_role(
    role_id: int, role_name: str, role_access: str, status: str, updated_by: str,
    db_engine: AsyncGenerator = Depends(get_db)
):
    query = text("""
        UPDATE role_config 
        SET role_name = :role_name, role_access = :role_access, status = :status, updated_by = :updated_by, last_updated_date = NOW()
        WHERE id = :role_id
    """)
    await db_engine.execute(query, {
        "role_name": role_name,
        "role_access": role_access,
        "status": status,
        "updated_by": updated_by,
        "role_id": role_id
    })
    await db_engine.commit()
    return JSONResponse(content={"message": "Role updated successfully"}, status_code=200)

# Delete a role
async def delete_role(role_id: int, db_engine: AsyncGenerator = Depends(get_db)):
    query = text("DELETE FROM role_config WHERE id = :role_id")
    await db_engine.execute(query, {"role_id": role_id})
    await db_engine.commit()
    return JSONResponse(content={"message": "Role deleted successfully"}, status_code=200)
