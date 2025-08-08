"""
test_simple_gear.py - Script de prueba para generar un engranaje simple
Ejecuta este script en Fusion 360 para probar la biblioteca
"""

import adsk.core
import adsk.fusion
import traceback
import sys
import os

# Agregar la carpeta actual al path para poder importar fusion_lib
current_dir = os.path.dirname(os.path.realpath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Importar nuestra biblioteca
from fusion_lib import SimpleGear, FusionWrapper

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Crear una instancia del generador de engranajes
        gear_generator = SimpleGear()
        
        # Mensaje de inicio
        ui.messageBox('Generando engranaje de prueba...')
        
        # Crear un engranaje simple
        # Parámetros: 20 dientes, módulo 2mm, espesor 10mm, agujero 8mm
        gear = gear_generator.crear_engranaje_spur(
            num_dientes=20,
            modulo_mm=2.0,
            espesor_mm=10.0,
            agujero_central_mm=8.0,
            nombre="EngranajeTest"
        )
        
        # Mensaje de éxito
        ui.messageBox('✅ ¡Engranaje creado exitosamente!\n\n' +
                     'Especificaciones:\n' +
                     '• 20 dientes\n' +
                     '• Módulo: 2mm\n' +
                     '• Espesor: 10mm\n' +
                     '• Agujero central: 8mm')
        
    except:
        if ui:
            ui.messageBox('Error:\n{}'.format(traceback.format_exc()))

def stop(context):
    """Limpieza al detener el script"""
    pass