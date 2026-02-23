from fastapi import APIRouter

router = APIRouter(prefix="/intelligence", tags=["Strategy Intelligence"])

@router.get("/strategies")
def list_strategies():
    return []  # registry adapter

@router.get("/strategy/{strategy_id}/metrics")
def strategy_metrics(strategy_id: str):
    return []  # snapshot reader

@router.get("/strategy/{strategy_id}/symbols")
def symbol_metrics(strategy_id: str):
    return []
