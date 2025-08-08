"""
fusion_utils.py - Wrapper simplificado para la API de Fusion 360
Hace que trabajar con Fusion sea más fácil y directo
"""

import adsk.core
import adsk.fusion
import math

class FusionWrapper:
    """
    Clase wrapper que simplifica las operaciones comunes de Fusion 360
    """
    
    def __init__(self):
        """Inicializa el wrapper con referencias a la app y el diseño actual"""
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface
        self.design = self.app.activeProduct
        self.root = self.design.rootComponent
        self.units_mgr = self.design.unitsManager
        
    def crear_componente(self, nombre="NuevoComponente"):
        """
        Crea un nuevo componente en el diseño
        
        Args:
            nombre: Nombre del componente
            
        Returns:
            El componente creado
        """
        occs = self.root.occurrences
        transform = adsk.core.Matrix3D.create()
        new_occ = occs.addNewComponent(transform)
        new_comp = new_occ.component
        new_comp.name = nombre
        return new_comp
    
    def crear_sketch(self, componente=None, plano="XY"):
        """
        Crea un sketch en el plano especificado
        
        Args:
            componente: Componente donde crear el sketch (None = root)
            plano: "XY", "XZ", o "YZ"
            
        Returns:
            El sketch creado
        """
        if componente is None:
            componente = self.root
            
        # Seleccionar el plano
        if plano == "XY":
            plane = componente.xYConstructionPlane
        elif plano == "XZ":
            plane = componente.xZConstructionPlane
        elif plano == "YZ":
            plane = componente.yZConstructionPlane
        else:
            plane = componente.xYConstructionPlane
            
        sketch = componente.sketches.add(plane)
        return sketch
    
    def dibujar_circulo(self, sketch, centro_x=0, centro_y=0, radio=1.0):
        """
        Dibuja un círculo en el sketch
        
        Args:
            sketch: El sketch donde dibujar
            centro_x: Coordenada X del centro (cm)
            centro_y: Coordenada Y del centro (cm)
            radio: Radio del círculo (cm)
            
        Returns:
            El círculo creado
        """
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(centro_x, centro_y, 0)
        circle = circles.addByCenterRadius(center, radio)
        return circle
    
    def dibujar_rectangulo(self, sketch, x1, y1, x2, y2):
        """
        Dibuja un rectángulo en el sketch
        
        Args:
            sketch: El sketch donde dibujar
            x1, y1: Esquina inferior izquierda (cm)
            x2, y2: Esquina superior derecha (cm)
            
        Returns:
            Las líneas del rectángulo
        """
        lines = sketch.sketchCurves.sketchLines
        
        # Crear los 4 puntos
        p1 = adsk.core.Point3D.create(x1, y1, 0)
        p2 = adsk.core.Point3D.create(x2, y1, 0)
        p3 = adsk.core.Point3D.create(x2, y2, 0)
        p4 = adsk.core.Point3D.create(x1, y2, 0)
        
        # Dibujar las 4 líneas
        l1 = lines.addByTwoPoints(p1, p2)
        l2 = lines.addByTwoPoints(p2, p3)
        l3 = lines.addByTwoPoints(p3, p4)
        l4 = lines.addByTwoPoints(p4, p1)
        
        return [l1, l2, l3, l4]
    
    def extruir(self, perfil, distancia_cm, componente=None, operacion="nuevo"):
        """
        Extruye un perfil
        
        Args:
            perfil: El perfil a extruir
            distancia_cm: Distancia de extrusión en cm
            componente: Componente donde extruir (None = root)
            operacion: "nuevo", "unir", "cortar", "intersectar"
            
        Returns:
            La extrusión creada
        """
        if componente is None:
            componente = self.root
            
        extrudes = componente.features.extrudeFeatures
        
        # Mapear operaciones
        ops = {
            "nuevo": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            "unir": adsk.fusion.FeatureOperations.JoinFeatureOperation,
            "cortar": adsk.fusion.FeatureOperations.CutFeatureOperation,
            "intersectar": adsk.fusion.FeatureOperations.IntersectFeatureOperation
        }
        
        operation_type = ops.get(operacion, ops["nuevo"])
        
        extrude_input = extrudes.createInput(perfil, operation_type)
        distance = adsk.core.ValueInput.createByReal(distancia_cm)
        extrude_input.setDistanceExtent(False, distance)
        
        extrude = extrudes.add(extrude_input)
        return extrude
    
    def patron_circular(self, objeto, eje, cantidad):
        """
        Crea un patrón circular de un objeto
        
        Args:
            objeto: El objeto a repetir
            eje: El eje de rotación
            cantidad: Número de copias (incluyendo el original)
            
        Returns:
            El patrón creado
        """
        # Esta función es más compleja, la simplificaremos más adelante
        pass
    
    def mm_a_cm(self, mm):
        """Convierte milímetros a centímetros (unidad interna de Fusion)"""
        return mm / 10.0
    
    def cm_a_mm(self, cm):
        """Convierte centímetros a milímetros"""
        return cm * 10.0
    
    def crear_punto(self, x, y, z=0):
        """
        Crea un punto 3D
        
        Args:
            x, y, z: Coordenadas en cm
            
        Returns:
            Point3D object
        """
        return adsk.core.Point3D.create(x, y, z)
    
    def dibujar_linea(self, sketch, x1, y1, x2, y2):
        """
        Dibuja una línea en el sketch
        
        Args:
            sketch: El sketch donde dibujar
            x1, y1: Punto inicial (cm)
            x2, y2: Punto final (cm)
            
        Returns:
            La línea creada
        """
        lines = sketch.sketchCurves.sketchLines
        p1 = self.crear_punto(x1, y1)
        p2 = self.crear_punto(x2, y2)
        line = lines.addByTwoPoints(p1, p2)
        return line
    
    def dibujar_arco(self, sketch, centro_x, centro_y, radio, angulo_inicio, angulo_fin):
        """
        Dibuja un arco en el sketch
        
        Args:
            sketch: El sketch donde dibujar
            centro_x, centro_y: Centro del arco (cm)
            radio: Radio del arco (cm)
            angulo_inicio: Ángulo inicial en grados
            angulo_fin: Ángulo final en grados
            
        Returns:
            El arco creado
        """
        arcs = sketch.sketchCurves.sketchArcs
        center = self.crear_punto(centro_x, centro_y)
        
        # Calcular puntos de inicio y fin
        ang_ini_rad = math.radians(angulo_inicio)
        ang_fin_rad = math.radians(angulo_fin)
        
        start_x = centro_x + radio * math.cos(ang_ini_rad)
        start_y = centro_y + radio * math.sin(ang_ini_rad)
        end_x = centro_x + radio * math.cos(ang_fin_rad)
        end_y = centro_y + radio * math.sin(ang_fin_rad)
        
        start_point = self.crear_punto(start_x, start_y)
        end_point = self.crear_punto(end_x, end_y)
        
        arc = arcs.addByCenterStartEnd(center, start_point, end_point)
        return arc
    
    def aplicar_color(self, body, nombre_color, r=128, g=128, b=128):
        """
        Aplica un color/apariencia a un cuerpo
        
        Args:
            body: El cuerpo al que aplicar color
            nombre_color: Nombre del color/material
            r, g, b: Valores RGB (0-255)
        """
        appearances = self.design.appearances
        
        # Buscar si ya existe
        appearance = None
        for i in range(appearances.count):
            if appearances.item(i).name == nombre_color:
                appearance = appearances.item(i)
                break
        
        # Crear si no existe
        if not appearance:
            appearance = appearances.add()
            appearance.name = nombre_color
            
            color_prop = appearance.appearanceProperties.itemByName("Color")
            if color_prop:
                color_value = adsk.core.Color.create(r, g, b, 255)
                color_prop.value = color_value
        
        body.appearance = appearance
    
    def mensaje(self, texto):
        """Muestra un mensaje al usuario"""
        self.ui.messageBox(texto)