"""
Harmonic Drive Generator - CLEAN VERSION
Simple, working version that creates actual harmonic drive components
"""
import adsk.core
import adsk.fusion
import traceback
import math

# Global variables
app = None
ui = None
handlers = []

def run(context):
    """Main entry point"""
    try:
        global app, ui
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Create command
        cmd_defs = ui.commandDefinitions
        
        # Remove old command if exists
        cmd_def = cmd_defs.itemById('HDriveCleanCmd')
        if cmd_def:
            cmd_def.deleteMe()
        
        # Create new command
        cmd_def = cmd_defs.addButtonDefinition(
            'HDriveCleanCmd',
            'Harmonic Drive Generator',
            'Create a simple harmonic drive'
        )
        
        # Add command created handler
        on_command_created = CommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        handlers.append(on_command_created)
        
        # Add button to panel
        panels = ui.allToolbarPanels
        panel = panels.itemById('SolidScriptsAddinsPanel')
        button = panel.controls.addCommand(cmd_def)
        button.isPromoted = True
        
        ui.messageBox('Harmonic Drive Generator (Clean) loaded!')
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    """Clean up"""
    try:
        # Remove button
        panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        button = panel.controls.itemById('HDriveCleanCmd')
        if button:
            button.deleteMe()
        
        # Remove command
        cmd_def = ui.commandDefinitions.itemById('HDriveCleanCmd')
        if cmd_def:
            cmd_def.deleteMe()
    except:
        pass

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            
            # Create simple UI
            inputs.addTextBoxCommandInput('info', '', '<b>Harmonic Drive Parameters</b>', 1, True)
            
            # Module (tooth size)
            module = inputs.addFloatSpinnerCommandInput(
                'module', 'Module (mm)', 'mm', 
                0.5, 2.0, 0.1, 1.0
            )
            
            # Number of teeth
            teeth = inputs.addIntegerSpinnerCommandInput(
                'teeth', 'Teeth (Circular Spline)', 
                60, 160, 2, 100
            )
            
            # Add handlers
            on_execute = CommandExecuteHandler()
            cmd.execute.add(on_execute)
            handlers.append(on_execute)
            
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            inputs = args.command.commandInputs
            
            # Get values (convert from cm to mm)
            module_input = inputs.itemById('module').value
            module = module_input * 10 if module_input < 0.3 else module_input
            teeth_cs = int(inputs.itemById('teeth').value)
            
            # Create the geometry
            create_harmonic_drive(module, teeth_cs)
            
            ui.messageBox(f'Created Harmonic Drive!\nModule: {module}mm\nTeeth: {teeth_cs}')
            
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def create_harmonic_drive(module, teeth_cs):
    """Create the actual harmonic drive geometry"""
    try:
        design = app.activeProduct
        root = design.rootComponent
        
        # Calculate dimensions
        teeth_fs = teeth_cs - 2  # Flex spline has 2 fewer teeth
        pitch_dia_cs = module * teeth_cs  # Pitch diameter
        pitch_dia_fs = module * teeth_fs
        
        # Create Circular Spline (outer ring with internal teeth)
        create_circular_spline(root, pitch_dia_cs / 10, teeth_cs)
        
        # Create Flex Spline (flexible cup with external teeth)
        create_flex_spline(root, pitch_dia_fs / 10, teeth_fs)
        
        # Create Wave Generator (elliptical cam)
        create_wave_generator(root, pitch_dia_fs / 10)
        
    except Exception as e:
        ui.messageBox(f'Error creating geometry: {str(e)}')

def create_circular_spline(root, pitch_radius_cm, num_teeth):
    """Create the circular spline (outer ring)"""
    try:
        # Create component
        occs = root.occurrences
        transform = adsk.core.Matrix3D.create()
        cs_occ = occs.addNewComponent(transform)
        cs_comp = cs_occ.component
        cs_comp.name = f"CircularSpline_{num_teeth}T"
        
        # Create sketch
        sketches = cs_comp.sketches
        xy_plane = cs_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Draw two circles for ring
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        
        outer_radius = pitch_radius_cm + 0.5  # Add 5mm wall
        inner_radius = pitch_radius_cm
        
        outer_circle = circles.addByCenterRadius(center, outer_radius)
        inner_circle = circles.addByCenterRadius(center, inner_radius)
        
        # Add simple teeth representation (just lines for now)
        if num_teeth <= 80:  # Limit for performance
            add_teeth_marks(sketch, inner_radius, num_teeth, True)
        
        # Extrude
        profile = sketch.profiles.item(0)  # Ring profile
        extrudes = cs_comp.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        distance = adsk.core.ValueInput.createByReal(3.0)  # 30mm height
        extrude_input.setDistanceExtent(False, distance)
        extrude = extrudes.add(extrude_input)
        
        # Color it gray
        if extrude.bodies.count > 0:
            body = extrude.bodies.item(0)
            apply_color(body, "Gray", 150, 150, 150)
        
    except Exception as e:
        ui.messageBox(f'Error in circular spline: {str(e)}')

