bl_info = {
    "name": "Platonic Solids Generator",
    "author": "Valentine Khytryi IK-32",
    "version": (1,1),
    "blender": (2, 80, 0),
    "location": "View3D > UI > Platonic Solids",
    "description": "Generate and manage Platonic solids with a simple UI",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, FloatVectorProperty, EnumProperty, PointerProperty
import math

# List of available shapes
PLATONIC_SOLIDS = [
    ('TETRAHEDRON', 'Tetrahedron', ''),
    ('CUBE', 'Cube', ''),
    ('OCTAHEDRON', 'Octahedron', ''),
    ('DODECAHEDRON', 'Dodecahedron', ''),
    ('ICOSAHEDRON', 'Icosahedron', ''),
]

class PlatonicSolidProperties(PropertyGroup):
    shape_type: EnumProperty(
        name="Shape",
        description="Type of platonic solid to create",
        items=PLATONIC_SOLIDS,
        default='TETRAHEDRON'
    )
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.8, 0.8, 0.8, 1.0)
    )
    
    scale: bpy.props.FloatProperty(
        name="Scale",
        default=1.0,
        min=0.1,
        max=10.0,
        description="Scale of the generated shape"
    )
    
    clear_before_create: bpy.props.BoolProperty(
        name="Clear Before Create",
        description="Clear all objects before creating a new one",
        default=False
    )

def generate_geometry(name):
    vertices = []
    edges = []
    faces = []
    
    match name:
        case 'TETRAHEDRON':
            vertices = [(0.943,0,-0.333), (-0.471,-0.816,-0.333), (-0.471,0.816,-0.333), (0, 0, 1)]
            faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
            
        case 'CUBE':
            vertices = [(1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1), 
                      (1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1)]
            faces = [(0, 1, 2, 3), (0, 1, 5, 4), (1, 2, 6, 5), 
                   (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
            
        case 'OCTAHEDRON':
            vertices = [(0, 0, -1), (-1, 0, 0), (0, -1, 0), 
                      (1, 0, 0), (0, 1, 0), (0, 0, 1)]
            faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), 
                   (5, 1, 2), (5, 2, 3), (5, 3, 4), (5, 4, 1)]
        
        case 'DODECAHEDRON':
            vertices = [
                (1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1), 
                (1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1),
                (0, 1.618, 0.618), (0, -1.618, 0.618), 
                (0, -1.618, -0.618), (0, 1.618, -0.618),
                (0.618, 0, 1.618), (-0.618, 0, 1.618), 
                (-0.618, 0, -1.618), (0.618, 0, -1.618),
                (1.618, 0.618, 0), (-1.618, 0.618, 0), 
                (-1.618, -0.618, 0), (1.618, -0.618, 0)
            ]
            faces = [
                (8, 11, 4, 16, 0), (8, 11, 7, 17, 3), (9, 10, 5, 19, 1), 
                (9, 10, 6, 18, 2), (12, 13, 3, 8, 0), (12, 13, 2, 9, 1), 
                (15, 14, 7, 11, 4), (15, 14, 6, 10, 5), (16, 19, 1, 12, 0), 
                (16, 19, 5, 15, 4), (17, 18, 2, 13, 3), (17, 18, 6, 14, 7)
            ]
            
        case 'ICOSAHEDRON':
            vertices = [
                (0, 1, 1.618), (0, -1, 1.618), (0, 1, -1.618), (0, -1, -1.618),
                (1.618, 0, 1), (1.618, 0, -1), (-1.618, 0, 1), (-1.618, 0, -1),
                (1, 1.618, 0), (-1, 1.618, 0), (1, -1.618, 0), (-1, -1.618, 0)
            ]
            faces = [
                (0, 1, 4), (0, 1, 6), (2, 3, 5), (2, 3, 7),
                (4, 5, 8), (4, 5, 10), (6, 7, 9), (6, 7, 11),
                (8, 9, 0), (8, 9, 2), (10, 11, 1), (10, 11, 3),
                (0, 4, 8), (1, 4, 10), (1, 6, 11), (0, 6, 9),
                (2, 5, 8), (3, 5, 10), (3, 7, 11), (2, 7, 9)
            ]
    
    return vertices, edges, faces

