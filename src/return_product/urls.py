from fastapi import APIRouter
from src.return_product.return_product import  get_return_categories, return_product
router = APIRouter(prefix="/return_product")

router.add_api_route("/get_return_categories", get_return_categories, methods=["GET"])
# router.add_api_route("/get-role", get_role, methods=["GET"])
router.add_api_route("/create-role", return_product, methods=["POST"])


