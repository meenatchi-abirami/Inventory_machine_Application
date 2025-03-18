from fastapi import APIRouter
from src.inventory.inventory_list import inventory_list, category_list


router = APIRouter(prefix = "/inventory-handler")

router.add_api_route("/inventory-lists", inventory_list, methods=["GET"])
router.add_api_route("/category-lists", category_list, methods=["GET"])

from src.inventory.user_config import (
    create_user, 
    get_all_users, 
    get_user, 
    update_user, 
    delete_user
)
# Adding user_config routes
router.add_api_route("/user-config/create", create_user, methods=["POST"])
router.add_api_route("/user-config", get_all_users, methods=["GET"])
router.add_api_route("/user-config/{user_id}", get_user, methods=["GET"])
router.add_api_route("/user-config/{user_id}", update_user, methods=["PUT"])
router.add_api_route("/user-config/{user_id}", delete_user, methods=["DELETE"])