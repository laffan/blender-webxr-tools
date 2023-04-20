import bpy
import os
from .connectBSDF import connectBSDF

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
                        print(progress_message)
                        progress += 1


                        # Bake the texture
                        bpy.ops.object.bake(type='COMBINED')

            # Deselect the object after baking
            obj.select_set(False)
            wm.progress_end()
