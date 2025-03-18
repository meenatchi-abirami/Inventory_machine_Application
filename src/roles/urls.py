from fastapi import APIRouter
from src.roles.role_config import role_list, get_role, create_role, update_role, delete_role

router = APIRouter(prefix="/role-handler")

router.add_api_route("/role-lists", role_list, methods=["GET"])
router.add_api_route("/get-role", get_role, methods=["GET"])
router.add_api_route("/create-role", create_role, methods=["POST"])
router.add_api_route("/update-role", update_role, methods=["PUT"])
router.add_api_route("/delete-role", delete_role, methods=["DELETE"])

