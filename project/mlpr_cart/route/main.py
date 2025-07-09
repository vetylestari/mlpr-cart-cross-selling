from fastapi import APIRouter, HTTPException
from project.mlpr_cart.services.generate_recommendation import run_batch

router = APIRouter()

@router.post("/recommendation/batch-update")
async def generate_recommendations():
    try:
        print("🔥 Calling run_batch...")
        run_batch()
        return {"status": "success", "message": "Recommendations updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation batch failed: {str(e)}")