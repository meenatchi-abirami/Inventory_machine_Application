from fastapi import APIRouter
from src.inventory_config.inventory import (
    create_inventory, get_inventory, get_all_inventory, update_inventory, delete_inventory
)

router = APIRouter(prefix="/inventory-config")

router.add_api_route("/create-inventory", create_inventory, methods=["POST"])
router.add_api_route("/get-inventory/{inventory_id}", get_inventory, methods=["GET"])
router.add_api_route("/get-all-inventory", get_all_inventory, methods=["GET"])
router.add_api_route("/update-inventory/{inventory_id}", update_inventory, methods=["PUT"])
router.add_api_route("/delete-inventory/{inventory_id}", delete_inventory, methods=["DELETE"])
