from fastapi import APIRouter
from src.location.location_config import (
    get_locations,
    get_location,
    create_location,
    update_location,
    delete_location
)

router = APIRouter(prefix="/location-handler")

router.add_api_route("/get-locations", get_locations, methods=["GET"])
router.add_api_route("/get-location/{location_id}", get_location, methods=["GET"])
router.add_api_route("/create-location", create_location, methods=["POST"])
router.add_api_route("/update-location/{location_id}", update_location, methods=["PUT"])
router.add_api_route("/delete-location/{location_id}", delete_location, methods=["DELETE"])
