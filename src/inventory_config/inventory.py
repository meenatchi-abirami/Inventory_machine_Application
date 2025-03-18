import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.responses import JSONResponse
from datetime import datetime
import base64
from typing import List
from src.database_config import get_db  

router = APIRouter(prefix="/inventory_config")


# Function to convert datetime to string for JSON response
def convert_datetime(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


# @router.post("/create-inventory")
# async def create_inventory(
#     item_code: str = Form(...),
#     category_name: str = Form(...),  # Take category name instead of ID
#     status: str = Form("Active"),
#     create_by: str = Form(...),  # Taking emp_code instead of user_id
#     last_updated_by: str = Form(...),  # Taking emp_code instead of user_id
#     name: str = Form(...),
#     price: int = Form(0),
#     file: UploadFile = File(None),  # Mandatory image upload
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         # Fetch category_id using category_name
#         category_query = text("SELECT id FROM category_config WHERE name = :category_name")
#         result = await db.execute(category_query, {"category_name": category_name})
#         category_data = result.fetchone()
#         if not category_data:
#             return JSONResponse(status_code=404, content={"message": f"Category '{category_name}' not found."})
#         category_id = category_data.id  # Get the ID

#         # Validate create_by and last_updated_by (convert emp_code to user_id)
#         user_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")

#         # Validate create_by
#         result = await db.execute(user_query, {"emp_code": create_by})
#         user_data = result.fetchone()
#         if not user_data:
#             return JSONResponse(status_code=404, content={"message": f"User with emp_code {create_by} not found."})
#         create_by_id = user_data.id

#         # Validate last_updated_by
#         result = await db.execute(user_query, {"emp_code": last_updated_by})
#         user_data = result.fetchone()
#         if not user_data:
#             return JSONResponse(status_code=404, content={"message": f"User with emp_code {last_updated_by} not found."})
#         last_updated_by_id = user_data.id

#         # Convert image to base64 (image is mandatory)
#         image_data = await file.read()
#         if not image_data:
#             return JSONResponse(status_code=400, content={"message": "Image upload is required."})
#         image_base64 = base64.b64encode(image_data).decode("utf-8")

#         # Insert into inventory_config
#         query = text("""
#             INSERT INTO inventory_config 
#             (item_code, category_id, status, create_by, last_updated_by, create_date, last_updated_date, name, price, picture_blob)
#             VALUES 
#             (:item_code, :category_id, :status, :create_by, :last_updated_by, NOW(), NOW(), :name, :price, :image)
#         """)
#         await db.execute(query, {
#             "item_code": item_code, "category_id": category_id, "status": status,
#             "create_by": create_by_id, "last_updated_by": last_updated_by_id,
#             "name": name, "price": price, "image": image_base64
#         })
#         await db.commit()
        
#         return JSONResponse(content={"message": "Inventory item created successfully"}, status_code=201)

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})


@router.post("/create-inventory")
async def create_inventory(
    item_code: str = Form(...),
    category_name: str = Form(...),  # Take category name instead of ID
    name: str = Form(...),  # ✅ Mandatory field (will raise 422 error if missing)
    status: str = Form("Active"),
    create_by: str = Form(...),  # Taking emp_code instead of user_id
    last_updated_by: str = Form(...),  # Taking emp_code instead of user_id
    price: int = Form(0),  # ✅ Default price is 0
    file: UploadFile = File(None),  # ✅ Image is optional (NULL if not uploaded)
    db: AsyncSession = Depends(get_db)
):
    try:
        # Fetch category_id using category_name
        category_query = text("SELECT id FROM category_config WHERE name = :category_name")
        result = await db.execute(category_query, {"category_name": category_name})
        category_data = result.fetchone()
        if not category_data:
            return JSONResponse(status_code=404, content={"message": f"Category '{category_name}' not found."})
        category_id = category_data.id  # Get the ID

        # Validate create_by and last_updated_by (convert emp_code to user_id)
        user_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")

        async def get_user_id(emp_code):
            result = await db.execute(user_query, {"emp_code": emp_code})
            user_data = result.fetchone()
            return user_data.id if user_data else None

        create_by_id = await get_user_id(create_by)
        last_updated_by_id = await get_user_id(last_updated_by)

        if not create_by_id:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {create_by} not found."})
        if not last_updated_by_id:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {last_updated_by} not found."})

        # Check if image is uploaded (allow NULL)
        image_data = await file.read() if file else None

        # Insert into inventory_config
        query = text("""
            INSERT INTO inventory_config 
            (item_code, category_id, status, create_by, last_updated_by, create_date, last_updated_date, name, price, picture_blob)
            VALUES 
            (:item_code, :category_id, :status, :create_by, :last_updated_by, NOW(), NOW(), :name, :price, :image)
        """)
        await db.execute(query, {
            "item_code": item_code, "category_id": category_id, "status": status,
            "create_by": create_by_id, "last_updated_by": last_updated_by_id,
            "name": name, "price": price, "image": image_data
        })
        await db.commit()

        return JSONResponse(content={"message": "Inventory item created successfully"}, status_code=201)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})


