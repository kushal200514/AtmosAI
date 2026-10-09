from fastapi import APIRouter


router = APIRouter(
    prefix="/accuracy",
    tags=["Accuracy"]
)


@router.get("")
def get_accuracy():

    return {
        "status": "not_available",
        "message": "Accuracy will be available after model backtesting."
    }