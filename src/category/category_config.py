from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.responses import JSONResponse
from datetime import datetime
from sqlalchemy import bindparam 
import base64
from typing import Optional
from src.database_config import get_db  

router = APIRouter(prefix="/category-handler")


# Function to convert datetime to string for JSON response
def convert_datetime(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


@router.post("/create-category")
async def create_category(
    name: str = Form(...),
    status: str = Form("active"),
    create_by: str = Form(...),  # Taking emp_code instead of user_id
    last_updated_by: str = Form(...),  # Taking emp_code instead of user_id
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validate create_by and last_updated_by (convert emp_code to user_id)
        user_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")

        # Validate create_by
        result = await db.execute(user_query, {"emp_code": create_by})
        user_data = result.fetchone()
        if not user_data:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {create_by} not found."})
        create_by_id = user_data.id

        # Validate last_updated_by
        result = await db.execute(user_query, {"emp_code": last_updated_by})
        user_data = result.fetchone()
        if not user_data:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {last_updated_by} not found."})
        last_updated_by_id = user_data.id

        # Read and store image as binary
        image_blob = None
        if file:
            image_blob = await file.read()

        # Insert into category_config
        query = text("""
            INSERT INTO category_config (name, picture_blob, status, create_by, last_updated_by, create_date, last_updated_date)
            VALUES (:name, :image_blob, :status, :create_by, :last_updated_by, NOW(), NOW())
        """)
        await db.execute(query, {
            "name": name, "image_blob": image_blob, "status": status,
            "create_by": create_by_id, "last_updated_by": last_updated_by_id
        })
        await db.commit()

        return JSONResponse(content={"message": "Category created successfully"}, status_code=201)

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")


# 2️⃣ **Get Category by ID (With Image)**
@router.get("/get-category/{category_id}")
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT id, name, picture_blob, status, create_by, last_updated_by, create_date, last_updated_date
            FROM category_config WHERE id = :category_id
        """)
        result = await db.execute(query, {"category_id": category_id})
        category = result.mappings().first()

        if not category:
            raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")

        category_dict = {key: convert_datetime(value) for key, value in dict(category).items()}

        # Convert image blob to Base64 string
        if category["picture_blob"]:
            category_dict["picture_blob"] = base64.b64encode(category["picture_blob"]).decode("utf-8")

        return JSONResponse(content={"data": category_dict}, status_code=200)

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")


# # 3️⃣ **Get All Categories (With Images)**
# @router.get("/get-all-categories")
# async def get_all_categories(db: AsyncSession = Depends(get_db)):
#     try:
#         query = text("""
#             SELECT id, name, picture_blob, status, create_by, last_updated_by, create_date, last_updated_date
#             FROM category_config
#         """)
#         result = await db.execute(query)
#         categories = result.mappings().all()

#         category_list = []
#         for category in categories:
#             category_dict = {key: convert_datetime(value) for key, value in dict(category).items()}
            
#             # Convert image blob to Base64 string
#             if category["picture_blob"]:
#                 category_dict["picture_blob"] = base64.b64encode(category["picture_blob"]).decode("utf-8")
            
#             category_list.append(category_dict)

#         return JSONResponse(content={"data": category_list}, status_code=200)

#     except Exception as e:
#         print("Error:", str(e))
#         raise HTTPException(status_code=500, detail="Database error")

@router.get("/get-all-categories")
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT c.id, c.name, c.picture_blob, c.status, 
                   uc1.emp_code AS create_by, 
                   uc2.emp_code AS last_updated_by, 
                   c.create_date, c.last_updated_date
            FROM category_config c
            LEFT JOIN user_config uc1 ON c.create_by = uc1.id
            LEFT JOIN user_config uc2 ON c.last_updated_by = uc2.id
        """)
        result = await db.execute(query)
        categories = result.mappings().all()

        category_list = []
        for category in categories:
            category_dict = {key: convert_datetime(value) for key, value in dict(category).items()}
            
            # Convert image blob to Base64 string
            if category["picture_blob"]:
                category_dict["picture_blob"] = base64.b64encode(category["picture_blob"]).decode("utf-8")
            
            category_list.append(category_dict)

        return JSONResponse(content={"data": category_list}, status_code=200)

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/update-category/{category_id}")
async def update_category(
    category_id: int,
    name: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    last_updated_by: str = Form(...),  # Taking emp_code instead of user_id
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Convert emp_code to user_id
        user_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")
        result = await db.execute(user_query, {"emp_code": last_updated_by})
        user_data = result.fetchone()
        if not user_data:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {last_updated_by} not found."})
        last_updated_by_id = user_data.id

        # Fetch existing category details
        query = text("SELECT name, status, picture_blob FROM category_config WHERE id = :category_id")
        result = await db.execute(query, {"category_id": category_id})
        category = result.mappings().first()

        if not category:
            raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")

        # Keep existing image unless a new file is uploaded
        image_data = category["picture_blob"]
        if file:
            image_data = await file.read()  # Keep as raw bytes (No Base64 encoding)

        updated_values = {
            "name": name if name else category["name"],
            "status": status if status else category["status"],
            "image": image_data,  # Store as raw bytes
            "last_updated_by": last_updated_by_id
        }

        # Update query (Store image as BLOB, not Base64)
        query = text("""
            UPDATE category_config
            SET name = :name, status = :status, picture_blob = :image,
                last_updated_by = :last_updated_by, last_updated_date = NOW()
            WHERE id = :category_id
        """)

        # Log the updated values for debugging
        print("Updated Values:", updated_values)

        await db.execute(query, {**updated_values, "category_id": category_id})
        await db.commit()

        return JSONResponse(content={"message": "Category updated successfully"}, status_code=200)

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# 5️⃣ **Delete Category**
@router.delete("/delete-category/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Check if category exists
        check_query = text("SELECT id FROM category_config WHERE id = :category_id")
        result = await db.execute(check_query, {"category_id": category_id})
        category = result.mappings().first()

        if not category:
            raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")

        # Delete category
        query = text("DELETE FROM category_config WHERE id = :category_id")
        await db.execute(query, {"category_id": category_id})
        await db.commit()

        return JSONResponse(content={"message": "Category deleted successfully"}, status_code=200)

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Database error")
