import threading
import logging
import json
from _services.config import MODEL_JSON_PATH

logger = logging.getLogger(__name__)


class ModelLoader:
    _model = None
    _lock = threading.Lock()

    @classmethod
    def load_model(cls, force: bool = False):
        """Load and cache the trained model weights."""
        if cls._model is None or force:
            with cls._lock:
                if MODEL_JSON_PATH.exists():
                    try:
                        with open(MODEL_JSON_PATH, 'r') as f:
                            cls._model = json.load(f)
                        logger.info("Successfully loaded ML model weights from disk.")
                    except Exception as e:
                        logger.error(f"Error loading model weights: {e}")
                        cls._model = None
                else:
                    logger.warning("ML model weights file does not exist on disk.")
                    cls._model = None
        return cls._model

    @classmethod
    def clear_cache(cls):
        """Clear cached model from memory."""
        with cls._lock:
            cls._model = None
