"""
Debug script to analyze the sample dome material from the blend file
"""

import bpy

dome_mat_path = r"e:\Projects\HDRI_editor\sample\hdri_maker\addon_resources\blendfiles\materials\HDRi_Maker_Dome.blend"

print("\n" + "="*60)
print("LOADING AND ANALYZING SAMPLE DOME MATERIAL")
print("="*60)

def analyze_node_tree(node_tree, depth=0):
    """Analyze a node tree (node group)"""
    indent = "  " * depth
    print(f"\n{indent}--- Node Tree: {node_tree.name} ---")
    
    for node in node_tree.nodes:
        node_info = f"{indent}[{node.type}] {node.name}"
        print(node_info)
        
        if node.type == 'TEX_ENVIRONMENT':
            print(f"{indent}  >>> PROJECTION: {node.projection} <<<")
            print(f"{indent}  image: {node.image.name if node.image else 'None'}")
        
        elif node.type == 'TEX_COORD':
            print(f"{indent}  object: {node.object.name if node.object else 'None'}")
            # Show which outputs are connected
            for out in node.outputs:
                if out.is_linked:
                    for link in out.links:
                        print(f"{indent}  -> {out.name} connected to {link.to_node.name}")
        
        elif node.type == 'MAPPING':
            loc = list(node.inputs['Location'].default_value)
            rot = list(node.inputs['Rotation'].default_value)
            scale = list(node.inputs['Scale'].default_value)
            print(f"{indent}  location: {loc}")
            print(f"{indent}  rotation: {rot}")
            print(f"{indent}  scale: {scale}")
        
        elif node.type == 'VECT_TRANSFORM':
            print(f"{indent}  convert_from: {node.convert_from}")
            print(f"{indent}  convert_to: {node.convert_to}")
            print(f"{indent}  vector_type: {node.vector_type}")
        
        elif node.type == 'GROUP':
            print(f"{indent}  node_tree: {node.node_tree.name if node.node_tree else 'None'}")
            if node.node_tree:
                analyze_node_tree(node.node_tree, depth + 2)

try:
    # Load material
    with bpy.data.libraries.load(dome_mat_path, link=False) as (data_from, data_to):
        data_to.materials = [name for name in data_from.materials if name == 'HDRi_Maker_Dome']
        data_to.node_groups = data_from.node_groups[:]
    
    if data_to.materials:
        mat = data_to.materials[0]
        print(f"\nMaterial loaded: {mat.name}")
        print(f"Node groups loaded: {[ng.name for ng in data_to.node_groups]}")
        
        if mat.use_nodes:
            analyze_node_tree(mat.node_tree, 0)
    else:
        print("Material not found!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
