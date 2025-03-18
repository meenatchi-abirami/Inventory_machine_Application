from fastapi import APIRouter
from src.inventory_unreturn.inventory_unreturn import get_all_inventory_unreturned_listings, create_inventory_unreturned_listing, update_inventory_unreturned_listing, delete_inventory_unreturned_listing

router = APIRouter(prefix="/inventory-unreturned-items")

router.add_api_route("/inventory_unreturned_lists", get_all_inventory_unreturned_listings, methods=["GET"])
router.add_api_route("/create-inventory_unreturned_lists", create_inventory_unreturned_listing, methods=["POST"])
router.add_api_route("/update-inventory_unreturned_lists", update_inventory_unreturned_listing, methods=["PUT"])
router.add_api_route("/delete-inventory_unreturned_lists", delete_inventory_unreturned_listing, methods=["DELETE"])

