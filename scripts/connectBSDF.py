import bpy
import os

def connectBSDF(materials):
    for material in materials:
        if material.node_tree is not None:  # Check if the material has a node tree

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
                        # First, check if the connection already exists
                        existing_link = None
                        for link in material.node_tree.links:
                            if link.from_socket == bsdf_output and link.to_socket == surface_input:
                                existing_link = link
                                break

                        # If the connection does not exist, create a new one
                        if existing_link is None:
                            material.node_tree.links.new(bsdf_output, surface_input)
                                