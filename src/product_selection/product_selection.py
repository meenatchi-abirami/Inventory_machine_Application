from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from starlette.responses import JSONResponse
import base64
from src.database_config import get_db

router = APIRouter()

@router.get("/inventory/unique-products")
async def get_unique_products(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT 
                i.name, 
                MIN(i.category_id) AS category_id, 
                COALESCE(MAX(i.price), 0) AS price,  
                c.picture_blob AS category_image  
            FROM inventory_config i
            JOIN category_config c ON i.category_id = c.id  
            WHERE i.status = 'Active' 
            AND i.id NOT IN (SELECT inventory_id FROM inventory_listings WHERE status = 'Active') 
            GROUP BY i.name, c.picture_blob
        """)
        result = await db.execute(query)
        products = result.fetchall()

        if not products:
            return JSONResponse(status_code=404, content={"message": "No products found"})

        product_list = [
            {
                "product_name": row.name,
                "category_id": row.category_id,
                "price": row.price,
                "product_image": base64.b64encode(row.category_image).decode("utf-8") if row.category_image else None
            }
            for row in products
        ]

        return {"unique_products": product_list}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})


@router.post("/select-product/{emp_code}/{product_name}")
async def take_product(emp_code: str, product_name: str, db: AsyncSession = Depends(get_db)):
    try:
        # Step 1: Fetch user_id using emp_code
        get_user_id_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")
        result = await db.execute(get_user_id_query, {"emp_code": emp_code})
        user_data = result.fetchone()

        if not user_data:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {emp_code} not found."})

        user_id = user_data.id  # Extract user_id

        # Step 2: Check if the user has an unreturned product
        check_unreturned_query = text("""
            SELECT id FROM inventory_unreturned_listings 
            WHERE create_by = :user_id AND status = 'Active'
        """)
        result = await db.execute(check_unreturned_query, {"user_id": user_id})
        unreturned_item = result.fetchone()

        if unreturned_item:
            return JSONResponse(status_code=400, content={"message": "Please return your previous product first."})

        # Step 3: Ensure the user is not taking the same product multiple times
        check_existing_query = text("""
            SELECT id FROM inventory_listings 
            WHERE create_by = :user_id 
            AND inventory_id IN (SELECT id FROM inventory_config WHERE name = :product_name) 
            AND status = 'Active'
        """)
        result = await db.execute(check_existing_query, {"product_name": product_name, "user_id": user_id})
        existing_entry = result.fetchone()

        if existing_entry:
            return JSONResponse(status_code=400, content={"message": "You have already taken this product."})

        # Step 4: Get an available inventory_id and item_code from inventory_config
        get_inventory_id_query = text("""
            SELECT id, item_code FROM inventory_config 
            WHERE name = :product_name AND status = 'Active' LIMIT 1
        """)
        result = await db.execute(get_inventory_id_query, {"product_name": product_name})
        inventory_data = result.fetchone()

        if not inventory_data:
            return JSONResponse(status_code=404, content={"message": "Product not found or inactive."})

        inventory_id, item_code = inventory_data  # Extract inventory_id and item_code

        # Step 5: Insert into inventory_listings with 'take' reason
        insert_inventory_query = text("""
            INSERT INTO inventory_listings (inventory_id, create_by, last_updated_by, emp_id, status, reasons)
            VALUES (:inventory_id, :user_id, :user_id, :user_id, 'Active', 'take')
        """)
        await db.execute(insert_inventory_query, {"inventory_id": inventory_id, "user_id": user_id})

        # Step 6: Mark the product as inactive in inventory_config
        update_inventory_status_query = text("""
            UPDATE inventory_config SET status = 'Inactive' WHERE id = :inventory_id
        """)
        await db.execute(update_inventory_status_query, {"inventory_id": inventory_id})

        await db.commit()

        return JSONResponse(status_code=200, content={
            "message": "Product selected successfully.",
            "item_code": item_code  # Returning the item_code
        })

    except Exception as e:
        await db.rollback()  # Rollback in case of any error
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})


# Get all categories
@router.get("/categories")
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT id, name, picture_blob FROM category_config WHERE status = 'Active'"))
        categories = result.fetchall()  

        if not categories:
            return JSONResponse(status_code=404, content={"message": "No categories found"})

        category_list = [
            {
                "category_id": row.id,
                "category_name": row.name,
                "category_image": base64.b64encode(row.picture_blob).decode("utf-8") if row.picture_blob else None
            }
            for row in categories
        ]

        return {"categories": category_list}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})


@router.get("/categories/{category_id}/products")
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            text("SELECT id, item_code, name, price, picture_blob FROM inventory_config WHERE category_id = :category_id AND status = 'Active'"),
            {"category_id": category_id}
        )
        products = result.fetchall()  # Corrected fetchall()

        if not products:
            return {"message": "No products found for this category"}

        product_list = [
            {
                "product_id": row[0],
                "item_code": row[1],
                "product_name": row[2],
                "price": row[3],
                "product_image": base64.b64encode(row[4]).decode("utf-8") if row[4] else None
            }
            for row in products
        ]

        return {"category_id": category_id, "products": product_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")



@router.get("/categories/{category_id}/products")
async def get_products_by_categories(category_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Check if the user has an unreturned item in this category
        unreturned_query = text("""
            SELECT iul.id FROM inventory_unreturned_listings iul
            JOIN inventory_config ic ON iul.listing_id = ic.id
            WHERE ic.category_id = :category_id 
            AND iul.create_by = :user_id
            AND iul.status = 'Active'
        """)
        unreturned_result = await db.execute(unreturned_query, {"category_id": category_id, "user_id": user_id})
        existing_unreturned = unreturned_result.fetchone()

        if existing_unreturned:
            return {"message": "You must return your previous item before purchasing another in this category."}

        # If no unreturned item, fetch all available products in the category
        product_query = text("""
            SELECT id, item_code, name, price, picture_blob 
            FROM inventory_config 
            WHERE category_id = :category_id AND status = 'Active'
        """)
        result = await db.execute(product_query, {"category_id": category_id})
        products = result.fetchall()

        if not products:
            return {"message": "No products found in this category."}

        product_list = [
            {
                "product_id": row[0],
                "item_code": row[1],
                "product_name": row[2],
                "price": row[3],
                "product_image": base64.b64encode(row[4]).decode("utf-8") if row[4] else None
            }
            for row in products
        ]

        return {"products": product_list}

    except Exception as e:
        print(f"Database Error: {e}")  # Log error in terminal
        raise HTTPException(status_code=500, detail=str(e))  # Send error response

 
##---additional product--

# ✅ Function to Check If User Can Take the Product
async def can_user_take_product(user_id: int, product_name: str, db: AsyncSession):
    """
    Checks if the user is eligible to take the product:
    - They must not have another active product (unless it was lost).
    - They can take the same product again only if it was lost.
    """
    # Step 1: Check if the user currently has an active product
    check_active_product_query = text("""
        SELECT inventory_id, reasons FROM inventory_listings 
        WHERE create_by = :user_id AND status = 'Active'
    """)
    result = await db.execute(check_active_product_query, {"user_id": user_id})
    active_product = result.fetchone()

    # Step 2: Check if the user has already taken this product before
    check_previous_count_query = text("""
        SELECT COUNT(*) FROM inventory_listings 
        WHERE create_by = :user_id 
        AND inventory_id IN (SELECT id FROM inventory_config WHERE name = :product_name)
    """)
    result = await db.execute(check_previous_count_query, {"product_name": product_name, "user_id": user_id})
    product_taken_count = result.scalar()

    # Step 3: Check if the user lost the product before
    check_lost_product_query = text("""
        SELECT id FROM inventory_listings 
        WHERE create_by = :user_id 
        AND inventory_id IN (SELECT id FROM inventory_config WHERE name = :product_name) 
        AND reasons = 'lost'
    """)
    result = await db.execute(check_lost_product_query, {"product_name": product_name, "user_id": user_id})
    lost_product = result.fetchone()

    # Step 4: Decision Logic
    if active_product:
        # Allow only if the previous product was lost
        if active_product.reasons == "lost":
            return "take (second time - lost)"  # Allowed due to loss
        else:
            return JSONResponse(status_code=400, content={"message": "You can only take one product at a time."})

    if product_taken_count == 0:
        return "take"  # First-time taking
    elif product_taken_count == 1 and lost_product:
        return "take (second time - lost)"  # Taking again due to loss
    else:
        return JSONResponse(status_code=400, content={"message": "You cannot take this product more than twice."})


# ✅ API Route for Selecting a Product
@router.post("/select-product/{emp_code}/{product_name}")
async def additional_take_product(emp_code: str, product_name: str, db: AsyncSession = Depends(get_db)):
    try:
        # Step 1: Fetch user_id using emp_code
        get_user_id_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")
        result = await db.execute(get_user_id_query, {"emp_code": emp_code})
        user_data = result.fetchone()

        if not user_data:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {emp_code} not found."})

        user_id = user_data.id  # Extract user_id

        # Step 2: Check if the user is allowed to take this product
        reason = await can_user_take_product(user_id, product_name, db)

        if isinstance(reason, JSONResponse):  # If the function returned an error, return it
            return reason

        # Step 3: Get an available inventory_id and item_code from inventory_config
        get_inventory_id_query = text("""
            SELECT id, item_code FROM inventory_config 
            WHERE name = :product_name AND status = 'Active' LIMIT 1
        """)
        result = await db.execute(get_inventory_id_query, {"product_name": product_name})
        inventory_data = result.fetchone()

        if not inventory_data:
            return JSONResponse(status_code=404, content={"message": "Product not found or inactive."})

        inventory_id, item_code = inventory_data  # Extract inventory_id and item_code

        # Step 4: Insert into inventory_listings
        insert_inventory_query = text("""
            INSERT INTO inventory_listings (inventory_id, create_by, last_updated_by, emp_id, status, reasons)
            VALUES (:inventory_id, :user_id, :user_id, :user_id, 'Active', :reason)
        """)
        await db.execute(insert_inventory_query, {"inventory_id": inventory_id, "user_id": user_id, "reason": reason})

        # Step 5: Mark the product as inactive in inventory_config
        update_inventory_status_query = text("""
            UPDATE inventory_config SET status = 'Inactive' WHERE id = :inventory_id
        """)
        await db.execute(update_inventory_status_query, {"inventory_id": inventory_id})

        await db.commit()

        return JSONResponse(status_code=200, content={
            "message": "Product selected successfully.",
            "item_code": item_code,
            "reason": reason  # Returning the reason for logging
        })

    except Exception as e:
        await db.rollback()  # Rollback in case of any error
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})
