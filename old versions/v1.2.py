# Improved Platonic Solids Generator with OOP principles

import bpy
import math
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import EnumProperty, FloatVectorProperty, FloatProperty, BoolProperty, PointerProperty

bl_info = {
    "name": "Platonic Solids Generator",
    "author": "Valentine Khytryi IK-32",
    "version": (2, 0),
    "blender": (2, 80, 0),
    "location": "View3D > UI > Platonic Solids",
    "description": "Generate and manage Platonic solids with a simple UI",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

# ==== Core Geometry Classes ====
class PlatonicSolid:
    def get_geometry(self):
        raise NotImplementedError("Must be implemented in subclasses")

class Tetrahedron(PlatonicSolid):
    def get_geometry(self):
        vertices = [(0.943,0,-0.333), (-0.471,-0.816,-0.333), (-0.471,0.816,-0.333), (0, 0, 1)]
        faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
        return vertices, [], faces

class Cube(PlatonicSolid):
    def get_geometry(self):
        vertices = [(1,1,1),(1,-1,1),(-1,-1,1),(-1,1,1), (1,1,-1),(1,-1,-1),(-1,-1,-1),(-1,1,-1)]
        faces = [(0,1,2,3),(4,5,6,7),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
        return vertices, [], faces

class Octahedron(PlatonicSolid):
    def get_geometry(self):
        vertices = [(0, 0, -1), (-1, 0, 0), (0, -1, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
        faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (5, 1, 2), (5, 2, 3), (5, 3, 4), (5, 4, 1)]
        return vertices, [], faces

class Dodecahedron(PlatonicSolid):
    def get_geometry(self):
        vertices = [(1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1), 
                (1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1),
                (0, 1.618, 0.618), (0, -1.618, 0.618), 
                (0, -1.618, -0.618), (0, 1.618, -0.618),
                (0.618, 0, 1.618), (-0.618, 0, 1.618), 
                (-0.618, 0, -1.618), (0.618, 0, -1.618),
                (1.618, 0.618, 0), (-1.618, 0.618, 0), 
                (-1.618, -0.618, 0), (1.618, -0.618, 0)]
        faces = [(8, 11, 4, 16, 0), (8, 11, 7, 17, 3), (9, 10, 5, 19, 1), 
                (9, 10, 6, 18, 2), (12, 13, 3, 8, 0), (12, 13, 2, 9, 1), 
                (15, 14, 7, 11, 4), (15, 14, 6, 10, 5), (16, 19, 1, 12, 0), 
                (16, 19, 5, 15, 4), (17, 18, 2, 13, 3), (17, 18, 6, 14, 7)]
        return vertices, [], faces

class Icosahedron(PlatonicSolid):
    def get_geometry(self):
        vertices = [
                (0, 1, 1.618), (0, -1, 1.618), (0, 1, -1.618), (0, -1, -1.618),
                (1.618, 0, 1), (1.618, 0, -1), (-1.618, 0, 1), (-1.618, 0, -1),
                (1, 1.618, 0), (-1, 1.618, 0), (1, -1.618, 0), (-1, -1.618, 0)
            ]
        faces = [(0, 1, 4), (0, 1, 6), (2, 3, 5), (2, 3, 7),
                (4, 5, 8), (4, 5, 10), (6, 7, 9), (6, 7, 11),
                (8, 9, 0), (8, 9, 2), (10, 11, 1), (10, 11, 3),
                (0, 4, 8), (1, 4, 10), (1, 6, 11), (0, 6, 9),
                (2, 5, 8), (3, 5, 10), (3, 7, 11), (2, 7, 9)]
        return vertices, [], faces

solid_classes = {
    'TETRAHEDRON': Tetrahedron,
    'CUBE': Cube,
    'OCTAHEDRON': Octahedron,
    'DODECAHEDRON': Dodecahedron,
    'ICOSAHEDRON': Icosahedron
}

# ==== Properties ====
class PlatonicSolidProperties(PropertyGroup):
    shape_type: EnumProperty(
        name="Shape",
        items=[(k, k.title(), '') for k in solid_classes.keys()],
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
    scale: FloatProperty(
        name="Scale",
        default=1.0,
        min=0.1,
        max=10.0
    )
    clear_before_create: BoolProperty(
        name="Clear Before Create",
        default=False
    )

# ==== Builder Utilities ====
class SolidBuilder:
    @staticmethod
    def create_mesh(name, vertices, edges, faces):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(vertices, edges, faces)
        mesh.update()
        return mesh

    @staticmethod
    def create_material(name, color):
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
        mat.diffuse_color = color
        return mat

# ==== Operators ====
class OBJECT_OT_generate_platonic(Operator):
    bl_idname = "object.generate_platonic"
    bl_label = "Generate Platonic Solid"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.platonic_props

        if props.clear_before_create:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

        solid_class = solid_classes.get(props.shape_type, Tetrahedron)
        solid = solid_class()
        vertices, edges, faces = solid.get_geometry()

        mesh = SolidBuilder.create_mesh(props.shape_type, vertices, edges, faces)
        obj = bpy.data.objects.new(props.shape_type, mesh)
        context.collection.objects.link(obj)
        obj.scale = (props.scale,) * 3

        mat = SolidBuilder.create_material(f"{props.shape_type}_Material", props.color)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}

class OBJECT_OT_change_color(Operator):
    bl_idname = "object.change_color"
    bl_label = "Change Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.platonic_props
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                mat = obj.data.materials[0] if obj.data.materials else bpy.data.materials.new(name="Updated_Material")
                mat.diffuse_color = props.color
                if not obj.data.materials:
                    obj.data.materials.append(mat)
        return {'FINISHED'}

class OBJECT_OT_delete_selected(Operator):
    bl_idname = "object.delete_selected"
    bl_label = "Delete Selected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.delete(use_global=False, confirm=False)
        return {'FINISHED'}

# ==== UI ====
class VIEW3D_PT_platonic_solids(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Platonic Solids'
    bl_label = 'Platonic Solids Generator'

    def draw(self, context):
        layout = self.layout
        props = context.scene.platonic_props

        # === Widget 1: Creation ===
        box = layout.box()
        box.label(text="1. Створення")
        box.prop(props, "shape_type")
        box.prop(props, "scale")
        box.prop(props, "clear_before_create")
        box.operator("object.generate_platonic")

        # === Widget 2: Selection ===
        box = layout.box()
        box.label(text="2. Виділення")
        box.operator("object.delete_selected", icon='TRASH')

        # === Widget 3: Editing ===
        box = layout.box()
        box.label(text="3. Редагування")
        box.prop(props, "color", text="Колір")
        box.operator("object.change_color")

# ==== Registration ====
def register():
    bpy.utils.register_class(PlatonicSolidProperties)
    bpy.types.Scene.platonic_props = PointerProperty(type=PlatonicSolidProperties)
    bpy.utils.register_class(OBJECT_OT_generate_platonic)
    bpy.utils.register_class(OBJECT_OT_change_color)
    bpy.utils.register_class(OBJECT_OT_delete_selected)
    bpy.utils.register_class(VIEW3D_PT_platonic_solids)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_platonic_solids)
    bpy.utils.unregister_class(OBJECT_OT_delete_selected)
    bpy.utils.unregister_class(OBJECT_OT_change_color)
    bpy.utils.unregister_class(OBJECT_OT_generate_platonic)
    del bpy.types.Scene.platonic_props
    bpy.utils.unregister_class(PlatonicSolidProperties)

if __name__ == "__main__":
    register()