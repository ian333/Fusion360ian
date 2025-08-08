# -*- coding: utf-8 -*-
"""
involute_profile.py - Generador de perfil involuta REAL para engranajes
Basado en las ecuaciones matemáticas correctas
"""

import math
from typing import List, Tuple, Dict
import sys
import os

# Importar los cálculos base
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.calculations import HarmonicDriveParams, HarmonicDriveCalculator


class InvoluteGearProfile:
    """Genera el perfil involuta correcto para engranajes"""
    
    def __init__(self, module: float, teeth: int, pressure_angle: float = 20.0):
        """
        Inicializa el generador de perfil involuta
        
        Args:
            module: Módulo del engranaje (mm)
            teeth: Número de dientes
            pressure_angle: Ángulo de presión (grados)
        """
        self.module = module
        self.teeth = teeth
        self.pressure_angle_deg = pressure_angle
        self.pressure_angle_rad = math.radians(pressure_angle)
        
        # Calcular dimensiones básicas
        self.pitch_diameter = module * teeth
        self.pitch_radius = self.pitch_diameter / 2
        self.base_radius = self.pitch_radius * math.cos(self.pressure_angle_rad)
        
        # Addendum y dedendum estándar
        self.addendum = 1.0 * module
        self.dedendum = 1.25 * module
        
        # Para Harmonic Drive, reducir addendum
        self.addendum_hd = 0.8 * module
        
        # Radios de los círculos
        self.outside_radius = self.pitch_radius + self.addendum
        self.root_radius = self.pitch_radius - self.dedendum
        
        # Espesor del diente en el círculo primitivo
        self.tooth_thickness = (math.pi * module) / 2
        
    def involute_function(self, angle: float) -> float:
        """
        Función involuta: inv(α) = tan(α) - α
        """
        return math.tan(angle) - angle
    
    def involute_point(self, t: float) -> Tuple[float, float]:
        """
        Calcula un punto en la curva involuta
        
        Args:
            t: Parámetro de la curva (radianes)
        
        Returns:
            (x, y) coordenadas del punto
        """
        x = self.base_radius * (math.cos(t) + t * math.sin(t))
        y = self.base_radius * (math.sin(t) - t * math.cos(t))
        return (x, y)
    
    def get_involute_points(self, start_radius: float = None, 
                           end_radius: float = None,
                           num_points: int = 30) -> List[Tuple[float, float]]:
        """
        Genera puntos de la curva involuta entre dos radios
        
        Args:
            start_radius: Radio inicial (None = círculo base)
            end_radius: Radio final (None = círculo exterior)
            num_points: Número de puntos a generar
        
        Returns:
            Lista de puntos (x, y)
        """
        
        if start_radius is None:
            start_radius = self.base_radius
        
        if end_radius is None:
            end_radius = self.outside_radius
        
        # Verificar que los radios sean válidos
        if start_radius < self.base_radius:
            start_radius = self.base_radius
        
        if end_radius < self.base_radius:
            return []  # No hay involuta bajo el círculo base
        
        # Calcular parámetros t para los radios
        if start_radius <= self.base_radius:
            t_start = 0
        else:
            t_start = math.sqrt((start_radius / self.base_radius) ** 2 - 1)
        
        t_end = math.sqrt((end_radius / self.base_radius) ** 2 - 1)
        
        # Generar puntos
        points = []
        for i in range(num_points):
            t = t_start + (t_end - t_start) * i / (num_points - 1)
            point = self.involute_point(t)
            points.append(point)
        
        return points
    
    def get_single_tooth_profile(self, num_points: int = 30) -> List[Tuple[float, float]]:
        """
        Genera el perfil completo de un solo diente
        
        Returns:
            Lista de puntos que forman el contorno del diente
        """
        
        # Obtener puntos de la involuta (lado derecho del diente)
        involute_right = self.get_involute_points(
            start_radius=self.root_radius,
            end_radius=self.outside_radius,
            num_points=num_points // 2
        )
        
        # Calcular el ángulo del espesor del diente en el pitch circle
        tooth_angle = self.tooth_thickness / self.pitch_radius
        
        # Crear el lado izquierdo del diente (espejo y rotación)
        involute_left = []
        for x, y in reversed(involute_right):
            # Espejo respecto al eje X
            x_mirror = x
            y_mirror = -y
            
            # Rotar por el ángulo del diente
            x_rot = x_mirror * math.cos(tooth_angle) - y_mirror * math.sin(tooth_angle)
            y_rot = x_mirror * math.sin(tooth_angle) + y_mirror * math.cos(tooth_angle)
            
            involute_left.append((x_rot, y_rot))
        
        # Agregar arco en la punta del diente
        tip_points = self._get_tip_arc(involute_right[-1], involute_left[0], 5)
        
        # Agregar arco en la raíz del diente
        root_points = self._get_root_fillet(involute_left[-1], involute_right[0], 5)
        
        # Combinar todos los puntos
        profile = involute_right + tip_points + involute_left + root_points
        
        return profile
    
    def _get_tip_arc(self, point1: Tuple[float, float], 
                     point2: Tuple[float, float],
                     num_points: int = 5) -> List[Tuple[float, float]]:
        """
        Genera un arco circular en la punta del diente
        """
        x1, y1 = point1
        x2, y2 = point2
        
        # Calcular el centro del arco (en el círculo exterior)
        r1 = math.sqrt(x1**2 + y1**2)
        r2 = math.sqrt(x2**2 + y2**2)
        r_avg = (r1 + r2) / 2
        
        # Ángulos de los puntos
        angle1 = math.atan2(y1, x1)
        angle2 = math.atan2(y2, x2)
        
        # Generar puntos del arco
        points = []
        for i in range(1, num_points):
            t = i / num_points
            angle = angle1 + (angle2 - angle1) * t
            x = r_avg * math.cos(angle)
            y = r_avg * math.sin(angle)
            points.append((x, y))
        
        return points
    
    def _get_root_fillet(self, point1: Tuple[float, float],
                        point2: Tuple[float, float],
                        num_points: int = 5) -> List[Tuple[float, float]]:
        """
        Genera un filete (radio) en la raíz del diente
        """
        # Radio del filete = 0.38 * módulo (estándar)
        fillet_radius = 0.38 * self.module
        
        # Por simplicidad, usar un arco directo entre los puntos
        return self._get_tip_arc(point1, point2, num_points)
    
    def get_gear_profile(self, is_internal: bool = False) -> List[List[Tuple[float, float]]]:
        """
        Genera el perfil completo del engranaje (todos los dientes)
        
        Args:
            is_internal: True para engranaje interno
        
        Returns:
            Lista de perfiles de dientes
        """
        
        # Obtener perfil de un diente
        single_tooth = self.get_single_tooth_profile()
        
        # Ángulo entre dientes
        tooth_pitch = 2 * math.pi / self.teeth
        
        # Generar todos los dientes
        all_teeth = []
        
        for i in range(self.teeth):
            angle = i * tooth_pitch
            
            # Rotar el diente a su posición
            tooth_points = []
            for x, y in single_tooth:
                # Para engranaje interno, invertir el diente
                if is_internal:
                    # Voltear el diente hacia adentro
                    r = math.sqrt(x**2 + y**2)
                    r_inverted = 2 * self.pitch_radius - r
                    angle_point = math.atan2(y, x)
                    x = r_inverted * math.cos(angle_point)
                    y = r_inverted * math.sin(angle_point)
                
                # Rotar a la posición correcta
                x_rot = x * math.cos(angle) - y * math.sin(angle)
                y_rot = x * math.sin(angle) + y * math.cos(angle)
                
                tooth_points.append((x_rot, y_rot))
            
            all_teeth.append(tooth_points)
        
        return all_teeth
    
    def validate_profile(self) -> Dict:
        """
        Valida que el perfil sea correcto
        
        Returns:
            Diccionario con resultados de validación
        """
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar número mínimo de dientes para evitar socavado
        min_teeth = 2 / (math.sin(self.pressure_angle_rad) ** 2)
        if self.teeth < min_teeth:
            results['errors'].append(
                f"Número de dientes ({self.teeth}) menor al mínimo para evitar socavado ({min_teeth:.0f})"
            )
            results['valid'] = False
        
        # Verificar que el círculo base sea menor que el de dedendum
        if self.base_radius > self.root_radius:
            results['warnings'].append(
                "Radio base mayor que radio de raíz - puede haber interferencia"
            )
        
        # Verificar relación de contacto
        contact_ratio = self._calculate_contact_ratio()
        if contact_ratio < 1.2:
            results['warnings'].append(
                f"Relación de contacto baja ({contact_ratio:.2f} < 1.2)"
            )
        
        results['contact_ratio'] = contact_ratio
        results['min_teeth_no_undercut'] = min_teeth
        
        return results
    
    def _calculate_contact_ratio(self) -> float:
        """
        Calcula la relación de contacto aproximada
        """
        # Longitud de acción
        action_length = (
            math.sqrt(self.outside_radius**2 - self.base_radius**2) +
            math.sqrt(self.pitch_radius**2 - self.base_radius**2)
        )
        
        # Paso base
        base_pitch = math.pi * self.module * math.cos(self.pressure_angle_rad)
        
        # Relación de contacto
        return action_length / base_pitch


