from fastapi import APIRouter
from src.api.auth import get_employee_actions
# from src.api.product_selection import take_product

router = APIRouter(prefix="/auth")

router.add_api_route("/get-actions", get_employee_actions, methods=["POST"])
# router.add_api_route("/take-product", take_product, methods=["GET"])


