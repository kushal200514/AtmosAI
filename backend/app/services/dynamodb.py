
import boto3

from app.config import settings


_dynamodb = None


def get_dynamodb():
    """Return a reusable DynamoDB resource."""
    global _dynamodb

    if not settings.use_dynamodb:
        return None

    if _dynamodb is None:
        _dynamodb = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
        )

    return _dynamodb


def get_telemetry_table():
    """Return the telemetry table."""
    dynamodb = get_dynamodb()

    if dynamodb is None:
        return None

    return dynamodb.Table(settings.dynamodb_telemetry_table)

def get_recent_telemetry(node_id: str, limit: int = 500):
    """Retrieve the most recent telemetry records for a node."""
    table = get_telemetry_table()

    if table is None:
        return []

    response = table.query(
        KeyConditionExpression="node_id = :node",
        ExpressionAttributeValues={
            ":node": node_id,
        },
        ScanIndexForward=False,
        Limit=limit,
    )

    return response.get("Items", [])
