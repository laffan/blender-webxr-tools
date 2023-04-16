import bpy
import os
import glob
import subprocess
import re

# Get user dir
# root_dir = "/Users/nate"
root_dir = os.path.expanduser("~")

def exportGLTF(model_export_path):
    bpy.ops.export_scene.gltf(filepath=model_export_path,
                          check_existing=False,
                          export_format='GLTF_EMBEDDED',
                          export_colors=False,
                          use_selection=False,
                          )
    return model_export_path 

def exportGLB(model_export_path):
    bpy.ops.export_scene.gltf(filepath=model_export_path,
                          check_existing=False,
                          export_format='GLB',
                          export_colors=False,
                          use_selection=False,
                          )
    return model_export_path


def gltfjsxExport(file_type, model_directory, jsx_directory, jsxUpdateType ):

    file_type_lower = file_type.lower()  # Convert file_type to lowercase

    blend_filepath = bpy.data.filepath
    blend_filename = os.path.splitext(os.path.basename(blend_filepath))[0] + f".{file_type_lower}"

    model_directory_parts = model_directory.split('/')
    model_export_path = os.path.join(root_dir, *model_directory_parts, blend_filename)

    if file_type == "GLB":
        exportGLB(model_export_path)
    elif file_type == "GLTF":
        exportGLTF(model_export_path)
    else:
        raise ValueError("Invalid file type. Must be 'GLB' or 'GLTF'.")

    # 1. Split the exportPath into 2 pieces: the filename and the rest of the path (directory)
    directory, filename = os.path.split(model_export_path)

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
    base_filename, ext = os.path.splitext(filename)        
    
    if file_type == "GLTF":
        # Get the base filename without the extension
        # rename the glb file
        os.rename(os.path.join(directory, f"{base_filename}-transformed.glb"), os.path.join(directory, f"{base_filename}.glb"))
        # Delete the original GLTF file
        os.remove(model_export_path)



    # Capitalize the initial name to get the jsx that is output by gltfjsx
    filename_without_ext = os.path.splitext(filename)[0]
    capitalized_filename = filename_without_ext[0].upper() + filename_without_ext[1:]
    temp_jsx_filepath = os.path.join(directory, capitalized_filename + ".jsx")

    def to_camel_case(name):
        components = re.split(r'[-_]', name)
        return components[0].title() + ''.join(x.title() for x in components[1:])


    camelFileName = to_camel_case(base_filename) + ".jsx"
    jsx_directory_parts = jsx_directory.split('/')
    existing_jsx_filepath = os.path.join(root_dir, *jsx_directory_parts, camelFileName)

    def update_attributes_only(existing_jsx, temp_jsx):
        updated_jsx = existing_jsx

        def parse_meshes_and_groups(jsx):
            regex_pattern = r'(<(mesh|group)(?:\s[^>]*)*>)'
            return re.findall(regex_pattern, jsx)

        existing_tags = parse_meshes_and_groups(existing_jsx)
        temp_tags = parse_meshes_and_groups(temp_jsx)

        for idx, (temp_full_tag, temp_tag) in enumerate(temp_tags):
            temp_attrs = temp_full_tag[len(temp_tag) + 1:-1]  # Extract attributes string without the tag name and angle brackets
            if idx < len(existing_tags):
                existing_full_tag, existing_tag = existing_tags[idx]
                existing_attrs = existing_full_tag[len(existing_tag) + 1:-1]  # Extract attributes string without the tag name and angle brackets

                if temp_tag == existing_tag:
                    for attr_name in ["geometry", "material", "position"]:
                        temp_attr_regex = r'({}\s*=\s*\{{[^\}}]*\}})'.format(attr_name)
                        temp_attr = next((attr for attr in re.findall(temp_attr_regex, temp_attrs) if attr.startswith(attr_name)), None)
                        existing_attr = next((attr for attr in re.findall(temp_attr_regex, existing_attrs) if attr.startswith(attr_name)), None)

                        if temp_attr and existing_attr and temp_attr != existing_attr:
                            updated_jsx = updated_jsx.replace(existing_attr, temp_attr)

        return updated_jsx
    
    if os.path.exists(existing_jsx_filepath):
        # Update ONLY the return statement of the existing file
        if jsxUpdateType == "ONLYRETURN":
            with open(temp_jsx_filepath, "r") as temp_jsx_file:
                temp_contents = temp_jsx_file.read()
                temp_match = re.search(r'return\s*\(([^()]*)\)', temp_contents)
                if temp_match:
                    temp_return_statement = temp_match.group(1)
                    
                    with open(existing_jsx_filepath, "r") as existing_jsx_file:
                        existing_contents = existing_jsx_file.read()
                        updated_contents = re.sub(r'return\s*\(([^()]*)\)', f'return ({temp_return_statement})', existing_contents)

                    with open(existing_jsx_filepath, "w") as existing_jsx_file:
                        existing_jsx_file.write(updated_contents)

        elif jsxUpdateType == "ONLYATTRIBUTES":
            print("ONLYATTRIBUTES")
            with open(temp_jsx_filepath, "r") as temp_jsx_file:
                temp_contents = temp_jsx_file.read()
                        
                with open(existing_jsx_filepath, "r") as existing_jsx_file:
                    existing_contents = existing_jsx_file.read()

                    updated_contents = update_attributes_only(existing_contents, temp_contents)
                
                with open(existing_jsx_filepath, "w") as existing_jsx_file:
                    existing_jsx_file.write(updated_contents)

                    
        else:
            # 4. Delete the temp_jsx_filepath
            os.remove(temp_jsx_filepath)

    else:
        # 3. Move the temp_jsx_filepath
        os.rename(temp_jsx_filepath, existing_jsx_filepath)