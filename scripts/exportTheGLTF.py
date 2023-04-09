import bpy
import os



# get the directory of the blend file and export gltf
def exportTheGLTF():
    blend_filepath = bpy.data.filepath
    blend_dir = os.path.dirname(blend_filepath)
    export_path = os.path.join(blend_dir, os.path.splitext(os.path.basename(blend_filepath))[0] + ".gltf")
    bpy.ops.export_scene.gltf(filepath=export_path,
                          check_existing=False,
                          export_format='GLTF_EMBEDDED',
                          export_colors=False,
                          use_selection=False
                          )