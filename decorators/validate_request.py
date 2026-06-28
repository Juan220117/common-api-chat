"""File with format response"""
import json
import functools
from datetime import datetime
from typing import Type, Callable, Any, Dict, Optional
from pydantic import BaseModel, ValidationError,Field
from responses.response import success_response,error_response,format_response
from loguru import logger

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

def validate_request(schema_class: Type[BaseModel], require_body: bool = True):
    """
    Decorator to validate the body of the request with Pydantic.
    
    Args:
        schema_class: Pydantic class that defines the expected scheme
        require_body: If True, the body of the request is required
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(event: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract the body of the application
                body = event.get('body', '{}')
                
                # If the body is a JSON string, parse it
                if isinstance(body, str):
                    try:
                        body = json.loads(body) if body else {}
                    except json.JSONDecodeError:
                        return error_response(
                            'Invalid JSON format',
                            400,
                            {'error': 'El cuerpo de la solicitud no es un JSON válido'}
                        )
                
                # If there is no body and it is required
                if not body and require_body:
                    return error_response('Request body is required', 400)
                
                # Validate with pydantic
                validated_data = schema_class(**body)
                
                # Si hay validación adicional, se puede hacer aquí
                # Ejemplo: check_rate_limit(validated_data.user_id)
                
                # Llamar a la función con los datos validados
                result = func(validated_data)
                
                # Si la función ya devuelve una respuesta formateada, usarla
                if isinstance(result, dict) and 'statusCode' in result:
                    return result
                
                # Si devuelve un modelo Pydantic, formatearlo
                if isinstance(result, BaseModel):
                    return success_response(result)
                
                # Si devuelve datos, formatearlos como éxito
                return success_response(result)
                
            except ValidationError as e:
                # Errores de validación de Pydantic
                details = {}
                for error in e.errors():
                    field = '.'.join(str(loc) for loc in error['loc'])
                    details[field] = error['msg']
                
                return error_response(
                    'Validation error',
                    400,
                    details
                )
                
            except ValueError as e:
                # Errores de negocio
                return error_response(str(e), 400)
                
            except Exception as e:
                # Errores inesperados
                return error_response(
                    'Internal server error',
                    500,
                    {'error': str(e)}
                )
        
        return wrapper
    return decorator
