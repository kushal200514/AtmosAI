from fastapi import APIRouter


router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"]
)


@router.get("")
def get_profiles():

    return {
        "profiles": [
            {
                "id": "general",
                "name": "General Public"
            },
            {
                "id": "parent",
                "name": "Parent"
            },
            {
                "id": "delivery_rider",
                "name": "Delivery Rider"
            },
            {
                "id": "asthma_patient",
                "name": "Respiratory Sensitive"
            },
            {
                "id": "runner",
                "name": "Runner"
            }
        ]
    }