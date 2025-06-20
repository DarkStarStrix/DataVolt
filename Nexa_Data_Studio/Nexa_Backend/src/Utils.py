import logging
from pydantic import ValidationError

def setup_logging(level=logging.INFO):
    """
    Sets up logging with a standard format and the provided logging level.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=level, format=log_format)
    logging.info("Logging is configured.")

def validate_request(schema, request_data):
    """
    Validates request_data against the provided Pydantic schema.

    Parameters:
        schema: A Pydantic BaseModel subclass.
        request_data: Dictionary containing the request data.

    Returns:
        An instance of the schema with validated data.

    Raises:
        ValueError: If validation fails.
    """
    try:
        validated = schema(**request_data)
        return validated
    except ValidationError as e:
        logging.error(f"Request validation failed: {e}")
        raise ValueError(f"Invalid request data: {e}")
