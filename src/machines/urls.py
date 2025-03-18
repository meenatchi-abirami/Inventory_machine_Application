from fastapi import APIRouter
from src.machines.machine_listings import (
    machine_list, get_machine, create_machine, update_machine, delete_machine
)

router = APIRouter(prefix="/machine-handler")

router.add_api_route("/get-machines", machine_list, methods=["GET"])
router.add_api_route("/get-machine/{machine_id}", get_machine, methods=["GET"])
router.add_api_route("/create-machine", create_machine, methods=["POST"])
router.add_api_route("/update-machine/{machine_id}", update_machine, methods=["PUT"])
router.add_api_route("/delete-machine/{machine_id}", delete_machine, methods=["DELETE"])
