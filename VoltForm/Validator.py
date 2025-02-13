from jsonschema import validate, ValidationError

schema = {
    "type": "object",
    "properties": {
        "infrastructure": {
            "type": "object",
            "properties": {
                "compute_cluster": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "region": {"type": "string"},
                        "instance_type": {"type": "string"},
                        "node_count": {"type": "integer", "minimum": 1}
                    },
                    "required": ["type", "region", "instance_type", "node_count"]
                }
            },
            "required": ["compute_cluster"]
        }
    },
    "required": ["infrastructure"]
}

def validate_voltform(config):
    try:
        validate(instance=config, schema=schema)
        return True
    except ValidationError as e:
        raise ValueError(f"Invalid configuration: {e.message}")
