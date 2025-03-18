from fastapi import APIRouter
from src.inventory.urls import router as inventory_handler
from src.roles.urls import router as role_router
from src.users.urls import router as user_router
from src.category.category_config import router as category_router
from src.inventory_config.inventory import router as inventory_config
from src.inventory_list.urls import router as inventory_list
from src.api.urls import router as employee_router
from src.inventory_unreturn.inventory_unreturn import router as unreturn_list
from src.inventory_damage.urls import router as damaged_list
from src.email_config.urls import router as email_list
from src.parameter.urls import router as paramter_config
from src.location.urls import router as location
from src.machines.urls import router as machine_list
from src.product_selection.urls import router as take_product
from src.return_product.urls import router as return_item
from src.return_damaged_products.urls import router as return_damaged_products
from src.load_item.urls import router as Load_items


router = APIRouter()

router.include_router(inventory_handler, tags=["Inventory Handlers"])
router.include_router(role_router, tags=["Roles"])
router.include_router(user_router, tags=["Users"])
router.include_router(category_router, tags=["Categories"])
router.include_router(inventory_config, tags=["Inventory_config"])
router.include_router(inventory_list, tags=["inventory_list"])
router.include_router(unreturn_list, tags=["Unreturn_list"])
router.include_router(damaged_list, tags=["damaged_list"])
router.include_router(email_list, tags=["email_list"])
router.include_router(paramter_config, tags=["parameter-config"])
router.include_router(location, tags=["location"])
router.include_router(machine_list, tags=["machine-list"])
router.include_router(employee_router,tags=["api"])
router.include_router(take_product,tags=["product_selection"])
router.include_router(return_item, tags=["Return product"])
router.include_router(return_damaged_products, tags=["Return damaged products"])
router.include_router(Load_items, tags=["Load_items"])

