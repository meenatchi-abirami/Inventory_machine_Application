from fastapi import APIRouter
from src.return_damaged_products.return_damages_product import get_damaged_return_categories, return_damaged_product
router = APIRouter(prefix="/return_damage_product")

router.add_api_route("/get_damaged_return_categories", get_damaged_return_categories, methods=["GET"])

# router.add_api_route("/return_damaged_product", return_damaged_product, methods=["POST"])


