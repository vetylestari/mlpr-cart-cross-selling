from fastapi import FastAPI
from project.mlpr_cart.route import main as recommendation_route

app = FastAPI()

# Register router
app.include_router(recommendation_route.router)