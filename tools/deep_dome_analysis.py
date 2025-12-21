"""
Deep analysis of sample dome setup to understand how it works
"""

import bpy
import os

# Path to sample dome blend file
dome_blend_path = r"e:\Projects\HDRI_editor\sample\hdri_maker\addon_resources\blendfiles\materials\HDRi_Maker_Dome.blend"

print("\n" + "="*70)
print("SAMPLE DOME DEEP ANALYSIS")
print("="*70)

# First, let's see what's in the blend file
print("\n1. CONTENTS OF DOME BLEND FILE:")
print("-"*50)

with bpy.data.libraries.load(dome_blend_path, link=False) as (data_from, data_to):
    print(f"  Materials: {data_from.materials}")
    print(f"  Objects: {data_from.objects}")
    print(f"  Meshes: {data_from.meshes}")
    print(f"  Node Groups: {data_from.node_groups}")

# Now load everything to analyze
print("\n2. LOADING ALL DATA FROM BLEND FILE:")
print("-"*50)

with bpy.data.libraries.load(dome_blend_path, link=False) as (data_from, data_to):
    data_to.materials = data_from.materials[:]
    data_to.objects = data_from.objects[:]
    data_to.meshes = data_from.meshes[:]
    data_to.node_groups = data_from.node_groups[:]

print(f"  Loaded materials: {[m.name for m in data_to.materials]}")
print(f"  Loaded objects: {[o.name for o in data_to.objects]}")
print(f"  Loaded meshes: {[m.name for m in data_to.meshes]}")
print(f"  Loaded node_groups: {[ng.name for ng in data_to.node_groups]}")

# Analyze any loaded objects
print("\n3. OBJECT ANALYSIS:")
print("-"*50)

for obj in data_to.objects:
    print(f"\n  Object: {obj.name}")
    print(f"    Type: {obj.type}")
    print(f"    Location: {list(obj.location)}")
    print(f"    Rotation: {list(obj.rotation_euler)}")
    print(f"    Scale: {list(obj.scale)}")
    
    if obj.type == 'MESH':
        mesh = obj.data
        print(f"    Mesh: {mesh.name}")
        print(f"    Vertices: {len(mesh.vertices)}")
        print(f"    Faces: {len(mesh.polygons)}")
        
        # Check normals direction by looking at a vertex
        if mesh.polygons:
            first_poly = mesh.polygons[0]
            print(f"    First face normal: {list(first_poly.normal)}")
        
        # Check UV layers
        print(f"    UV Layers: {[uv.name for uv in mesh.uv_layers]}")
        
        # Check materials
        print(f"    Materials: {[m.name if m else 'None' for m in obj.data.materials]}")

# Analyze the dome material in detail
print("\n4. DOME MATERIAL DETAILED ANALYSIS:")
print("-"*50)

dome_mat = None
for mat in data_to.materials:
    if 'Dome' in mat.name or 'dome' in mat.name:
        dome_mat = mat
        break

if dome_mat:
    print(f"\n  Material: {dome_mat.name}")
    print(f"  Use nodes: {dome_mat.use_nodes}")
    print(f"  Blend method: {dome_mat.blend_method}")
    print(f"  Shadow method: {dome_mat.shadow_method}")
    print(f"  Backface culling: {dome_mat.use_backface_culling}")
    
    if dome_mat.use_nodes:
        print(f"\n  NODE TREE STRUCTURE:")
        
        def print_node_tree(node_tree, indent=2):
            for node in node_tree.nodes:
                prefix = " " * indent
                print(f"{prefix}[{node.type}] {node.name}")
                
                # Special handling for different node types
                if node.type == 'TEX_COORD':
                    print(f"{prefix}  -> object: {node.object.name if node.object else 'None'}")
                    for out in node.outputs:
                        if out.is_linked:
                            for link in out.links:
                                print(f"{prefix}  -> {out.name} connected to {link.to_node.name}.{link.to_socket.name}")
                
                elif node.type == 'TEX_ENVIRONMENT':
                    print(f"{prefix}  -> projection: {node.projection}")
                    print(f"{prefix}  -> image: {node.image.name if node.image else 'None'}")
                
                elif node.type == 'MAPPING':
                    print(f"{prefix}  -> vector_type: {node.vector_type}")
                    # Check inputs for values
                    for inp in node.inputs:
                        if inp.name in ['Location', 'Rotation', 'Scale']:
                            print(f"{prefix}  -> {inp.name}: {list(inp.default_value)}")
                
                elif node.type == 'GROUP' and node.node_tree:
                    print(f"{prefix}  -> node_tree: {node.node_tree.name}")
                    # Print node group contents
                    print_node_tree(node.node_tree, indent + 4)
        
        print_node_tree(dome_mat.node_tree)

# Look for the Dome Vectors node group specifically
print("\n5. DOME VECTORS NODE GROUP ANALYSIS:")
print("-"*50)

for ng in data_to.node_groups:
    if 'Vector' in ng.name:
        print(f"\n  Node Group: {ng.name}")
        print(f"  Inputs: {[i.name for i in ng.inputs]}")
        print(f"  Outputs: {[o.name for o in ng.outputs]}")
        
        # Find the critical nodes
        for node in ng.nodes:
            if node.type == 'TEX_COORD':
                print(f"\n  TEX_COORD Node: {node.name}")
                print(f"    object: {node.object.name if node.object else 'None'}")
                for out in node.outputs:
                    if out.is_linked:
                        print(f"    {out.name} is linked")
            
            elif node.type == 'MAPPING':
                print(f"\n  MAPPING Node: {node.name}")
                for inp in node.inputs:
                    if inp.name in ['Location', 'Rotation', 'Scale']:
                        val = list(inp.default_value) if hasattr(inp.default_value, '__iter__') else inp.default_value
                        print(f"    {inp.name}: {val}")

# Check how sample addon creates the dome
print("\n6. CHECKING SAMPLE ADDON DOME CREATION CODE:")
print("-"*50)

dome_fc_path = r"e:\Projects\HDRI_editor\sample\hdri_maker\dome_tools\dome_fc.py"
if os.path.exists(dome_fc_path):
    with open(dome_fc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find relevant sections
    import re
    
    # Look for dome creation
    if 'dome_sky' in content.lower():
        print("  Found dome_sky references in dome_fc.py")
    
    # Look for material assignment
    mat_matches = re.findall(r'\.materials\[.*?\].*?=.*', content)
    for m in mat_matches[:5]:
        print(f"  Material assignment: {m.strip()}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
