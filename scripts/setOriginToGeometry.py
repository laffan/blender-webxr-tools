import bpy
import os

def setOriginToGeometry():
  # Get all meshes in the scene
  meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

  # Loop through each mesh and set origin to geometry
  for mesh in meshes:
      # Select the mesh and make it active
      bpy.context.view_layer.objects.active = mesh
      mesh.select_set(True)
      
      # Set origin to geometry
      bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
      
      # Deselect the mesh
      mesh.select_set(False)