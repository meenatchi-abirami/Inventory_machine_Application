from fastapi import APIRouter
from src.inventory_list.inventory_listing import (
    get_all_inventory_listings,
    get_inventory_listing,
    create_inventory_listing,
    update_inventory_listing,
    delete_inventory_listing,
)

router = APIRouter(prefix="/inventory-listings")

router.add_api_route("/listings", get_all_inventory_listings, methods=["GET"])
router.add_api_route("/get-listing/{listing_id}", get_inventory_listing, methods=["GET"])
router.add_api_route("/create-listing", create_inventory_listing, methods=["POST"])
router.add_api_route("/update-listing/{listing_id}", update_inventory_listing, methods=["PUT"])
router.add_api_route("/delete-listing/{listing_id}", delete_inventory_listing, methods=["DELETE"])
