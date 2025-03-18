from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from pydantic import BaseModel
from typing import Optional, List
from src.database_config import get_db  # Ensure this exists

router = APIRouter()

# ✅ Pydantic Models
class EmailConfigRequest(BaseModel):
    email_username: str  # Mapped to `email_id`
    email_password: str  # Mapped to `password`
    email_server: str  # Mapped to `mx_record`
    email_port: int  # Mapped to `port_number`
    smpt_format: str
    status: str
    created_by: int


class UpdateEmailConfigRequest(BaseModel):
    email_username: Optional[str] = None  # email_id in DB
    email_password: Optional[str] = None  # password in DB
    email_server: Optional[str] = None  # mx_record in DB
    email_port: Optional[int] = None  # port_number in DB
    smpt_format: Optional[str] = None
    status: Optional[str] = None
    last_updated_by: Optional[int] = None


class EmailConfigResponse(BaseModel):
    id: int
    email_username: str
    email_password: str
    email_server: str
    email_port: int
    smpt_format: str
    status: str
    created_by: int
    last_updated_by: Optional[int]


# ✅ Create Email Config (POST)
@router.post("/email-config", response_model=dict)
async def create_email_config(request: EmailConfigRequest, db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            INSERT INTO email_config (email_id, password, mx_record, port_number, smpt_format, status, create_by, last_updated_by, create_date, last_updated_date)
            VALUES (:email_id, :password, :mx_record, :port_number, :smpt_format, :status, :create_by, :create_by, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """)

        params = {
            "email_id": request.email_username,
            "password": request.email_password,
            "mx_record": request.email_server,
            "port_number": request.email_port,
            "smpt_format": request.smpt_format,
            "status": request.status,
            "create_by": request.created_by,
        }

        await db.execute(query, params)
        await db.commit()
        return {"message": "Email configuration created successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# ✅ Get All Email Configs (GET)
@router.get("/email-config", response_model=List[EmailConfigResponse])
async def get_all_email_configs(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT id, email_id, password, mx_record, port_number, smpt_format, status, create_by, last_updated_by, create_date, last_updated_date
            FROM email_config
        """)
        result = await db.execute(query)
        rows = result.fetchall()

        return [
            {
                "id": row.id,
                "email_username": row.email_id,
                "email_password": row.password,
                "email_server": row.mx_record,
                "email_port": row.port_number,
                "smpt_format": row.smpt_format,
                "status": row.status,
                "created_by": row.create_by,
                "last_updated_by": row.last_updated_by,
            }
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# ✅ Get Single Email Config by ID (GET)
@router.get("/email-config/{config_id}", response_model=EmailConfigResponse)
async def get_email_config(config_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT id, email_id, password, mx_record, port_number, smpt_format, status, create_by, last_updated_by, create_date, last_updated_date
            FROM email_config WHERE id = :config_id
        """)
        result = await db.execute(query, {"config_id": config_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Email configuration not found")

        return {
            "id": row.id,
            "email_username": row.email_id,
            "email_password": row.password,
            "email_server": row.mx_record,
            "email_port": row.port_number,
            "smpt_format": row.smpt_format,
            "status": row.status,
            "created_by": row.create_by,
            "last_updated_by": row.last_updated_by,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# ✅ Update Email Configuration (PUT)
@router.put("/email-config/{config_id}", response_model=dict)
async def update_email_config(config_id: int, request: UpdateEmailConfigRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Check if email config exists
        check_query = text("SELECT id FROM email_config WHERE id = :config_id")
        result = await db.execute(check_query, {"config_id": config_id})
        email_entry = result.fetchone()

        if not email_entry:
            raise HTTPException(status_code=404, detail="Email configuration not found")

        # Map request fields to database columns
        update_fields = {
            "email_id": request.email_username,
            "password": request.email_password,
            "mx_record": request.email_server,
            "port_number": request.email_port,
            "smpt_format": request.smpt_format,
            "status": request.status,
            "last_updated_by": request.last_updated_by,
        }

        # Remove `None` values
        update_fields = {key: value for key, value in update_fields.items() if value is not None}

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_fields["config_id"] = config_id
        set_clause = ", ".join([f"{key} = :{key}" for key in update_fields.keys() if key != "config_id"])

        update_query = text(f"""
            UPDATE email_config
            SET {set_clause}, last_updated_date = CURRENT_TIMESTAMP()
            WHERE id = :config_id
        """)

        await db.execute(update_query, update_fields)
        await db.commit()

        return {"message": "Email configuration updated successfully"}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# ✅ Delete Email Configuration (DELETE)
@router.delete("/email-config/{config_id}", response_model=dict)
async def delete_email_config(config_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Check if email config exists
        check_query = text("SELECT id FROM email_config WHERE id = :config_id")
        result = await db.execute(check_query, {"config_id": config_id})
        email_entry = result.fetchone()

        if not email_entry:
            raise HTTPException(status_code=404, detail="Email configuration not found")

        # Delete the email config
        delete_query = text("DELETE FROM email_config WHERE id = :config_id")
        await db.execute(delete_query, {"config_id": config_id})
        await db.commit()

        return {"message": "Email configuration deleted successfully"}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