# 2️⃣ **Get Inventory Item by ID**
@router.get("/get-inventory/{inventory_id}")
async def get_inventory(inventory_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT id, item_code, category_id, status, create_by, last_updated_by, 
                   create_date, last_updated_date, name, price, picture_blob
            FROM inventory_config WHERE id = :inventory_id
        """)
        result = await db.execute(query, {"inventory_id": inventory_id})
        inventory = result.mappings().first()

        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory item with ID {inventory_id} not found")

        inventory_dict = {key: convert_datetime(value) for key, value in dict(inventory).items()}

        # Convert picture_blob to Base64
        if "picture_blob" in inventory_dict:
            picture_blob = inventory_dict["picture_blob"]
            if picture_blob and isinstance(picture_blob, bytes):
                print(f"Encoding Picture BLOB: {type(picture_blob)}")  # Debugging
                inventory_dict["picture_blob"] = base64.b64encode(picture_blob).decode("utf-8")
            else:
                print("No picture BLOB found or not in bytes format")  # Debugging
                inventory_dict["picture_blob"] = None  # Ensure JSON serializability

        return JSONResponse(content={"data": inventory_dict}, status_code=200)

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# @router.get("/get-all-inventory")
# async def get_all_inventory(db: AsyncSession = Depends(get_db)):
#     try:
#         query = text("""
#             SELECT ic.id, ic.item_code, ic.category_id, ic.status, 
#                    uc1.emp_code AS create_by, uc2.emp_code AS last_updated_by, 
#                    ic.create_date, ic.last_updated_date, ic.name, ic.price, ic.picture_blob
#             FROM inventory_config ic
#             LEFT JOIN user_config uc1 ON ic.create_by = uc1.id
#             LEFT JOIN user_config uc2 ON ic.last_updated_by = uc2.id
#         """)
#         result = await db.execute(query)
#         inventory_list = result.mappings().all()

#         inventories = []
#         for item in inventory_list:
#             item_dict = {key: convert_datetime(value) for key, value in dict(item).items()}

#             # Handle picture_blob
#             if "picture_blob" in item_dict:
#                 picture_blob = item_dict["picture_blob"]
#                 if picture_blob and isinstance(picture_blob, bytes):
#                     item_dict["picture_blob"] = base64.b64encode(picture_blob).decode("utf-8")
#                 else:
#                     item_dict["picture_blob"] = None  # Ensure JSON serializable

#             inventories.append(item_dict)

#         return JSONResponse(content={"data": inventories}, status_code=200)

#     except Exception as e:
#         print("Error:", str(e))
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/get-all-inventory")
async def get_all_inventory(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT ic.id, ic.item_code, cc.name AS category_name, ic.status, 
                   uc1.emp_code AS create_by, uc2.emp_code AS last_updated_by, 
                   ic.create_date, ic.last_updated_date, ic.name, ic.price, ic.picture_blob
            FROM inventory_config ic
            LEFT JOIN category_config cc ON ic.category_id = cc.id  -- Join to get category name
            LEFT JOIN user_config uc1 ON ic.create_by = uc1.id
            LEFT JOIN user_config uc2 ON ic.last_updated_by = uc2.id
        """)
        result = await db.execute(query)
        inventory_list = result.mappings().all()

        inventories = []
        for item in inventory_list:
            item_dict = {key: convert_datetime(value) for key, value in dict(item).items()}

            # Handle picture_blob
            if "picture_blob" in item_dict:
                picture_blob = item_dict["picture_blob"]
                if picture_blob and isinstance(picture_blob, bytes):
                    item_dict["picture_blob"] = base64.b64encode(picture_blob).decode("utf-8")
                else:
                    item_dict["picture_blob"] = None  # Ensure JSON serializable

            inventories.append(item_dict)

        return JSONResponse(content={"data": inventories}, status_code=200)

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/inventory/{inventory_id}")
async def update_inventory(
    inventory_id: int,
    item_code: str = Form(None),
    category_name: str = Form(None),
    status: str = Form(None),
    last_updated_by: str = Form(...),  # Must provide emp_code
    name: str = Form(None),
    price: int = Form(None),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Fetch existing inventory
        query = text("SELECT * FROM inventory_config WHERE id = :inventory_id")
        result = await db.execute(query, {"inventory_id": inventory_id})
        inventory_data = result.fetchone()
        if not inventory_data:
            return JSONResponse(status_code=404, content={"message": "Inventory item not found."})

        update_data = {}

        # Update category_id if category_name is provided
        if category_name:
            category_query = text("SELECT id FROM category_config WHERE name = :category_name")
            result = await db.execute(category_query, {"category_name": category_name})
            category_data = result.fetchone()
            if not category_data:
                return JSONResponse(status_code=404, content={"message": f"Category '{category_name}' not found."})
            update_data["category_id"] = category_data.id

        # Validate last_updated_by (convert emp_code to user_id)
        user_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")
        result = await db.execute(user_query, {"emp_code": last_updated_by})
        user_data = result.fetchone()
        if not user_data:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {last_updated_by} not found."})
        update_data["last_updated_by"] = user_data.id

        # Convert image to base64 if file is provided
        if file:
            image_data = await file.read()
            if image_data:
                update_data["picture_blob"] = base64.b64encode(image_data).decode("utf-8")

        # Only add fields that are provided in the request
        if item_code:
            update_data["item_code"] = item_code
        if status:
            update_data["status"] = status
        if name:
            update_data["name"] = name
        if price is not None:
            update_data["price"] = price

        # Debugging: Print update_data to verify what is being updated
        print("Update Data:", update_data)

        # If no fields are updated, return a message
        if not update_data:
            return JSONResponse(status_code=400, content={"message": "No fields provided for update."})

        # Update fields dynamically
        update_fields = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        update_query = text(f"""
            UPDATE inventory_config 
            SET {update_fields}, last_updated_date = NOW() 
            WHERE id = :inventory_id
        """)
        update_data["inventory_id"] = inventory_id
        result = await db.execute(update_query, update_data)

        # Debugging: Check if the query affected any rows
        if result.rowcount == 0:
            return JSONResponse(status_code=400, content={"message": "No changes were made to the inventory item."})

        await db.commit()

        return JSONResponse(content={"message": "Inventory updated successfully"}, status_code=200)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})


# 5️⃣ **Delete Inventory Item**
# @router.delete("/delete-inventory/{inventory_id}")
# async def delete_inventory(inventory_id: int, db: AsyncSession = Depends(get_db)):
#     try:
#         query = text("DELETE FROM inventory_config WHERE id = :inventory_id")
#         await db.execute(query, {"inventory_id": inventory_id})
#         await db.commit()

#         return JSONResponse(content={"message": "Inventory item deleted successfully"}, status_code=200)

#     except Exception as e:
#         print("Error:", str(e))
#         raise HTTPException(status_code=500, detail="Database error")

@router.delete("/delete-inventory/{item_code}")
async def delete_inventory(item_code: str, db: AsyncSession = Depends(get_db)):
    try:
        # Get inventory ID based on item_code
        query_get_id = text("SELECT id FROM inventory_config WHERE item_code = :item_code")
        result = await db.execute(query_get_id, {"item_code": item_code})
        inventory_id = result.scalar()

        if not inventory_id:
            raise HTTPException(status_code=404, detail="Inventory item not found")

        # Delete from inventory_unreturned_listings
        await db.execute(text("DELETE FROM inventory_unreturned_listings WHERE listing_id IN "
                              "(SELECT id FROM inventory_listings WHERE inventory_id = :inventory_id)"),
                         {"inventory_id": inventory_id})

        # Delete from inventory_damaged_listings
        await db.execute(text("DELETE FROM inventory_damaged_listings WHERE listing_id IN "
                              "(SELECT id FROM inventory_listings WHERE inventory_id = :inventory_id)"),
                         {"inventory_id": inventory_id})

        # Delete from inventory_listings
        await db.execute(text("DELETE FROM inventory_listings WHERE inventory_id = :inventory_id"),
                         {"inventory_id": inventory_id})

        # Delete from inventory_config
        await db.execute(text("DELETE FROM inventory_config WHERE id = :inventory_id"),
                         {"inventory_id": inventory_id})

        await db.commit()  # Commit changes after successful deletion

        return JSONResponse(content={"message": "Inventory item deleted successfully"}, status_code=200)

    except Exception as e:
        print("Error:", str(e))
        await db.rollback()  # Rollback in case of failure
        raise HTTPException(status_code=500, detail="Database error")
