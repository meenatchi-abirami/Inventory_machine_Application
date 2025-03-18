from fastapi import APIRouter
from src.load_item.load_item import load_items, filter_products

router = APIRouter(prefix="/load_items")

router.add_api_route("/load_items", load_items, methods=["POST"])
router.add_api_route("/filter_products", filter_products, methods=["GET"])

