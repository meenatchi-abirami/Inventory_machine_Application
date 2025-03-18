from fastapi import APIRouter
from src.users.user_config import create_user, get_users, get_user, update_user, delete_user

router = APIRouter(prefix="/user-handler")

router.add_api_route("/create-user", create_user, methods=["POST"])
router.add_api_route("/get-users", get_users, methods=["GET"])
router.add_api_route("/get-user/{user_id}", get_user, methods=["GET"])
router.add_api_route("/update-user/{user_id}", update_user, methods=["PUT"])
router.add_api_route("/delete-user/{user_id}", delete_user, methods=["DELETE"])
