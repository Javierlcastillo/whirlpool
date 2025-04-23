from rest_framework import viewsets, filters, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Technician
from .api_serializers import TechnicianAuthSerializer, TechnicianSerializer

@swagger_auto_schema(
    method='post',
    request_body=TechnicianAuthSerializer,
    responses={
        200: openapi.Response(
            description='Autenticación exitosa',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'authenticated': openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description='Indica si la autenticación fue exitosa'
                    ),
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Mensaje descriptivo del resultado'
                    ),
                    'technician': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description='Datos del técnico (solo si authenticated=true)',
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'numero_empleado': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'region': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'nombre': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            ),
                            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                            'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                        }
                    )
                }
            )
        ),
        401: openapi.Response(
            description='Credenciales inválidas',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'authenticated': openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description='Siempre false en caso de error'
                    ),
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Mensaje descriptivo del error'
                    )
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def technician_login(request):
    """
    Endpoint para la autenticación de técnicos.
    
    Recibe:
    - numero_empleado: Número de empleado del técnico
    - password: Contraseña
    
    Devuelve:
    - authenticated: true/false
    - message: Mensaje de estado
    - technician: Datos del técnico (solo si la autenticación es exitosa)
    """
    serializer = TechnicianAuthSerializer(data=request.data)
    
    if serializer.is_valid():
        technician = serializer.validated_data['technician']
        technician_data = TechnicianSerializer(technician).data
        
        return Response({
            'authenticated': True,
            'message': 'Autenticación exitosa',
            'technician': technician_data
        })
    
    return Response({
        'authenticated': False,
        'message': 'Credenciales inválidas'
    }, status=status.HTTP_401_UNAUTHORIZED) 