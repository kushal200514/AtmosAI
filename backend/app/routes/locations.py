from fastapi import APIRouter


router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


@router.get("")
def get_locations():

    return {
        "locations": [
            {
                "id": "bengaluru",
                "name": "Bengaluru"
            },
            {
                "id": "delhi",
                "name": "Delhi"
            },
            {
                "id": "hyderabad",
                "name": "Hyderabad"
            }
        ]
    }