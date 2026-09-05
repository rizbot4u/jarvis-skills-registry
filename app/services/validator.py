import json
import jsonschema
from jsonschema.exceptions import ValidationError
from fastapi import HTTPException, status

def validate_skill_payload(raw_config: str, payload: dict) -> dict:
    try:
        config = json.loads(raw_config) if isinstance(raw_config, str) else raw_config
        schema = config.get("parameters_schema", config)
        jsonschema.validate(instance=payload, schema=schema)
        return payload
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid skill configuration JSON stored in active version."
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Schema validation failed: {e.message}"
        )
