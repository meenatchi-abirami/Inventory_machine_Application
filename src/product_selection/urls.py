
from fastapi import APIRouter
from src.product_selection.product_selection import get_all_categories, get_products_by_category, get_products_by_categories,get_unique_products, take_product,additional_take_product

router = APIRouter(prefix="/product-selection")

router.add_api_route("/get_all_categories", get_all_categories, methods=["GET"])

router.add_api_route("/get_products_by_category", get_products_by_category, methods=["GET"])

router.add_api_route("/get_products_by_categories", get_products_by_categories, methods=["GET"])

router.add_api_route("/get_unique_products", get_unique_products, methods=["GET"])

router.add_api_route("/additional_take_product", additional_take_product , methods=["POST"])

router.add_api_route("/take_product", take_product, methods=["POST"])