class HarmonicDriveInvoluteProfile:
    """Generador especializado para perfiles de Harmonic Drive"""
    
    def __init__(self, params: HarmonicDriveParams):
        """
        Inicializa con parámetros de Harmonic Drive
        """
        self.params = params
        self.calc = HarmonicDriveCalculator(params)
        
        # Crear generadores para CS y FS
        self.cs_profile = InvoluteGearProfile(
            module=params.module,
            teeth=params.teeth_cs,
            pressure_angle=params.pressure_angle
        )
        
        self.fs_profile = InvoluteGearProfile(
            module=params.module,
            teeth=params.teeth_fs,
            pressure_angle=params.pressure_angle
        )
        
        # Ajustar addendum para HD
        self.cs_profile.addendum = params.addendum_factor * params.module
        self.fs_profile.addendum = params.addendum_factor * params.module
    
    def get_cs_profile(self) -> List[List[Tuple[float, float]]]:
        """Obtiene el perfil del Circular Spline (interno)"""
        return self.cs_profile.get_gear_profile(is_internal=True)
    
    def get_fs_profile(self) -> List[List[Tuple[float, float]]]:
        """Obtiene el perfil del Flex Spline (externo)"""
        return self.fs_profile.get_gear_profile(is_internal=False)
    
    def validate_meshing(self) -> Dict:
        """
        Valida que los engranajes engranen correctamente
        """
        
        cs_validation = self.cs_profile.validate_profile()
        fs_validation = self.fs_profile.validate_profile()
        
        results = {
            'cs_valid': cs_validation['valid'],
            'fs_valid': fs_validation['valid'],
            'mesh_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Agregar errores de cada perfil
        results['errors'].extend([f"CS: {e}" for e in cs_validation['errors']])
        results['errors'].extend([f"FS: {e}" for e in fs_validation['errors']])
        results['warnings'].extend([f"CS: {w}" for w in cs_validation['warnings']])
        results['warnings'].extend([f"FS: {w}" for w in fs_validation['warnings']])
        
        # Verificar compatibilidad de engrane
        if self.params.teeth_cs - self.params.teeth_fs != 2:
            results['errors'].append("Diferencia de dientes debe ser 2")
            results['mesh_valid'] = False
        
        # Verificar módulos iguales
        if abs(self.cs_profile.module - self.fs_profile.module) > 0.001:
            results['errors'].append("Los módulos deben ser iguales")
            results['mesh_valid'] = False
        
        # Verificar ángulos de presión iguales
        if abs(self.cs_profile.pressure_angle_deg - self.fs_profile.pressure_angle_deg) > 0.001:
            results['errors'].append("Los ángulos de presión deben ser iguales")
            results['mesh_valid'] = False
        
        results['overall_valid'] = (
            results['cs_valid'] and 
            results['fs_valid'] and 
            results['mesh_valid']
        )
        
        return results


# Funciones de utilidad para testing
def test_involute_profile():
    """Test rápido del generador de perfil involuta"""
    
    print("Testing Involute Profile Generator")
    print("="*50)
    
    # Crear un engranaje de prueba
    profile = InvoluteGearProfile(module=1.0, teeth=20, pressure_angle=20)
    
    print(f"Módulo: {profile.module} mm")
    print(f"Dientes: {profile.teeth}")
    print(f"Diámetro primitivo: {profile.pitch_diameter:.2f} mm")
    print(f"Radio base: {profile.base_radius:.2f} mm")
    print(f"Radio exterior: {profile.outside_radius:.2f} mm")
    
    # Generar puntos de involuta
    points = profile.get_involute_points(num_points=10)
    print(f"\nPrimeros 5 puntos de la involuta:")
    for i, (x, y) in enumerate(points[:5]):
        print(f"  {i}: ({x:.3f}, {y:.3f})")
    
    # Validar perfil
    validation = profile.validate_profile()
    print(f"\nValidación:")
    print(f"  Válido: {validation['valid']}")
    print(f"  Relación de contacto: {validation['contact_ratio']:.2f}")
    print(f"  Dientes mín sin socavado: {validation['min_teeth_no_undercut']:.0f}")
    
    if validation['errors']:
        print("  Errores:")
        for error in validation['errors']:
            print(f"    - {error}")
    
    if validation['warnings']:
        print("  Advertencias:")
        for warning in validation['warnings']:
            print(f"    - {warning}")
    
    return validation['valid']


if __name__ == "__main__":
    # Ejecutar test cuando se llame directamente
    test_involute_profile()