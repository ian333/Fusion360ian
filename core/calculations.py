# -*- coding: utf-8 -*-
"""
calculations.py - Cálculos matemáticos puros para Harmonic Drive
NO depende de Fusion 360 - puede ser testeado independientemente
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class HarmonicDriveParams:
    """Parámetros completos del Harmonic Drive"""
    # Entrada básica
    teeth_cs: int           # Dientes del Circular Spline
    module: float          # Módulo en mm
    pressure_angle: float  # Ángulo de presión en grados
    
    # Calculados automáticamente
    teeth_fs: int = None   # Dientes del Flex Spline
    ratio: float = None    # Relación de reducción
    eccentricity: float = None  # Excentricidad del WG
    
    # Geometría del diente
    addendum_factor: float = 0.8   # Factor de addendum (reducido para HD)
    dedendum_factor: float = 1.0   # Factor de dedendum
    
    # Material y manufactura
    material: str = 'steel'
    wall_thickness_factor: float = 1.5  # Factor para espesor de pared FS
    print_tolerance: float = 0.2  # Tolerancia para impresión 3D en mm
    
    def __post_init__(self):
        """Calcula parámetros derivados"""
        if self.teeth_fs is None:
            self.teeth_fs = self.teeth_cs - 2
        if self.ratio is None:
            self.ratio = self.teeth_cs / 2
        if self.eccentricity is None:
            self.eccentricity = (2 * self.module) / math.pi


class HarmonicDriveCalculator:
    """Calculadora para todos los parámetros del Harmonic Drive"""
    
    def __init__(self, params: HarmonicDriveParams):
        self.params = params
        self._validate_basic_params()
        
    def _validate_basic_params(self):
        """Valida parámetros básicos"""
        errors = []
        
        # Validar número de dientes
        if self.params.teeth_cs % 2 != 0:
            errors.append("teeth_cs debe ser par")
        
        if self.params.teeth_cs < 60:
            errors.append("teeth_cs mínimo es 60")
            
        if self.params.teeth_cs > 320:
            errors.append("teeth_cs máximo es 320")
        
        # Validar módulo (con tolerancia para errores de redondeo)
        if self.params.module < 0.299:  # Tolerancia de 0.001
            errors.append("Módulo mínimo es 0.3mm")
            
        if self.params.module > 5.001:  # Tolerancia de 0.001
            errors.append("Módulo máximo es 5.0mm")
        
        # Validar ángulo de presión
        if self.params.pressure_angle < 20:
            errors.append("Ángulo de presión mínimo es 20°")
            
        if self.params.pressure_angle > 30:
            errors.append("Ángulo de presión máximo es 30°")
        
        if errors:
            raise ValueError(f"Errores de validación: {', '.join(errors)}")
    
    def get_circular_spline_geometry(self) -> Dict:
        """Calcula geometría del Circular Spline (engranaje interno)"""
        
        # Diámetros básicos
        pitch_diameter = self.params.module * self.params.teeth_cs
        pitch_radius = pitch_diameter / 2
        
        # Para engranaje INTERNO, los dientes van hacia adentro
        addendum = self.params.addendum_factor * self.params.module
        dedendum = self.params.dedendum_factor * self.params.module
        
        # En engranajes internos:
        # - El diámetro de addendum es MENOR que el primitivo
        # - El diámetro de dedendum es MAYOR que el primitivo
        addendum_diameter = pitch_diameter - 2 * addendum
        dedendum_diameter = pitch_diameter + 2 * dedendum
        
        # Radio base para perfil involuta
        pressure_angle_rad = math.radians(self.params.pressure_angle)
        base_diameter = pitch_diameter * math.cos(pressure_angle_rad)
        
        # Anillo exterior (carcasa)
        outer_diameter = dedendum_diameter + 2 * 10 * self.params.module  # 10x módulo de pared
        
        return {
            'type': 'internal',
            'teeth': self.params.teeth_cs,
            'module': self.params.module,
            'pitch_diameter': pitch_diameter,
            'pitch_radius': pitch_radius,
            'addendum_diameter': addendum_diameter,
            'dedendum_diameter': dedendum_diameter,
            'base_diameter': base_diameter,
            'outer_diameter': outer_diameter,
            'tooth_height': addendum + dedendum,
            'pressure_angle': self.params.pressure_angle
        }
    
    def get_flex_spline_geometry(self) -> Dict:
        """Calcula geometría del Flex Spline (engranaje externo flexible)"""
        
        # Diámetros básicos
        pitch_diameter = self.params.module * self.params.teeth_fs
        pitch_radius = pitch_diameter / 2
        
        # Para engranaje EXTERNO normal
        addendum = self.params.addendum_factor * self.params.module
        dedendum = self.params.dedendum_factor * self.params.module
        
        # En engranajes externos:
        # - El diámetro de addendum es MAYOR que el primitivo
        # - El diámetro de dedendum es MENOR que el primitivo
        addendum_diameter = pitch_diameter + 2 * addendum
        dedendum_diameter = pitch_diameter - 2 * dedendum
        
        # Radio base para perfil involuta
        pressure_angle_rad = math.radians(self.params.pressure_angle)
        base_diameter = pitch_diameter * math.cos(pressure_angle_rad)
        
        # Espesor de pared de la copa
        wall_thickness = self.params.wall_thickness_factor * self.params.module
        
        # Diámetro interior de la copa
        inner_diameter = dedendum_diameter - 2 * wall_thickness
        
        # Longitud de la copa
        cup_length = 0.8 * pitch_diameter  # 80% del diámetro primitivo
        
        return {
            'type': 'external',
            'teeth': self.params.teeth_fs,
            'module': self.params.module,
            'pitch_diameter': pitch_diameter,
            'pitch_radius': pitch_radius,
            'addendum_diameter': addendum_diameter,
            'dedendum_diameter': dedendum_diameter,
            'base_diameter': base_diameter,
            'inner_diameter': inner_diameter,
            'wall_thickness': wall_thickness,
            'cup_length': cup_length,
            'tooth_height': addendum + dedendum,
            'pressure_angle': self.params.pressure_angle
        }
    
    def get_wave_generator_geometry(self) -> Dict:
        """Calcula geometría del Wave Generator (leva elíptica)"""
        
        fs_geometry = self.get_flex_spline_geometry()
        
        # Radio interior del Flex Spline
        fs_inner_radius = fs_geometry['inner_diameter'] / 2
        
        # Holgura con el FS
        clearance = 0.1 * self.params.module  # 10% del módulo
        
        # Dimensiones de la elipse
        # El WG debe tocar el FS en el eje mayor y tener holgura en el menor
        major_radius = fs_inner_radius - clearance
        minor_radius = major_radius - 2 * self.params.eccentricity
        
        # Agujero central para eje motor
        shaft_diameter = max(5.0, 5 * self.params.module)  # Mínimo 5mm
        
        # Altura del WG (típicamente 50% de la longitud de la copa)
        height = 0.5 * fs_geometry['cup_length']
        
        return {
            'type': 'elliptical_cam',
            'major_radius': major_radius,
            'minor_radius': minor_radius,
            'major_diameter': 2 * major_radius,
            'minor_diameter': 2 * minor_radius,
            'eccentricity': self.params.eccentricity,
            'shaft_diameter': shaft_diameter,
            'height': height,
            'clearance': clearance
        }
    
    def calculate_strain(self) -> Dict:
        """Calcula la deformación del Flex Spline"""
        
        fs_geometry = self.get_flex_spline_geometry()
        
        # Radio medio del FS
        mean_radius = fs_geometry['pitch_radius']
        
        # Deformación radial máxima
        max_deformation = 2 * self.params.eccentricity
        
        # Strain (deformación relativa)
        strain = max_deformation / mean_radius
        
        # Límites de strain según material
        strain_limits = {
            'steel': 0.003,      # 0.3%
            'aluminum': 0.004,   # 0.4%
            'plastic': 0.02,     # 2%
            'tpu': 0.05         # 5%
        }
        
        max_strain = strain_limits.get(self.params.material, 0.003)
        is_safe = strain <= max_strain
        
        return {
            'strain': strain,
            'strain_percent': strain * 100,
            'max_strain': max_strain,
            'max_strain_percent': max_strain * 100,
            'is_safe': is_safe,
            'safety_factor': max_strain / strain if strain > 0 else float('inf')
        }
    
    def calculate_contact_ratio(self) -> float:
        """Calcula la relación de contacto (debe ser > 1.2)"""
        
        cs_geo = self.get_circular_spline_geometry()
        
        # Simplificación: usar fórmula aproximada
        # Para cálculo exacto necesitaríamos el perfil completo del diente
        pressure_angle_rad = math.radians(self.params.pressure_angle)
        
        # Longitud de la línea de acción
        addendum = self.params.addendum_factor * self.params.module
        action_length = 2 * addendum / math.sin(pressure_angle_rad)
        
        # Paso base
        base_pitch = math.pi * self.params.module * math.cos(pressure_angle_rad)
        
        # Relación de contacto
        contact_ratio = action_length / base_pitch
        
        return contact_ratio
    
    def calculate_backlash(self) -> Dict:
        """Calcula el juego (backlash) recomendado"""
        
        # Juego tangencial (en el círculo primitivo)
        tangential_min = 0.04 * self.params.module
        tangential_max = 0.06 * self.params.module
        tangential_nominal = 0.05 * self.params.module
        
        # Juego radial
        pressure_angle_rad = math.radians(self.params.pressure_angle)
        radial_nominal = tangential_nominal / (2 * math.tan(pressure_angle_rad))
        
        return {
            'tangential_min': tangential_min,
            'tangential_max': tangential_max,
            'tangential_nominal': tangential_nominal,
            'radial_nominal': radial_nominal
        }
    
    def get_involute_profile_points(self, num_points: int = 50, 
                                   is_internal: bool = False) -> List[Tuple[float, float]]:
        """
        Genera puntos del perfil involuta para un diente
        
        Args:
            num_points: Número de puntos a generar
            is_internal: True para engranaje interno (CS), False para externo (FS)
        
        Returns:
            Lista de tuplas (x, y) con los puntos del perfil
        """
        
        if is_internal:
            geometry = self.get_circular_spline_geometry()
        else:
            geometry = self.get_flex_spline_geometry()
        
        base_radius = geometry['base_diameter'] / 2
        pitch_radius = geometry['pitch_radius']
        
        # Calcular rango del parámetro t
        # t_min es donde empieza la involuta (en el círculo base)
        t_min = 0
        
        # t_max es donde la involuta alcanza el círculo de addendum
        if is_internal:
            # Para engranaje interno, el addendum está hacia adentro
            addendum_radius = geometry['addendum_diameter'] / 2
            if addendum_radius > base_radius:
                # No hay involuta si el addendum es mayor que el base
                t_max = 0
            else:
                t_max = math.sqrt((base_radius / addendum_radius) ** 2 - 1)
        else:
            # Para engranaje externo normal
            addendum_radius = geometry['addendum_diameter'] / 2
            if addendum_radius > base_radius:
                t_max = math.sqrt((addendum_radius / base_radius) ** 2 - 1)
            else:
                t_max = 0
        
        points = []
        
        for i in range(num_points):
            t = t_min + (t_max - t_min) * i / (num_points - 1)
            
            # Ecuaciones paramétricas de la involuta
            x = base_radius * (math.cos(t) + t * math.sin(t))
            y = base_radius * (math.sin(t) - t * math.cos(t))
            
            points.append((x, y))
        
        return points
    
    def get_tooth_profile(self, is_internal: bool = False) -> Dict:
        """
        Genera el perfil completo de un diente
        
        Returns:
            Diccionario con los puntos del perfil y metadata
        """
        
        if is_internal:
            geometry = self.get_circular_spline_geometry()
        else:
            geometry = self.get_flex_spline_geometry()
        
        # Puntos de la involuta (un lado del diente)
        involute_points = self.get_involute_profile_points(30, is_internal)
        
        # Espesor del diente en el círculo primitivo
        tooth_thickness = (math.pi * self.params.module) / 2
        
        # Ángulo que ocupa medio diente en el círculo primitivo
        pitch_radius = geometry['pitch_radius']
        half_tooth_angle = tooth_thickness / (2 * pitch_radius)
        
        # Espejo de los puntos para el otro lado del diente
        mirrored_points = []
        for x, y in reversed(involute_points):
            # Rotar los puntos para crear el otro lado
            angle = 2 * half_tooth_angle
            x_rot = x * math.cos(angle) - y * math.sin(angle)
            y_rot = x * math.sin(angle) + y * math.cos(angle)
            mirrored_points.append((x_rot, y_rot))
        
        # Perfil completo del diente
        full_profile = involute_points + mirrored_points
        
        return {
            'points': full_profile,
            'tooth_thickness': tooth_thickness,
            'is_internal': is_internal,
            'num_teeth': geometry['teeth'],
            'module': self.params.module
        }
    
    def get_full_summary(self) -> Dict:
        """Obtiene un resumen completo de todos los cálculos"""
        
        cs_geo = self.get_circular_spline_geometry()
        fs_geo = self.get_flex_spline_geometry()
        wg_geo = self.get_wave_generator_geometry()
        strain = self.calculate_strain()
        contact_ratio = self.calculate_contact_ratio()
        backlash = self.calculate_backlash()
        
        return {
            'parameters': {
                'teeth_cs': self.params.teeth_cs,
                'teeth_fs': self.params.teeth_fs,
                'module': self.params.module,
                'reduction_ratio': self.params.ratio,
                'eccentricity': self.params.eccentricity,
                'pressure_angle': self.params.pressure_angle
            },
            'circular_spline': cs_geo,
            'flex_spline': fs_geo,
            'wave_generator': wg_geo,
            'analysis': {
                'strain': strain,
                'contact_ratio': contact_ratio,
                'backlash': backlash,
                'is_valid': strain['is_safe'] and contact_ratio > 1.2
            }
        }


def quick_validation(teeth_cs: int, module: float, material: str = 'steel') -> Tuple[bool, List[str]]:
    """
    Validación rápida de parámetros del Harmonic Drive
    
    Args:
        teeth_cs: Número de dientes del Circular Spline
        module: Módulo en mm
        material: Material del Flex Spline
    
    Returns:
        (es_valido, lista_de_errores)
    """
    
    errors = []
    warnings = []
    
    try:
        # Crear parámetros y calculadora
        params = HarmonicDriveParams(
            teeth_cs=teeth_cs,
            module=module,
            pressure_angle=30,  # Estándar para HD
            material=material
        )
        
        calc = HarmonicDriveCalculator(params)
        
        # Verificar strain
        strain_data = calc.calculate_strain()
        if not strain_data['is_safe']:
            errors.append(f"Deformación excesiva: {strain_data['strain_percent']:.2f}% > {strain_data['max_strain_percent']:.2f}%")
        
        # Verificar relación de contacto
        contact_ratio = calc.calculate_contact_ratio()
        if contact_ratio < 1.2:
            errors.append(f"Relación de contacto baja: {contact_ratio:.2f} < 1.2")
        
        # Advertencias
        if teeth_cs < 100:
            warnings.append("Pocos dientes, considere aumentar para mejor suavidad")
        
        if module < 0.5:
            warnings.append("Módulo muy pequeño, difícil de fabricar")
        
    except ValueError as e:
        errors.append(str(e))
    
    # Combinar errores y advertencias
    all_messages = errors + [f"ADVERTENCIA: {w}" for w in warnings]
    
    return len(errors) == 0, all_messages


# Funciones de utilidad adicionales
def suggest_parameters(reduction_ratio: float, 
                       max_diameter: float = 100,
                       material: str = 'steel') -> Optional[HarmonicDriveParams]:
    """
    Sugiere parámetros óptimos dado una relación de reducción deseada
    
    Args:
        reduction_ratio: Relación de reducción deseada (30:1 a 320:1)
        max_diameter: Diámetro máximo permitido en mm
        material: Material del Flex Spline
    
    Returns:
        HarmonicDriveParams optimizados o None si no es posible
    """
    
    # Calcular número de dientes necesario
    teeth_cs = int(2 * reduction_ratio)
    
    # Asegurar que es par
    if teeth_cs % 2 != 0:
        teeth_cs += 1
    
    # Validar rango
    if teeth_cs < 60 or teeth_cs > 320:
        return None
    
    # Calcular módulo máximo permitido
    module_max = max_diameter / teeth_cs
    
    # Seleccionar módulo estándar más cercano
    standard_modules = [0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
    module = None
    
    for m in reversed(standard_modules):
        if m <= module_max:
            # Verificar que funcione con este módulo
            params = HarmonicDriveParams(
                teeth_cs=teeth_cs,
                module=m,
                pressure_angle=30,
                material=material
            )
            
            try:
                calc = HarmonicDriveCalculator(params)
                strain_data = calc.calculate_strain()
                
                if strain_data['is_safe']:
                    module = m
                    break
            except:
                continue
    
    if module is None:
        return None
    
    return HarmonicDriveParams(
        teeth_cs=teeth_cs,
        module=module,
        pressure_angle=30,
        material=material
    )