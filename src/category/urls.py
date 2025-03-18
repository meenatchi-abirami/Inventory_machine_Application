from fastapi import APIRouter
from src.category.category_config import (
    create_category,
    get_all_categories,
    get_category,
    update_category,
    delete_category
)

router = APIRouter(prefix="/category-handler")

router.add_api_route("/create-category", create_category, methods=["POST"])
router.add_api_route("/get-categories", get_all_categories, methods=["GET"])
router.add_api_route("/get-category/{category_id}", get_category, methods=["GET"])
router.add_api_route("/update-category/{category_id}", update_category, methods=["PUT"])
router.add_api_route("/delete-category/{category_id}", delete_category, methods=["DELETE"])
