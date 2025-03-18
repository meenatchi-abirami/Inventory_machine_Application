from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, AsyncGenerator
from src.database_config import get_db
from src.inventory.schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/user-config", tags=["User Config"])

# ✅ Create a New User
@router.post("/create", response_model=UserResponse)
async def create_user(user_data: UserCreate, db_engine: AsyncGenerator = Depends(get_db)):
    try:
        query = text("""
            INSERT INTO user_config (first_name, last_name, email_id, emp_code, role_id, status, create_by, updated_by, create_date, last_updated_date)
            VALUES (:first_name, :last_name, :email_id, :emp_code, :role_id, :status, :create_by, :updated_by, NOW(), NOW())
        """)

        result = await db_engine.execute(query, user_data.dict())
        await db_engine.commit()

        return JSONResponse(content={"msg": "User created successfully", "id": result.lastrowid}, status_code=201)

    except SQLAlchemyError as e:
        print(f"Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error")


# ✅ Read All Users
@router.get("/", response_model=List[UserResponse])
async def get_all_users(db_engine: AsyncGenerator = Depends(get_db)):
    query = text("SELECT * FROM user_config")
    users = await db_engine.execute(query)
    users_data = users.mappings().all()

    if not users_data:
        raise HTTPException(status_code=404, detail="No users found")

    return users_data


# ✅ Read User by ID
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db_engine: AsyncGenerator = Depends(get_db)):
    query = text("SELECT * FROM user_config WHERE id = :user_id")
    user = await db_engine.execute(query, {"user_id": user_id})
    user_data = user.mappings().first()

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return user_data


# ✅ Update User
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db_engine: AsyncGenerator = Depends(get_db)):
    try:
        query = text("""
            UPDATE user_config 
            SET first_name = :first_name, last_name = :last_name, email_id = :email_id,
                emp_code = :emp_code, role_id = :role_id, status = :status, 
                updated_by = :updated_by, last_updated_date = NOW()
            WHERE id = :user_id
        """)

        result = await db_engine.execute(query, {**user_data.dict(), "user_id": user_id})
        await db_engine.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(content={"msg": "User updated successfully"}, status_code=200)

    except SQLAlchemyError as e:
        print(f"Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


# ✅ Delete User
@router.delete("/{user_id}")
async def delete_user(user_id: int, db_engine: AsyncGenerator = Depends(get_db)):
    try:
        query = text("DELETE FROM user_config WHERE id = :user_id")
        result = await db_engine.execute(query, {"user_id": user_id})
        await db_engine.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(content={"msg": "User deleted successfully"}, status_code=200)

    except SQLAlchemyError as e:
        print(f"Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
