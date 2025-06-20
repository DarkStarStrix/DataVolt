import torch
import logging
import os

logger = logging.getLogger(__name__)

def load_torch_model(model_class, model_path, device="cpu"):
    """
    Loads a PyTorch model from a .pt or .pth file, avoiding safetensors errors.
    Returns an instance of model_class with loaded weights.
    """
    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        raise FileNotFoundError(f"Model file not found: {model_path}")

    try:
        # Try loading as a regular torch model
        state = torch.load(model_path, map_location=device)
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        model = model_class()
        model.load_state_dict(state)
        model.eval()
        return model
    except Exception as e:
        # Handle safetensors error or other loading issues
        logger.error(f"Error loading model: {e}")
        raise RuntimeError(f"Failed to load model: {e}")

def predict(model, input_tensor):
    """
    Runs inference on the given model and input tensor.
    """
    try:
        with torch.no_grad():
            output = model(input_tensor)
        return output
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise RuntimeError(f"Prediction failed: {e}")
