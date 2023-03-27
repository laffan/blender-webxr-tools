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

def applyAllTransforms():
  # Get all meshes in the scene
  meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

  # Loop through each mesh and apply all transforms
  for mesh in meshes:
      # Select the mesh and make it active
      bpy.context.view_layer.objects.active = mesh
      mesh.select_set(True)
      
      # Apply all transforms
      bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
      
      # Deselect the mesh
      mesh.select_set(False)


def rebakeAll():
    materials = bpy.data.materials
    connectBSDF(materials)
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    # Initialize the progress bar
    wm = bpy.context.window_manager
    progress = 0
    wm.progress_begin(0, len(mesh_objects))


    # Loop through each object in the scene
    for index, obj in enumerate(mesh_objects):
        if obj.type == 'MESH':
            # Select the object
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            # Check if the object has a material
            if obj.data.materials:
                material = obj.data.materials[0]
                if material.node_tree is not None:
                    # Find the image texture node labeled "bake"
                    bake_node = None
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.label == 'Bake':
                            bake_node = node
                            break

                    if bake_node is not None:
                        # Set the image texture node as active
                        material.node_tree.nodes.active = bake_node

                        # Update the progress bar
                        wm.progress_update(index)
                        progress_message = f"Baking mesh: {obj.name}"
                        # Update the progress bar
                        progress += 1
                        wm.progress_update(progress)

                        # Bake the texture
                        bpy.ops.object.bake(type='COMBINED')

            # Deselect the object after baking
            obj.select_set(False)
            wm.progress_end()
