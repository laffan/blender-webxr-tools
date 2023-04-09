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

