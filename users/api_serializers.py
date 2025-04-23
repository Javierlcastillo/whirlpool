from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Technician

class TechnicianAuthSerializer(serializers.Serializer):
    """
    Serializer para la autenticación de técnicos.
    Recibe numero_empleado y password, y valida la autenticación.
    
    Campos:
    - numero_empleado: Número de empleado del técnico
    - password: Contraseña del técnico
    """
    numero_empleado = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, data):
        numero_empleado = data.get('numero_empleado')
        password = data.get('password')
        
        if numero_empleado and password:
            # Autenticar usando el número de empleado como username
            user = authenticate(username=numero_empleado, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Usuario desactivado.')
                
                # Verificar que el usuario es un técnico
                try:
                    technician = Technician.objects.get(user=user)
                    if not technician.is_active:
                        raise serializers.ValidationError('Este técnico está desactivado.')
                    
                    # Añadir los datos del técnico a los datos validados
                    data['technician'] = technician
                    return data
                except Technician.DoesNotExist:
                    raise serializers.ValidationError('Este usuario no es un técnico registrado.')
            else:
                raise serializers.ValidationError('Credenciales incorrectas.')
        else:
            raise serializers.ValidationError('Debe proporcionar número de empleado y contraseña.') 