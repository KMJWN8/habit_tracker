from http import HTTPStatus

class AppError(Exception):
    def __init__(
            self, 
            message: str = "Internal Server Error", 
            status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(AppError):
    """401"""
    def __init__(self, message: str = "Authentification failed"):
        super().__init__(message=message, status_code=HTTPStatus.UNAUTHORIZED.value)


class ForbiddenError(AppError):
    """Ошибка доступа — прав недостаточно (403)."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, status_code=HTTPStatus.FORBIDDEN.value)


class NotFoundError(AppError):
    """404"""
    def __init__(self, entity: str = "Entity"):
        super().__init__(message=f"{entity} not found", status_code=HTTPStatus.NOT_FOUND.value)


class DatabaseError(AppError):
    """500"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value)


class BusinessError(AppError):
    """400"""
    def __init__(self, message: str = "Business logic error"):
        super().__init__(message=message, status_code=HTTPStatus.BAD_REQUEST.value)


class ConflictError(BusinessError):
    """409"""    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message=message, status_code=HTTPStatus.CONFLICT.value)