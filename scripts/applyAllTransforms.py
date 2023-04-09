import bpy
import os

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
