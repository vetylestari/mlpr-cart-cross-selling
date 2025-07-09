from project.mlpr_cart.route.main import (
    router as mlpr_cart_router,
)
from fastapi import APIRouter

# Initialize the FastAPI application
router = APIRouter(
    prefix="/datapi/mlpr-cart",
    tags=["mlpr-cart"],
    responses={404: {"description": "Not found"}},
)

router.include_router(mlpr_cart_router)