# Blender Add-on Template
# Contributor(s): Aaron Powell (aaron@lunadigital.tv)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
        "name": "The WebXR Belt",
        "description": "Tools to help the transition from blender to web.",
        "author": "Nate Laffan",
        "version": (1, 0),
        "blender": (3, 4, 1),
        "location": "Sidebar",
        "warning": "", # used for warning icon and text in add-ons panel
        "wiki_url": "http://my.wiki.url",
        "tracker_url": "http://my.bugtracker.url",
        "support": "COMMUNITY",
        "category": "Tools"
        }

import bpy
import importlib
import os
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper


# Import functions and reload them so they aren't cached by mistake.

def import_and_reload_functions(function_names):
    imported_functions = {}
    
    for function_name in function_names:
        module_name = f"scripts.{function_name}"
        if module_name in globals():
            importlib.reload(globals()[module_name])
        else:
            globals()[module_name] = importlib.import_module(f".{module_name}", __package__)
        
        imported_functions[function_name] = getattr(globals()[module_name], function_name)
    
    return imported_functions

# List of function names matching their file names
function_names = ["connectBakeNodes", "applyAllTransforms", "connectBSDF", "rebakeAll", "gltfjsxExport", "setOriginToGeometry"]

# Import and reload functions
imported_functions = import_and_reload_functions(function_names)

connectBakeNodes = imported_functions["connectBakeNodes"]
applyAllTransforms = imported_functions["applyAllTransforms"]
connectBSDF = imported_functions["connectBSDF"]
rebakeAll = imported_functions["rebakeAll"]
gltfjsxExport = imported_functions["gltfjsxExport"]
setOriginToGeometry = imported_functions["setOriginToGeometry"]

class SimplePanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_simple_panel"
    bl_label = "Blender Belt"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "++ Belt ++"

    bpy.types.Scene.model_path = StringProperty(name="Model File Path", subtype="FILE_PATH")

    bpy.types.Scene.jsx_path = StringProperty(name="JSX File Path", subtype="FILE_PATH")

    # Define the EnumProperty
    bpy.types.Scene.jsxUpdateType = bpy.props.EnumProperty(
        name="JSX Update Type",
        description="Choose an option",
        items=[
            ("FILE", "File", "Overwrite JSX file"),
            ("ONLYRETURN", "Return", "Overwrite only return statement. (Maintain import path.)"),
            ("ONLYATTRIBUTES", "Attributes", "Only overwrite attributes. (Materials and position. May break if new meshes exist.)"),
        ],
        default="FILE",
    )


    def draw(self, context):
        layout = self.layout

        # Wrap existing buttons in a group
        box = layout.box()
        box.label(text="Nodes / Baking")
        box.operator("script.run_script1")
        box.operator("script.run_script2")
        box.operator("script.run_script4")

        # New group with two lines
        box = layout.box()
        box.label(text="Transforms")

        box.operator("script.run_script5")
        box.operator("script.run_script6")

        box = layout.box()
        box.label(text="Export & Copy JSX")
        
        row = box.row()
        row.prop(context.scene, "model_path", text="Model Path")
        row = box.row()
        row.prop(context.scene, "jsx_path", text="JSX Path")
            # Create a row with three buttons
        row = box.row()
        row.prop(context.scene, "jsxUpdateType", expand=True)


        # Line 2: Export buttons
        row = box.row()
        row.operator("export.export_glb", text="GLB")
        row.operator("export.export_gltf", text="GLTF (Transformed)")

class ExportGLB(bpy.types.Operator):
    bl_idname = "export.export_glb"
    bl_label = "Export GLB"

    def execute(self, context):
        model_directory = os.path.abspath(context.scene.model_path)
        jsx_directory = os.path.abspath(context.scene.jsx_path)
        gltfjsxExport("GLB", model_directory, jsx_directory, context.scene.jsxUpdateType )
        return {'FINISHED'}

class ExportGLTF(bpy.types.Operator):
    bl_idname = "export.export_gltf"
    bl_label = "Export GLTF"

    def execute(self, context):
        model_directory = os.path.abspath(context.scene.model_path)
        jsx_directory = os.path.abspath(context.scene.jsx_path)
        gltfjsxExport("GLTF", model_directory, jsx_directory, context.scene.jsxUpdateType  )
        return {'FINISHED'}


class Button1(bpy.types.Operator):
    bl_idname = "script.run_script1"
    bl_label = "Connect Bake Nodes"

    def execute(self, context):
        materials = bpy.data.materials
        connectBakeNodes(materials)
        return {'FINISHED'}

class Button2(bpy.types.Operator):
    bl_idname = "script.run_script2"
    bl_label = "Connect BSDF"

    def execute(self, context):
        materials = bpy.data.materials
        connectBSDF(materials)
        return {'FINISHED'}

class Button4(bpy.types.Operator):
    bl_idname = "script.run_script4"
    bl_label = "Rebake All (TBD)"

    def execute(self, context):
        rebakeAll()
        return {'FINISHED'}

class Button5(bpy.types.Operator):
    bl_idname = "script.run_script5"
    bl_label = "Apply All Transforms"

    def execute(self, context):
        applyAllTransforms()
        return {'FINISHED'}
class Button6(bpy.types.Operator):
    bl_idname = "script.run_script6"
    bl_label = "All Origins to Geometry"

    def execute(self, context):
        setOriginToGeometry()
        return {'FINISHED'}

def register():
    bpy.types.Scene.copy_jsx_only = bpy.props.BoolProperty(default=False)
    bpy.utils.register_class(SimplePanel)
    bpy.utils.register_class(Button1)
    bpy.utils.register_class(Button2)
    bpy.utils.register_class(Button4)
    bpy.utils.register_class(Button5)
    bpy.utils.register_class(Button6)
    bpy.utils.register_class(ExportGLB)
    bpy.utils.register_class(ExportGLTF)

def unregister():
    bpy.utils.unregister_class(SimplePanel)
    bpy.utils.unregister_class(Button1)
    bpy.utils.unregister_class(Button2)
    bpy.utils.unregister_class(Button4)
    bpy.utils.unregister_class(Button5)
    bpy.utils.unregister_class(Button6)
    bpy.utils.unregister_class(ExportGLB)
    bpy.utils.unregister_class(ExportGLTF)


if __name__ == "__main__":
    register()