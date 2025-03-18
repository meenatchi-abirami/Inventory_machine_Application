from fastapi import Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import AsyncGenerator
from sqlalchemy import text
# Application modules
from src.database_config import get_db
from src.seedwork.models.status_msg_model import StatusMessage


async def inventory_list(db_engine: AsyncGenerator = Depends(get_db)):
    inventory_list_query = await db_engine.execute(text("""select * from category_config cc where cc.id =
            (select category_id from inventory_config where status = 'Active' group by (category_id))
            and cc.status = 'Active'"""))
    inventory_list_data = inventory_list_query.mappings().all()
    if len(inventory_list_data) == 0:
        raise HTTPException(status_code= 404, detail=[{"msg":StatusMessage.s_404}])
    return JSONResponse(content={"data":inventory_list_data}, status_code= 200)

async def category_list(pk:int = Query(default=None),db_engine: AsyncGenerator = Depends(get_db)):
    query = "select * from category_config"
    if pk:
        query += " where id = :pk"
    category_list_query = await db_engine.execute(text(query), {"pk":pk})
    category_list_data = category_list_query.mappings().all()
    if len(category_list_data) == 0:
        raise HTTPException(status_code= 404, detail=[{"msg":StatusMessage.s_404}])
    return JSONResponse(content={"data":category_list_data}, status_code=200)