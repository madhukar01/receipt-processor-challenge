"""Update rules configuration endpoint."""
import json

import yaml
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import PlainTextResponse

from rest_server.api.config.models import RulesConfig

router = APIRouter()


@router.put("/rules", response_class=PlainTextResponse)
async def update_rules(
    request: Request,
    file: UploadFile,
) -> str:
    """Update rules configuration from YAML file.

    Args:
        request: FastAPI request object
        file: YAML file containing rules configuration

    Returns:
        Updated rules configuration as YAML
    """
    if not file.filename or not file.filename.endswith((".yml", ".yaml")):
        raise HTTPException(
            status_code=400,
            detail="Only YAML files are allowed (.yml, .yaml)",
        )

    try:
        # Read and parse YAML content
        content = await file.read()
        rules_dict = yaml.safe_load(content)

        # Validate against model
        RulesConfig(**rules_dict)

        # Store as JSON in Redis
        redis = request.state.context.redis
        redis.set_key("rules_config", json.dumps(rules_dict))

        # Convert back to YAML for response
        yaml_content = yaml.dump(
            rules_dict,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            indent=2,
        )
        return yaml_content

    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid YAML format: {str(e)}",
        ) from e
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error converting to JSON for storage: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
