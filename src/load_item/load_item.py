from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel
from src.database_config import get_db
from datetime import datetime

def convert_datetime(value):
    """Convert datetime to string format or return as-is for other types."""
    return value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value 

router = APIRouter()

# ✅ Define the Pydantic model for JSON input
class InventoryCreateRequest(BaseModel):
    item_codes: List[str]  # List of item codes
    category_name: str  
    name: str  
    status: str = "Active"
    create_by: str  
    last_updated_by: str  
    price: int = 0  

# @router.post("/load_items", response_model=dict)
# async def load_items(
#     request: InventoryCreateRequest,
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         # ✅ Ensure `item_codes` is a list
#         if not isinstance(request.item_codes, list) or len(request.item_codes) == 0:
#             raise HTTPException(status_code=400, detail="item_codes must be a non-empty list")

#         # ✅ Fetch category_id using category_name
#         category_query = text("SELECT id FROM category_config WHERE name = :category_name")
#         result = await db.execute(category_query, {"category_name": request.category_name})
#         category_data = result.fetchone()
#         if not category_data:
#             raise HTTPException(status_code=404, detail=f"Category '{request.category_name}' not found.")
#         category_id = category_data.id  

#         # ✅ Validate `create_by` and `last_updated_by` (convert emp_code to user_id)
#         user_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")

#         async def get_user_id(emp_code):
#             result = await db.execute(user_query, {"emp_code": emp_code})
#             user_data = result.fetchone()
#             return user_data.id if user_data else None

#         create_by_id = await get_user_id(request.create_by)
#         last_updated_by_id = await get_user_id(request.last_updated_by)

#         if not create_by_id:
#             raise HTTPException(status_code=404, detail=f"User with emp_code {request.create_by} not found.")
#         if not last_updated_by_id:
#             raise HTTPException(status_code=404, detail=f"User with emp_code {request.last_updated_by} not found.")

#         # ✅ Insert each item_code as a **separate row**
#         insert_query = text("""
#             INSERT INTO inventory_config 
#             (item_code, category_id, status, create_by, last_updated_by, create_date, last_updated_date, name, price)
#             VALUES 
#             (:item_code, :category_id, :status, :create_by, :last_updated_by, NOW(), NOW(), :name, :price)
#         """)

#         inserted_count = 0
#         for item_code in request.item_codes:
#             if isinstance(item_code, str) and item_code.strip():  # Ensure it's a valid string
#                 await db.execute(insert_query, {
#                     "item_code": item_code.strip(),  # Trim any spaces
#                     "category_id": category_id, 
#                     "status": request.status,
#                     "create_by": create_by_id, 
#                     "last_updated_by": last_updated_by_id,
#                     "name": request.name, 
#                     "price": request.price
#                 })
#                 inserted_count += 1  # Track successful inserts

#         if inserted_count == 0:
#             raise HTTPException(status_code=400, detail="No valid item_codes were provided for insertion.")

#         await db.commit()

#         return {"message": f"{inserted_count} inventory items created successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# from datetime import datetime

# def convert_datetime(value):
#     """Convert datetime to string format or return as-is for other types."""
#     return value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value

import traceback  # ✅ Import this to capture detailed errors

@router.post("/load_items", response_model=dict)
async def load_items(
    request: InventoryCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        if not isinstance(request.item_codes, list) or len(request.item_codes) == 0:
            raise HTTPException(status_code=400, detail="item_codes must be a non-empty list")

        # ✅ Fetch category_id using category_name
        category_query = text("SELECT id FROM category_config WHERE name = :category_name")
        result = await db.execute(category_query, {"category_name": request.category_name})
        category_data = result.fetchone()
        if not category_data:
            raise HTTPException(status_code=404, detail=f"Category '{request.category_name}' not found.")
        category_id = category_data[0]  # ✅ Extract the category ID

        # ✅ Fetch user IDs
        user_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")

        async def get_user_id(emp_code):
            result = await db.execute(user_query, {"emp_code": emp_code})
            user_data = result.fetchone()
            return user_data[0] if user_data else None  # ✅ Extract the user ID

        create_by_id = await get_user_id(request.create_by)
        last_updated_by_id = await get_user_id(request.last_updated_by)

        if not create_by_id:
            raise HTTPException(status_code=404, detail=f"User with emp_code {request.create_by} not found.")
        if not last_updated_by_id:
            raise HTTPException(status_code=404, detail=f"User with emp_code {request.last_updated_by} not found.")

        # ✅ Insert items
        insert_query = text("""
            INSERT INTO inventory_config 
            (item_code, category_id, status, create_by, last_updated_by, create_date, last_updated_date, name, price)
            VALUES 
            (:item_code, :category_id, :status, :create_by, :last_updated_by, NOW(), NOW(), :name, :price)
        """)

        inserted_count = 0
        try:
            for item_code in request.item_codes:
                if isinstance(item_code, str) and item_code.strip():
                    await db.execute(insert_query, {
                        "item_code": item_code.strip(),  
                        "category_id": category_id, 
                        "status": request.status,
                        "create_by": create_by_id, 
                        "last_updated_by": last_updated_by_id,
                        "name": request.name, 
                        "price": request.price
                    })
                    inserted_count += 1  

            if inserted_count == 0:
                raise HTTPException(status_code=400, detail="No valid item_codes provided.")

            await db.commit()
        except Exception as e:
            await db.rollback()
            print("🔴 Database Insert Error:", traceback.format_exc())  # ✅ Print full error
            raise HTTPException(status_code=500, detail=str(e))

        return {"message": f"{inserted_count} inventory items created successfully"}

    except Exception as e:
        print("🔴 Unexpected Error:", traceback.format_exc())  # ✅ Print full error
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter-products")
async def filter_products(category_name: str, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch category_id using category_name
        get_category_query = text("SELECT id FROM category_config WHERE name = :category_name")
        result = await db.execute(get_category_query, {"category_name": category_name})
        category_data = result.fetchone()

        if not category_data:
            return JSONResponse(status_code=404, content={"message": "Category not found."})

        category_id = category_data.id

        # Fetch products related to the category, fixing the column name issue
        get_products_query = text("""
            SELECT 
                ic.id, ic.item_code, ic.name, ic.status, ic.price, 
                ic.category_id, ic.create_date, ic.last_updated_date, 
                uc1.emp_code AS create_by,  -- ✅ Using the correct column name
                uc2.emp_code AS last_updated_by
            FROM inventory_config ic
            JOIN user_config uc1 ON ic.create_by = uc1.id  -- ✅ Fixed column name
            JOIN user_config uc2 ON ic.last_updated_by = uc2.id
            WHERE ic.category_id = :category_id
        """)
        result = await db.execute(get_products_query, {"category_id": category_id})
        products = result.mappings().all()

        # Convert datetime fields to strings
        product_list = [
            {key: convert_datetime(value) for key, value in dict(product).items()}
            for product in products
        ]

        # Get the count of products
        product_count_query = text("SELECT COUNT(*) AS total FROM inventory_config WHERE category_id = :category_id")
        result = await db.execute(product_count_query, {"category_id": category_id})
        total_products = result.fetchone().total

        return JSONResponse(status_code=200, content={
            "category_name": category_name,
            "category_id": category_id,
            "total_products": total_products,
            "products": product_list
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})
