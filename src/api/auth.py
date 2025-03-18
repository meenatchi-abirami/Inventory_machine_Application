from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import AsyncGenerator
from src.database_config import get_db
from src.seedwork.models.status_msg_model import StatusMessage

router = APIRouter(prefix="/auth-handler")

# ✅ Fetch Employee Role & Allowed Actions
async def get_employee_actions(emp_code: str = Form(...), db_engine: AsyncGenerator = Depends(get_db)):
    query = text("""
        SELECT u.first_name, u.last_name, r.role_name 
        FROM user_config u 
        JOIN role_config r ON u.role_id = r.id 
        WHERE u.emp_code = :emp_code AND u.status = 'Active'
    """)
    result = await db_engine.execute(query, {"emp_code": emp_code})
    user = result.mappings().first()

    if not user:
        raise HTTPException(status_code=404, detail=[{"msg": "Employee not found or role not assigned"}])

    role_name = user["role_name"].lower()
    actions = ["Take Product", "Return Product", "Return Damaged Product"]
    
    # ✅ If role contains "admin", allow "Admin Mode"
    if "admin" in role_name:
        actions.append("Admin Mode")

    return JSONResponse(content={
        "emp_code": emp_code,
        "name": f"{user['first_name']} {user['last_name']}",
        "role": role_name,
        "actions": actions
    }, status_code=200)
