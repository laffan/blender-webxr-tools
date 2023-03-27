import bpy
import os

# loop through all materials and connect "Bake" node to "Surface" output
def connectBakeNodes(materials):
    for material in materials:
        if material.node_tree is not None:  # Check if the material has a node tree
            # check if "Bake" node exists in material
            bake_node = None
            for node in material.node_tree.nodes:
                if node.label == "Bake":
                    bake_node = node
                    break
            # connect "Bake" node to "Surface" output if it exists
            if bake_node is not None:
                material_output = material.node_tree.nodes.get("Material Output")
                if material_output is not None:  # Check if the Material Output node exists
                    color_output = bake_node.outputs.get("Color")
                    surface_input = material_output.inputs.get("Surface")
                    if color_output is not None and surface_input is not None:
                        material.node_tree.links.new(color_output, surface_input)


def connectBSDF(materials):
    for material in materials:
        if material.node_tree is not None:  # Check if the material has a node tree
            material.node_tree.links.clear()

            principled_bsdf_node = None
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled_bsdf_node = node
                    break

            if principled_bsdf_node is not None:
                material_output = material.node_tree.nodes.get("Material Output")
                if material_output is not None:
                    bsdf_output = principled_bsdf_node.outputs.get("BSDF")
                    surface_input = material_output.inputs.get("Surface")
                    if bsdf_output is not None and surface_input is not None:
                        material.node_tree.links.new(bsdf_output, surface_input)


# get the directory of the blend file and export gltf
def exportTheGLTF():
    blend_filepath = bpy.data.filepath
    blend_dir = os.path.dirname(blend_filepath)
    export_path = os.path.join(blend_dir, os.path.splitext(os.path.basename(blend_filepath))[0] + ".gltf")
    bpy.ops.export_scene.gltf(filepath=export_path,
                          check_existing=False,
                          export_format='GLTF_EMBEDDED',
                          export_colors=False)

