"""
Debug script to analyze the dome material structure
Run this in Blender after creating a canvas
"""

import bpy

def analyze_material(mat, depth=0):
    """Recursively analyze a material's node tree"""
    indent = "  " * depth
    
    if not mat or not mat.use_nodes:
        print(f"{indent}No nodes")
        return
    
    print(f"\n{indent}=== Material: {mat.name} ===")
    
    for node in mat.node_tree.nodes:
        print(f"{indent}Node: {node.name} ({node.type})")
        
        # Show specific properties based on node type
        if node.type == 'TEX_ENVIRONMENT':
            print(f"{indent}  projection: {node.projection}")
            print(f"{indent}  image: {node.image.name if node.image else 'None'}")
        
        elif node.type == 'TEX_COORD':
            print(f"{indent}  object: {node.object.name if node.object else 'None'}")
        
        elif node.type == 'MAPPING':
            print(f"{indent}  location: {list(node.inputs['Location'].default_value)}")
            print(f"{indent}  rotation: {list(node.inputs['Rotation'].default_value)}")
            print(f"{indent}  scale: {list(node.inputs['Scale'].default_value)}")
        
        elif node.type == 'GROUP':
            print(f"{indent}  node_tree: {node.node_tree.name if node.node_tree else 'None'}")
            if node.node_tree:
                analyze_node_tree(node.node_tree, depth + 2)
        
        # Show connections
        for input in node.inputs:
            if input.is_linked:
                for link in input.links:
                    print(f"{indent}  <- {input.name} from {link.from_node.name}.{link.from_socket.name}")

def analyze_node_tree(node_tree, depth=0):
    """Analyze a node tree (node group)"""
    indent = "  " * depth
    print(f"\n{indent}--- Node Group: {node_tree.name} ---")
    
    for node in node_tree.nodes:
        print(f"{indent}Node: {node.name} ({node.type})")
        
        if node.type == 'TEX_ENVIRONMENT':
            print(f"{indent}  projection: {node.projection}")
            print(f"{indent}  image: {node.image.name if node.image else 'None'}")
        
        elif node.type == 'TEX_COORD':
            print(f"{indent}  object: {node.object.name if node.object else 'None'}")
        
        elif node.type == 'MAPPING':
            print(f"{indent}  location: {list(node.inputs['Location'].default_value)}")
            print(f"{indent}  rotation: {list(node.inputs['Rotation'].default_value)}")
            print(f"{indent}  scale: {list(node.inputs['Scale'].default_value)}")
        
        elif node.type == 'GROUP':
            print(f"{indent}  node_tree: {node.node_tree.name if node.node_tree else 'None'}")
            if node.node_tree:
                analyze_node_tree(node.node_tree, depth + 2)

# Find the HDRI sphere and analyze its material
sphere = bpy.data.objects.get('HDRI_Sphere')
if sphere:
    print("\n" + "="*60)
    print("HDRI SPHERE MATERIAL ANALYSIS")
    print("="*60)
    
    if sphere.active_material:
        analyze_material(sphere.active_material)
    else:
        print("No active material on sphere!")
else:
    print("HDRI_Sphere not found!")

# Also check the world material for reference
if bpy.context.scene.world and bpy.context.scene.world.use_nodes:
    print("\n" + "="*60)
    print("WORLD MATERIAL ANALYSIS")
    print("="*60)
    for node in bpy.context.scene.world.node_tree.nodes:
        print(f"Node: {node.name} ({node.type})")
        if node.type == 'TEX_ENVIRONMENT':
            print(f"  projection: {node.projection}")