class OBJECT_OT_generate_platonic(Operator):
    bl_idname = "object.generate_platonic"
    bl_label = "Generate Platonic Solid"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.platonic_props
        
        # Clear all objects if the option is enabled
        if props.clear_before_create:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False, confirm=False)
        
        # Generate the geometry
        vertices, edges, faces = generate_geometry(props.shape_type)
        
        # Create mesh and object
        mesh = bpy.data.meshes.new(name=props.shape_type.capitalize())
        mesh.from_pydata(vertices, edges, faces)
        mesh.update()
        
        obj = bpy.data.objects.new(props.shape_type.capitalize(), mesh)
        context.collection.objects.link(obj)
        
        # Apply color
        mat = bpy.data.materials.new(name=f"{props.shape_type}_Material")
        mat.diffuse_color = props.color
        
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        # Apply scale
        obj.scale = (props.scale, props.scale, props.scale)
        
        # Select the new object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        return {'FINISHED'}

class OBJECT_OT_delete_selected(Operator):
    bl_idname = "object.delete_selected"
    bl_label = "Delete Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.delete(use_global=False, confirm=False)
        return {'FINISHED'}

class OBJECT_OT_clear_scene(Operator):
    bl_idname = "object.clear_scene"
    bl_label = "Clear All Objects"
    bl_description = "Remove all objects from the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Select all objects
        bpy.ops.object.select_all(action='SELECT')
        # Delete all selected objects
        bpy.ops.object.delete(use_global=False, confirm=False)
        return {'FINISHED'}

class OBJECT_OT_change_color(Operator):
    bl_idname = "object.change_color"
    bl_label = "Change Color"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.platonic_props
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                if not obj.data.materials:
                    mat = bpy.data.materials.new(name="Platonic_Material")
                    obj.data.materials.append(mat)
                else:
                    mat = obj.data.materials[0]
                
                mat.diffuse_color = props.color
        
        return {'FINISHED'}

class VIEW3D_PT_platonic_solids(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Platonic Solids'
    bl_label = 'Platonic Solids Generator'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.platonic_props
        
        box = layout.box()
        box.label(text="Create New Shape:")
        box.prop(props, "shape_type")
        box.prop(props, "scale")
        row = box.row()
        row.prop(props, "clear_before_create", toggle=True)
        box.operator("object.generate_platonic")
        
        box = layout.box()
        box.label(text="Edit Selected:")
        box.prop(props, "color", text="")
        row = box.row()
        row.operator("object.change_color")
        row.operator("object.delete_selected", icon='TRASH')
        
        box = layout.box()
        box.label(text="Scene Management:")
        box.operator("object.clear_scene", icon='TRASH')
        box.label(text="Warning: Deletes all objects", icon='ERROR')

def register():
    bpy.utils.register_class(PlatonicSolidProperties)
    bpy.types.Scene.platonic_props = PointerProperty(type=PlatonicSolidProperties)
    
    bpy.utils.register_class(OBJECT_OT_generate_platonic)
    bpy.utils.register_class(OBJECT_OT_delete_selected)
    bpy.utils.register_class(OBJECT_OT_clear_scene)
    bpy.utils.register_class(OBJECT_OT_change_color)
    bpy.utils.register_class(VIEW3D_PT_platonic_solids)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_platonic_solids)
    bpy.utils.unregister_class(OBJECT_OT_change_color)
    bpy.utils.unregister_class(OBJECT_OT_clear_scene)
    bpy.utils.unregister_class(OBJECT_OT_delete_selected)
    bpy.utils.unregister_class(OBJECT_OT_generate_platonic)
    
    del bpy.types.Scene.platonic_props
    bpy.utils.unregister_class(PlatonicSolidProperties)

if __name__ == "__main__":
    register()
