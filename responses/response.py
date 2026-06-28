"""Responses format"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

def format_response(status_code: int, body: Any) -> Dict[str, Any]:
    """Formato estándar de respuesta para Lambda (API Gateway)"""
    # Si el body es un modelo Pydantic, serializarlo
    if isinstance(body, BaseModel):
        body = body.model_dump(mode='json')
    
    # Convertir datetime a string si existe
    if isinstance(body, dict):
        for key, value in body.items():
            if isinstance(value, datetime):
                body[key] = value.isoformat()
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body, default=str)
    }

def success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Respuesta exitosa"""
    if isinstance(data, BaseModel):
        data = data.model_dump(mode='json')
    return format_response(status_code, {
        'success': True,
        'data': data
    })

def error_response(message: str, status_code: int = 400, details: Optional[Dict] = None) -> Dict[str, Any]:
    """Respuesta de error"""
    return format_response(status_code, {
        'success': False,
        'error': message,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })