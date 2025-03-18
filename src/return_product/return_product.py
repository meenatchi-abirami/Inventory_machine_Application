from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from fastapi.responses import JSONResponse
from src.database_config import get_db  # Import your database session dependency
import base64

router = APIRouter()

# @router.get("/return-products/{emp_code}")
# async def get_return_categories(emp_code: str, db: AsyncSession = Depends(get_db)):
#     try:
#         # Step 1: Convert emp_code to user_id
#         get_user_id_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")
#         result = await db.execute(get_user_id_query, {"emp_code": emp_code})
#         user_data = result.fetchone()

#         if not user_data:
#             return JSONResponse(status_code=404, content={"message": f"User with emp_code {emp_code} not found."})

#         user_id = user_data.id  # Extract user_id

#         # Step 2: Fetch active items taken by the user along with taken date and item_code
#         get_user_items_query = text("""
#             SELECT 
#                 ic.item_code,  -- Fetching item_code
#                 ic.name AS product_name, 
#                 ic.category_id, 
#                 ic.price, 
#                 ic.picture_blob, 
#                 c.name AS category_name,
#                 il.create_date AS product_taken_date,  -- Taken Date
#                 NOW() AS product_return_date,          -- Current Date (simulating return date)
#                 DATEDIFF(NOW(), il.create_date) AS days_used  -- Difference in days
#             FROM inventory_listings il
#             JOIN inventory_config ic ON il.inventory_id = ic.id
#             JOIN category_config c ON ic.category_id = c.id
#             WHERE il.emp_id = :user_id AND il.status = 'Active'
#         """)
#         result = await db.execute(get_user_items_query, {"user_id": user_id})
#         products = result.fetchall()

#         if not products:
#             return JSONResponse(status_code=404, content={"message": "No active products to return."})

#         # Format the response
#         product_list = []
#         for row in products:
#             product_image = (
#                 base64.b64encode(row.picture_blob).decode("utf-8") if row.picture_blob else None
#             )

#             product_list.append({
#                 "item_code": row.item_code,  # Added item_code
#                 "product_name": row.product_name,
#                 "category_id": row.category_id,
#                 "category_name": row.category_name,
#                 "price": row.price,
#                 "product_image": product_image,
#                 "product_taken_date": row.product_taken_date.strftime("%Y-%m-%d %H:%M:%S") if row.product_taken_date else None,
#                 "product_return_date": row.product_return_date.strftime("%Y-%m-%d %H:%M:%S") if row.product_return_date else None,
#                 "days_used": row.days_used if row.days_used is not None else 0
#             })

#         return JSONResponse(status_code=200, content={"products": product_list})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})


@router.get("/return-products/{emp_code}")
async def get_return_categories(emp_code: str, db: AsyncSession = Depends(get_db)):
    try:
        # Step 1: Convert emp_code to user_id
        get_user_id_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")
        result = await db.execute(get_user_id_query, {"emp_code": emp_code})
        user_data = result.fetchone()

        if not user_data:
            return JSONResponse(status_code=404, content={"message": f"User with emp_code {emp_code} not found."})

        user_id = user_data[0]  # Extract user_id

        # Step 2: Fetch active items taken by the user along with taken date and item_code
        get_user_items_query = text("""
            SELECT 
                ic.item_code,  
                ic.name AS product_name, 
                ic.category_id, 
                ic.price, 
                ic.picture_blob, 
                c.name AS category_name,
                il.create_date AS product_taken_date,  
                NOW() AS product_return_date,          
                TIMESTAMPDIFF(HOUR, il.create_date, NOW()) AS hours_used  -- ✅ Calculate hours used
            FROM inventory_listings il
            JOIN inventory_config ic ON il.inventory_id = ic.id
            JOIN category_config c ON ic.category_id = c.id
            WHERE il.emp_id = :user_id AND il.status = 'Active'
        """)
        result = await db.execute(get_user_items_query, {"user_id": user_id})
        products = result.fetchall()

        if not products:
            return JSONResponse(status_code=404, content={"message": "No active products to return."})

        # Format the response
        product_list = []
        for row in products:
            product_image = (
                base64.b64encode(row.picture_blob).decode("utf-8") if row.picture_blob else None
            )

            product_list.append({
                "item_code": row.item_code,
                "product_name": row.product_name,
                "category_id": row.category_id,
                "category_name": row.category_name,
                "price": row.price,
                "product_image": product_image,
                "product_taken_date": row.product_taken_date.strftime("%Y-%m-%d %H:%M:%S") if row.product_taken_date else None,
                "product_return_date": row.product_return_date.strftime("%Y-%m-%d %H:%M:%S") if row.product_return_date else None,
                "hours_used": row.hours_used if row.hours_used is not None else 0  # ✅ Show hours used
            })

        return JSONResponse(status_code=200, content={"products": product_list})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})

@router.post("/return-product/{emp_code}/{item_code}")
async def return_product(emp_code: str, item_code: str, db: AsyncSession = Depends(get_db)):
    try:
        # Step 1: Fetch user_id using emp_code
        get_user_id_query = text("SELECT id FROM user_config WHERE emp_code = :emp_code")
        result = await db.execute(get_user_id_query, {"emp_code": emp_code})
        user_data = result.fetchone()

        if not user_data:
            return JSONResponse(status_code=404, content={"message": "User not found."})

        user_id = user_data.id

        # Step 2: Fetch inventory_id using item_code
        get_inventory_id_query = text("SELECT id FROM inventory_config WHERE item_code = :item_code")
        result = await db.execute(get_inventory_id_query, {"item_code": item_code})
        inventory_data = result.fetchone()

        if not inventory_data:
            return JSONResponse(status_code=404, content={"message": "Invalid item_code."})

        inventory_id = inventory_data.id

        # Step 3: Check if the user has this product in inventory_listings
        check_query = text("""
            SELECT id FROM inventory_listings
            WHERE inventory_id = :inventory_id AND emp_id = :user_id AND status = 'Active'
        """)
        result = await db.execute(check_query, {"inventory_id": inventory_id, "user_id": user_id})
        listing_data = result.fetchone()

        if not listing_data:
            return JSONResponse(status_code=400, content={"message": "You can't return this item."})

        listing_id = listing_data.id

        # Step 4: Update inventory_listings to mark as returned
        update_listing_query = text("""
            UPDATE inventory_listings 
            SET status = 'Returned', reasons = 'return', last_updated_by = :user_id, last_updated_date = NOW()
            WHERE id = :listing_id
        """)
        await db.execute(update_listing_query, {"user_id": user_id, "listing_id": listing_id})

        # Step 5: Update inventory_config to set status back to Active
        update_inventory_status_query = text("""
            UPDATE inventory_config SET status = 'Active' WHERE id = :inventory_id
        """)
        await db.execute(update_inventory_status_query, {"inventory_id": inventory_id})

        # Commit transaction
        await db.commit()

        return JSONResponse(status_code=200, content={"message": "Product returned successfully."})

    except Exception as e:
        await db.rollback()  # Rollback in case of any error
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})
