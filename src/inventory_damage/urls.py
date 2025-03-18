from fastapi import APIRouter
from src.inventory_damage.inventory_damage import get_all_damaged_listings,create_damaged_listing, get_damaged_listing, update_damaged_listing_status, delete_damaged_listing

router = APIRouter(prefix="/inventory-damaged-handler")

router.add_api_route("/damaged-listings", get_all_damaged_listings, methods=["GET"])
# router.add_api_route("/damaged-listings", get_damaged_listing, methods=["GET"])
router.add_api_route("/create-damaged-listing", create_damaged_listing, methods=["POST"])
router.add_api_route("/update-damaged-listing", update_damaged_listing_status, methods=["PUT"])
router.add_api_route("/delete-damaged-listing", delete_damaged_listing, methods=["DELETE"])
