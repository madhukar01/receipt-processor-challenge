"""Get rules configuration endpoint."""
import json

import yaml
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/rules", response_class=PlainTextResponse)
async def get_rules(request: Request) -> str:
    """Get current rules configuration.

    Args:
        request: FastAPI request object

    Returns:
        Current rules configuration as YAML
    """
    context = request.state.context
    rules_json = context.redis.get_key("rules_config")

    if not rules_json:
        # Return minimal YAML with empty rules list
        return "rules: []\n"

    try:
        # Parse stored JSON
        rules_dict = json.loads(rules_json)

        # Convert to YAML
        yaml_content = yaml.dump(
            rules_dict,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            indent=2,
        )
        return yaml_content

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stored rules have invalid JSON format: {str(e)}",
        ) from e
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error converting to YAML format: {str(e)}",
        ) from e
