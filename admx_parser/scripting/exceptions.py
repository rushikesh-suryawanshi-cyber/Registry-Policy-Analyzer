class ScriptGenerationError(Exception):
    """Base class for exceptions in script generation."""
    pass

class TemplateNotFoundError(ScriptGenerationError):
    """Raised when a template file cannot be found."""
    pass

class PolicyValidationError(ScriptGenerationError):
    """Raised when policy data is invalid or missing required fields for script generation."""
    pass
