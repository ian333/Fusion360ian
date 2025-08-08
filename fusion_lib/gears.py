"""
gears.py - Generador simple de engranajes
Empezamos con engranajes spur básicos
"""

import math
from .fusion_utils import FusionWrapper

class SimpleGear:
    """
    Generador de engranajes simple
    """
    
    def __init__(self):
        self.fusion = FusionWrapper()
    
    def crear_engranaje_spur(self, 
                            num_dientes=20,
                            modulo_mm=1.0,
                            espesor_mm=5.0,
                            agujero_central_mm=5.0,
                            nombre="Engranaje"):
        """
        Crea un engranaje recto (spur) simple
        
        Args:
            num_dientes: Número de dientes
            modulo_mm: Módulo del engranaje en mm
            espesor_mm: Espesor del engranaje en mm
            agujero_central_mm: Diámetro del agujero central en mm
            nombre: Nombre del componente
            
        Returns:
            El componente del engranaje creado
        """
        
        # Convertir a cm (unidad interna de Fusion)
        modulo = self.fusion.mm_a_cm(modulo_mm)
        espesor = self.fusion.mm_a_cm(espesor_mm)
        agujero = self.fusion.mm_a_cm(agujero_central_mm)
        
        # Calcular dimensiones básicas
        diametro_primitivo = modulo * num_dientes
        radio_primitivo = diametro_primitivo / 2
        
        # Altura del diente (addendum) y profundidad (dedendum)
        addendum = modulo * 1.0  # Altura estándar
        dedendum = modulo * 1.25  # Profundidad estándar
        
        radio_exterior = radio_primitivo + addendum
        radio_raiz = radio_primitivo - dedendum
        
        # Crear componente
        componente = self.fusion.crear_componente(f"{nombre}_{num_dientes}T")
        
        # Crear sketch
        sketch = self.fusion.crear_sketch(componente, "XY")
        
        # Dibujar el cuerpo base del engranaje (círculo exterior)
        self.fusion.dibujar_circulo(sketch, 0, 0, radio_exterior)
        
        # Dibujar agujero central si se especifica
        if agujero > 0:
            self.fusion.dibujar_circulo(sketch, 0, 0, agujero/2)
        
        # Por ahora, vamos a hacer dientes simplificados (trapezoidales)
        # En el futuro podemos hacer dientes involutivos reales
        self._dibujar_dientes_simples(sketch, num_dientes, radio_primitivo, 
                                     radio_exterior, radio_raiz)
        
        # Extruir el engranaje
        # Buscar el perfil correcto (el que tiene el agujero si existe)
        perfiles = sketch.profiles
        perfil = None
        
        if agujero > 0:
            # Buscar el perfil con agujero (2 loops)
            for i in range(perfiles.count):
                p = perfiles.item(i)
                if p.profileLoops.count == 2:
                    perfil = p
                    break
        else:
            # Usar el primer perfil
            perfil = perfiles.item(0)
        
        if perfil:
            extrusion = self.fusion.extruir(perfil, espesor, componente, "nuevo")
            
            # Aplicar color metálico
            if extrusion.bodies.count > 0:
                self.fusion.aplicar_color(extrusion.bodies.item(0), 
                                        "Metal_Gear", 160, 160, 170)
        
        return componente
    
    def _dibujar_dientes_simples(self, sketch, num_dientes, radio_primitivo, 
                                radio_exterior, radio_raiz):
        """
        Dibuja dientes simplificados (trapezoidales) en el sketch
        
        Esta es una versión simplificada. Los dientes reales deberían
        usar el perfil involuta para un engrane correcto.
        """
        
        angulo_por_diente = 360.0 / num_dientes
        ancho_diente = angulo_por_diente * 0.4  # El diente ocupa 40% del paso
        
        # Dibujar líneas radiales para formar los dientes
        for i in range(num_dientes):
            angulo_base = i * angulo_por_diente
            
            # Ángulos para el diente
            ang1 = angulo_base - ancho_diente/2
            ang2 = angulo_base + ancho_diente/2
            
            # Convertir a radianes
            rad1 = math.radians(ang1)
            rad2 = math.radians(ang2)
            
            # Puntos en el radio primitivo
            x1_prim = radio_primitivo * math.cos(rad1)
            y1_prim = radio_primitivo * math.sin(rad1)
            x2_prim = radio_primitivo * math.cos(rad2)
            y2_prim = radio_primitivo * math.sin(rad2)
            
            # Puntos en el radio exterior (punta del diente)
            x1_ext = radio_exterior * math.cos(rad1)
            y1_ext = radio_exterior * math.sin(rad1)
            x2_ext = radio_exterior * math.cos(rad2)
            y2_ext = radio_exterior * math.sin(rad2)
            
            # Dibujar el diente (dos líneas radiales)
            self.fusion.dibujar_linea(sketch, x1_prim, y1_prim, x1_ext, y1_ext)
            self.fusion.dibujar_linea(sketch, x2_prim, y2_prim, x2_ext, y2_ext)
            
            # Conectar las puntas
            self.fusion.dibujar_linea(sketch, x1_ext, y1_ext, x2_ext, y2_ext)
    
    def crear_engranaje_interno(self,
                              num_dientes=40,
                              modulo_mm=1.0,
                              espesor_mm=5.0,
                              ancho_anillo_mm=5.0,
                              nombre="EngranajeInterno"):
        """
        Crea un engranaje con dientes internos (como el Circular Spline)
        
        Args:
            num_dientes: Número de dientes
            modulo_mm: Módulo del engranaje en mm
            espesor_mm: Espesor del engranaje en mm
            ancho_anillo_mm: Ancho del anillo en mm
            nombre: Nombre del componente
            
        Returns:
            El componente del engranaje interno creado
        """
        
        # Convertir a cm
        modulo = self.fusion.mm_a_cm(modulo_mm)
        espesor = self.fusion.mm_a_cm(espesor_mm)
        ancho_anillo = self.fusion.mm_a_cm(ancho_anillo_mm)
        
        # Calcular dimensiones
        diametro_primitivo = modulo * num_dientes
        radio_primitivo = diametro_primitivo / 2
        
        addendum = modulo * 1.0
        dedendum = modulo * 1.25
        
        radio_interior = radio_primitivo - addendum  # Los dientes apuntan hacia adentro
        radio_exterior = radio_primitivo + ancho_anillo
        
        # Crear componente
        componente = self.fusion.crear_componente(f"{nombre}_{num_dientes}T")
        
        # Crear sketch
        sketch = self.fusion.crear_sketch(componente, "XY")
        
        # Dibujar anillo exterior
        self.fusion.dibujar_circulo(sketch, 0, 0, radio_exterior)
        
        # Dibujar círculo interior (donde están los dientes)
        self.fusion.dibujar_circulo(sketch, 0, 0, radio_interior)
        
        # TODO: Agregar dientes internos
        # Por ahora es solo un anillo simple
        
        # Extruir
        perfil = sketch.profiles.item(0)  # El anillo
        extrusion = self.fusion.extruir(perfil, espesor, componente, "nuevo")
        
        # Aplicar color
        if extrusion.bodies.count > 0:
            self.fusion.aplicar_color(extrusion.bodies.item(0),
                                    "Metal_Dark", 100, 100, 110)
        
        return componente