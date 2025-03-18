from fastapi import APIRouter
from src.email_config.email_config import create_email_config,get_all_email_configs, get_email_config, delete_email_config, update_email_config

router = APIRouter(prefix="/email-handler")

router.add_api_route("/get_all_email_configs", get_all_email_configs, methods=["GET"])
router.add_api_route("/get_email_config", get_email_config, methods=["GET"])
router.add_api_route("/create_email_config", create_email_config, methods=["POST"])
router.add_api_route("/update_email_config", update_email_config, methods=["PUT"])
router.add_api_route("/delete_email_config", delete_email_config, methods=["DELETE"])
