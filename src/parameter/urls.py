from fastapi import APIRouter
from src.parameter.parameter_config import (
    get_all_parameter_configs,
    get_parameter_config,
    create_parameter_config,
    update_parameter_config,
    delete_parameter_config
)

router = APIRouter(prefix="/parameter-config")

router.add_api_route("/list", get_all_parameter_configs, methods=["GET"])
router.add_api_route("/get/{id}", get_parameter_config, methods=["GET"])
router.add_api_route("/create", create_parameter_config, methods=["POST"])
router.add_api_route("/update/{id}", update_parameter_config, methods=["PUT"])
router.add_api_route("/delete/{id}", delete_parameter_config, methods=["DELETE"])
