from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from src.database_config import get_db

router = APIRouter(prefix="/user-handler")

def convert_datetime(value):
    """Convert datetime objects to ISO format strings"""
    if isinstance(value, datetime):
        return value.isoformat()  # Converts to "YYYY-MM-DDTHH:MM:SS"
    return value  # Return other data types as-is

# Create User
@router.post("/create-user")
async def create_user(first_name: str, last_name: str, email_id: str, emp_code: str, role_id: int, status: str, create_by: str, updated_by: str, db: AsyncSession = Depends(get_db)):
    try:
        # Check if role_id exists
        role_query = text("SELECT id FROM role_config WHERE id = :role_id")
        role_result = await db.execute(role_query, {"role_id": role_id})
        role = role_result.fetchone()

        if not role:
            raise HTTPException(status_code=400, detail="Invalid role_id. Role does not exist.")

        # Insert user data
        query = text("""
            INSERT INTO user_config (first_name, last_name, email_id, emp_code, role_id, status, create_by, updated_by, create_date, last_updated_date)
            VALUES (:first_name, :last_name, :email_id, :emp_code, :role_id, :status, :create_by, :updated_by, NOW(), NOW())
        """)
        await db.execute(query, {
            "first_name": first_name,
            "last_name": last_name,
            "email_id": email_id,
            "emp_code": emp_code,
            "role_id": role_id,
            "status": status,
            "create_by": create_by,
            "updated_by": updated_by
        })
        await db.commit()
        return JSONResponse(content={"message": "User created successfully"}, status_code=201)
    except Exception as e:
        print("Error:", str(e))  # Debugging
        raise HTTPException(status_code=500, detail="Database error")

# Get All Users
@router.get("/get-users")
async def get_users(db: AsyncSession = Depends(get_db)):
    try:
        query = text("SELECT * FROM user_config")
        result = await db.execute(query)
        users = result.mappings().all()

        # Convert RowMapping to list of dictionaries
        user_list = [{key: convert_datetime(value) for key, value in dict(row).items()} for row in users]

        return JSONResponse(content={"data": user_list}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# Get User by ID
@router.get("/get-user/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("SELECT * FROM user_config WHERE id = :user_id")
        result = await db.execute(query, {"user_id": user_id})
        user = result.mappings().first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

        user_dict = {key: convert_datetime(value) for key, value in dict(user).items()}

        return JSONResponse(content={"data": user_dict}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# Update User
@router.put("/update-user/{user_id}")
async def update_user(user_id: int, first_name: str, last_name: str, email_id: str, emp_code: str, role_id: int, status: str, updated_by: str, db: AsyncSession = Depends(get_db)):
    try:
        # Check if role_id exists
        role_query = text("SELECT id FROM role_config WHERE id = :role_id")
        role_result = await db.execute(role_query, {"role_id": role_id})
        role = role_result.fetchone()

        if not role:
            raise HTTPException(status_code=400, detail="Invalid role_id. Role does not exist.")

        query = text("""
            UPDATE user_config 
            SET first_name = :first_name, last_name = :last_name, email_id = :email_id, emp_code = :emp_code, role_id = :role_id, status = :status, updated_by = :updated_by, last_updated_date = NOW()
            WHERE id = :user_id
        """)
        await db.execute(query, {
            "first_name": first_name,
            "last_name": last_name,
            "email_id": email_id,
            "emp_code": emp_code,
            "role_id": role_id,
            "status": status,
            "updated_by": updated_by,
            "user_id": user_id
        })
        await db.commit()
        return JSONResponse(content={"message": "User updated successfully"}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")

# Delete User
@router.delete("/delete-user/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("DELETE FROM user_config WHERE id = :user_id")
        await db.execute(query, {"user_id": user_id})
        await db.commit()
        return JSONResponse(content={"message": "User deleted successfully"}, status_code=200)
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")
