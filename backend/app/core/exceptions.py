from fastapi import Request, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class DatasetNotFoundError(AppException):
    def __init__(self, dataset_name: str):
        super().__init__(f"Dataset '{dataset_name}' not found.", status.HTTP_404_NOT_FOUND)

class DatasetValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(f"Dataset validation failed: {message}", status.HTTP_422_UNPROCESSABLE_ENTITY)

class ModelNotFoundError(AppException):
    def __init__(self, model_name: str):
        super().__init__(f"Model '{model_name}' not found. Please train the model first.", status.HTTP_404_NOT_FOUND)

class InsufficientDataError(AppException):
    def __init__(self, message: str):
        super().__init__(f"Insufficient data for operation: {message}", status.HTTP_400_BAD_REQUEST)

class InvalidRequestError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_type": exc.__class__.__name__}
    )
