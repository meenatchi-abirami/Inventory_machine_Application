from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from src.database_config import get_db

router = APIRouter(prefix="/parameter-handler")

# 📌 Helper function to convert datetime to ISO format
def convert_datetime(value):
    """Convert datetime objects to ISO format strings"""
    if isinstance(value, datetime):
        return value.isoformat()
    return value  # Return other data types as-is

# ✅ **Create Parameter**
@router.post("/create-parameter")
async def create_parameter_config(
    param_category: str, param_name: str, param_value: str, status: str, 
    create_by: int, last_updated_by: int, machine_id: int, 
    db: AsyncSession = Depends(get_db)
):
    try:
        # Insert into database
        query = text("""
            INSERT INTO parameter_config (param_category, param_name, param_value, status, create_by, last_updated_by, machine_id, create_date, last_updated_date)
            VALUES (:param_category, :param_name, :param_value, :status, :create_by, :last_updated_by, :machine_id, NOW(), NOW())
        """)
        await db.execute(query, {
            "param_category": param_category,
            "param_name": param_name,
            "param_value": param_value,
            "status": status,
            "create_by": create_by,
            "last_updated_by": last_updated_by,
            "machine_id": machine_id
        })
        await db.commit()
        return JSONResponse(content={"message": "Parameter created successfully"}, status_code=201)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ **Get All Parameters**
@router.get("/get-parameters")
async def get_all_parameter_configs(db: AsyncSession = Depends(get_db)):
    try:
        query = text("SELECT * FROM parameter_config")
        result = await db.execute(query)
        parameters = result.mappings().all()

        # Convert RowMapping to list of dictionaries
        parameter_list = [{key: convert_datetime(value) for key, value in dict(row).items()} for row in parameters]

        return JSONResponse(content={"data": parameter_list}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ **Get Parameter by ID**
@router.get("/get-parameter/{param_id}")
async def get_parameter_config(param_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("SELECT * FROM parameter_config WHERE id = :param_id")
        result = await db.execute(query, {"param_id": param_id})
        parameter = result.mappings().first()

        if not parameter:
            raise HTTPException(status_code=404, detail=f"Parameter with ID {param_id} not found")

        parameter_dict = {key: convert_datetime(value) for key, value in dict(parameter).items()}

        return JSONResponse(content={"data": parameter_dict}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ **Update Parameter**
@router.put("/update-parameter/{param_id}")
async def update_parameter_config(
    param_id: int, param_category: str, param_name: str, param_value: str, 
    status: str, last_updated_by: int, machine_id: int, 
    db: AsyncSession = Depends(get_db)
):
    try:
        query = text("""
            UPDATE parameter_config 
            SET param_category = :param_category, param_name = :param_name, param_value = :param_value, 
                status = :status, last_updated_by = :last_updated_by, machine_id = :machine_id, last_updated_date = NOW()
            WHERE id = :param_id
        """)
        await db.execute(query, {
            "param_category": param_category,
            "param_name": param_name,
            "param_value": param_value,
            "status": status,
            "last_updated_by": last_updated_by,
            "machine_id": machine_id,
            "param_id": param_id
        })
        await db.commit()
        return JSONResponse(content={"message": "Parameter updated successfully"}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# ✅ **Delete Parameter**
@router.delete("/delete-parameter/{param_id}")
async def delete_parameter_config(param_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("DELETE FROM parameter_config WHERE id = :param_id")
        await db.execute(query, {"param_id": param_id})
        await db.commit()
        return JSONResponse(content={"message": "Parameter deleted successfully"}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")
