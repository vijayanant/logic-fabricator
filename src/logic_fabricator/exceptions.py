class FabricatorError(Exception):
    """Base exception for all Fabricator-related errors."""
    pass

class UnsupportedIRFeatureError(FabricatorError):
    """Raised when an IR feature is not supported by the current fabric.py runtime types."""
    pass
