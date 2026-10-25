"""Application-level exceptions."""


class HRMError(Exception):
    """Base exception for HRM automation."""


class PolicyViolationError(HRMError):
    pass


class ApprovalNotFoundError(HRMError):
    pass


class ToolNotFoundError(HRMError):
    pass


class ModelProviderError(HRMError):
    pass