def create_flex_spline(root, pitch_radius_cm, num_teeth):
    """Create the flex spline (flexible cup)"""
    try:
        # Create component with offset
        occs = root.occurrences
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, 0.2)  # 2mm offset
        fs_occ = occs.addNewComponent(transform)
        fs_comp = fs_occ.component
        fs_comp.name = f"FlexSpline_{num_teeth}T"
        
        # Create sketch for cup walls
        sketches = fs_comp.sketches
        xy_plane = fs_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Draw thin wall ring
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        
        outer_radius = pitch_radius_cm
        inner_radius = pitch_radius_cm - 0.1  # 1mm wall thickness
        
        outer_circle = circles.addByCenterRadius(center, outer_radius)
        inner_circle = circles.addByCenterRadius(center, inner_radius)
        
        # Add teeth marks
        if num_teeth <= 80:
            add_teeth_marks(sketch, outer_radius, num_teeth, False)
        
        # Extrude cup walls
        profile = sketch.profiles.item(0)
        extrudes = fs_comp.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        distance = adsk.core.ValueInput.createByReal(4.0)  # 40mm cup height
        extrude_input.setDistanceExtent(False, distance)
        cup_extrude = extrudes.add(extrude_input)
        
        # Create bottom of cup
        bottom_sketch = sketches.add(xy_plane)
        bottom_circle = bottom_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            center, inner_radius
        )
        
        bottom_profile = bottom_sketch.profiles.item(0)
        bottom_extrude_input = extrudes.createInput(
            bottom_profile,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        bottom_distance = adsk.core.ValueInput.createByReal(0.2)  # 2mm bottom
        bottom_extrude_input.setDistanceExtent(False, bottom_distance)
        bottom_extrude = extrudes.add(bottom_extrude_input)
        
        # Color it green
        for i in range(fs_comp.bRepBodies.count):
            body = fs_comp.bRepBodies.item(i)
            apply_color(body, "Green", 100, 200, 100)
        
    except Exception as e:
        ui.messageBox(f'Error in flex spline: {str(e)}')

def create_wave_generator(root, base_radius_cm):
    """Create the wave generator (elliptical cam)"""
    try:
        # Create component with offset
        occs = root.occurrences
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, 0.5)  # 5mm offset
        wg_occ = occs.addNewComponent(transform)
        wg_comp = wg_occ.component
        wg_comp.name = "WaveGenerator"
        
        # Create sketch
        sketches = wg_comp.sketches
        xy_plane = wg_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Create ellipse
        curves = sketch.sketchCurves
        
        # Calculate ellipse dimensions
        eccentricity = 0.1  # 1mm eccentricity
        major_radius = base_radius_cm - 0.2 + eccentricity
        minor_radius = base_radius_cm - 0.2 - eccentricity
        
        # Create ellipse using points
        points = adsk.core.ObjectCollection.create()
        num_points = 50
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = major_radius * math.cos(angle)
            y = minor_radius * math.sin(angle)
            point = adsk.core.Point3D.create(x, y, 0)
            points.add(point)
        
        points.add(points.item(0))  # Close the curve
        
        # Create spline
        spline = curves.sketchFittedSplines.add(points)
        
        # Add center hole for motor shaft
        center = adsk.core.Point3D.create(0, 0, 0)
        shaft_hole = sketch.sketchCurves.sketchCircles.addByCenterRadius(center, 0.25)  # 2.5mm radius
        
        # Extrude
        profiles = sketch.profiles
        if profiles.count > 1:
            # Get the ellipse profile (not the hole)
            for i in range(profiles.count):
                profile = profiles.item(i)
                if profile.profileLoops.count == 2:  # Profile with hole
                    extrudes = wg_comp.features.extrudeFeatures
                    extrude_input = extrudes.createInput(
                        profile,
                        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                    )
                    distance = adsk.core.ValueInput.createByReal(2.0)  # 20mm height
                    extrude_input.setDistanceExtent(False, distance)
                    extrude = extrudes.add(extrude_input)
                    
                    # Color it red
                    if extrude.bodies.count > 0:
                        body = extrude.bodies.item(0)
                        apply_color(body, "Red", 200, 100, 100)
                    break
        
    except Exception as e:
        ui.messageBox(f'Error in wave generator: {str(e)}')

def add_teeth_marks(sketch, radius, num_teeth, is_internal):
    """Add simple lines to represent teeth"""
    try:
        lines = sketch.sketchCurves.sketchLines
        
        for i in range(num_teeth):
            angle = 2 * math.pi * i / num_teeth
            
            # Start point on circle
            x1 = radius * math.cos(angle)
            y1 = radius * math.sin(angle)
            
            # End point (slightly in or out)
            tooth_height = 0.05  # 0.5mm
            if is_internal:
                r2 = radius + tooth_height
            else:
                r2 = radius - tooth_height
            
            x2 = r2 * math.cos(angle)
            y2 = r2 * math.sin(angle)
            
            # Draw line
            p1 = adsk.core.Point3D.create(x1, y1, 0)
            p2 = adsk.core.Point3D.create(x2, y2, 0)
            lines.addByTwoPoints(p1, p2)
            
    except:
        pass  # Silently fail if too many teeth

def apply_color(body, name, r, g, b):
    """Apply color to a body"""
    try:
        design = app.activeProduct
        appearances = design.appearances
        
        # Try to find existing appearance
        appearance = None
        for i in range(appearances.count):
            if appearances.item(i).name == name:
                appearance = appearances.item(i)
                break
        
        # Create if not found
        if not appearance:
            appearance = appearances.add()
            appearance.name = name
            
            color_prop = appearance.appearanceProperties.itemByName("Color")
            if color_prop:
                color_value = adsk.core.Color.create(r, g, b, 255)
                color_prop.value = color_value
        
        body.appearance = appearance
        
    except:
        pass  # Silently fail if can't apply color