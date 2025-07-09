import os
import sys
import uvicorn
import importlib
from fastapi import APIRouter, FastAPI, status
from pydantic import BaseModel

# Tambahkan project ke sys.path
sys.path.append(os.path.dirname(__file__))

dir_path = f"{os.path.dirname(os.path.realpath(__file__))}/project"
project_list = os.listdir(dir_path)

class HealthCheck(BaseModel):
    status: str = "OK"

app = FastAPI(
    title="Renos DataAPI",
    description="",
    summary="",
    version="2.0.0",
    terms_of_service="",
    contact={
        "name": "Asyraf Nur Adianto",
        "email": "asyraf.adianto@renos.id",
    },
)

router = APIRouter(
    prefix="/dataapi/mlpr-cart",
    tags=["mlpr-cart"],
    responses={404: {"description": "Not found"}},
)

@app.get("/health", tags=["System"], response_model=HealthCheck)
def healthcheck():
    return HealthCheck(status="OK")

def project_import(project_name):
    path = "project"
    module = project_name
    full_module_path = f"{path}.{module}.main"
    print(f"Importing: {full_module_path}")
    imported_module = importlib.import_module(full_module_path)
    app.include_router(imported_module.router)


# Skip non-python or invalid folders
for pl in project_list:
    if pl.endswith(".py") and pl not in ['__init__.py']:
        module_name = pl.replace(".py", "")
    elif os.path.isdir(os.path.join(dir_path, pl)):
        module_name = pl
    else:
        continue

    try:
        project_import(module_name)
        print(f"SUCCESS ON IMPORTING '{module_name}'")
    except Exception as e:
        print(f"FAILED TO IMPORT '{module_name}'")
        print(f"Error: {str(e)}")

app.include_router(router)

def run():
    uvicorn.run("handler_fastapi:app", host="0.0.0.0", port=8000)