import bpy
import os
import glob
import subprocess
import re


root_dir = "/Users/nate"

def exportGLTF(export_path):
    bpy.ops.export_scene.gltf(filepath=export_path,
                          check_existing=False,
                          export_format='GLTF_EMBEDDED',
                          export_colors=False,
                          use_selection=False
                          )
    return export_path 

def exportGLB(export_path):
    bpy.ops.export_scene.gltf(filepath=export_path,
                          check_existing=False,
                          export_format='GLB',
                          export_colors=False,
                          use_selection=False
                          )
    return export_path


def gltfjsxExport(file_type, target_path, copy_jsx_only):

    file_type_lower = file_type.lower()  # Convert file_type to lowercase

    blend_filepath = bpy.data.filepath
    blend_filename = os.path.splitext(os.path.basename(blend_filepath))[0] + f".{file_type_lower}"

    target_parts = target_path.split('/')
    export_path = os.path.join(root_dir, *target_parts, blend_filename)

    if file_type == "GLB":
        exportGLB(export_path)
    elif file_type == "GLTF":
        exportGLTF(export_path)
    else:
        raise ValueError("Invalid file type. Must be 'GLB' or 'GLTF'.")

    # 1. Split the exportPath into 2 pieces: the filename and the rest of the path (directory)
    directory, filename = os.path.split(export_path)

    # 2. Delete all .jsx files from the directory
    for jsx_file in glob.glob(os.path.join(directory, "*.jsx")):
        os.remove(jsx_file)

    # 2. Execute the following bash script inside the directory

    if file_type == "GLB":
        command = f"npx gltfjsx {filename} --keepgroups --keepnames"
    elif file_type == "GLTF":
        command = f"npx gltfjsx {filename} --transform -R 8192 --keepgroups --keepnames"
    else:
        raise ValueError("Invalid file type. Must be 'GLB' or 'GLTF'.")

    subprocess.run(command, shell=True, cwd=directory, check=True)

    # If using a GLTF file that has been transformed, remove the original
    # and rename the glb file.
    if file_type == "GLTF":
        # Get the base filename without the extension
        base_filename, ext = os.path.splitext(filename)        
        # rename the glb file
        os.rename(os.path.join(directory, f"{base_filename}-transformed.glb"), os.path.join(directory, f"{base_filename}.glb"))
        # Delete the original GLTF file
        os.remove(export_path)



    # 3. This script will output a file of the same name with a .jsx suffix.
    jsx_filepath = os.path.join(directory, os.path.splitext(filename)[0] + ".jsx")
    
    # Copy the contents of this file to the clipboard and delete the .jsx file.
    with open(jsx_filepath, "r") as jsx_file:
        contents = jsx_file.read()
        if copy_jsx_only == True:
            print("MISTERT")
            match = re.search(r'return\s*\(([^()]*)\)', contents)
            if match:
                contents = match.group(1)
        bpy.context.window_manager.clipboard = contents

        
    os.remove(jsx_filepath)
