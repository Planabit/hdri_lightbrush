"""
Analyze how the Dome Vectors node group calculates coordinates
Focus on understanding the TEX_COORD -> Environment Texture flow
"""

import bpy

dome_blend_path = r"e:\Projects\HDRI_editor\sample\hdri_maker\addon_resources\blendfiles\materials\HDRi_Maker_Dome.blend"

print("\n" + "="*70)
print("DOME VECTORS COORDINATE FLOW ANALYSIS")
print("="*70)

# Load node groups
with bpy.data.libraries.load(dome_blend_path, link=False) as (data_from, data_to):
    data_to.node_groups = data_from.node_groups[:]
    data_to.objects = data_from.objects[:]

# Find Dome Vectors
dome_vectors = None
for ng in bpy.data.node_groups:
    if ng.name == 'Dome Vectors':
        dome_vectors = ng
        break

if dome_vectors:
    print(f"\nDome Vectors Node Group:")
    print("-"*50)
    
    # Find TEX_COORD node and trace where its output goes
    tex_coord_node = None
    for node in dome_vectors.nodes:
        if node.type == 'TEX_COORD':
            tex_coord_node = node
            print(f"\nTEX_COORD node: {node.name}")
            print(f"  Object reference: {node.object.name if node.object else 'None'}")
            
            # Check which outputs are used
            for out in node.outputs:
                if out.is_linked:
                    print(f"  Output '{out.name}' is connected:")
                    for link in out.links:
                        print(f"    -> {link.to_node.name}.{link.to_socket.name}")
    
    # Find the Group Output and trace back what feeds into it
    print("\n\nTRACING OUTPUT PATH:")
    print("-"*50)
    
    for node in dome_vectors.nodes:
        if node.type == 'GROUP_OUTPUT':
            print(f"\nGroup Output node: {node.name}")
            for inp in node.inputs:
                if inp.is_linked:
                    print(f"  Input '{inp.name}' receives from:")
                    for link in inp.links:
                        print(f"    <- {link.from_node.name}.{link.from_socket.name}")
    
    # List all nodes with their connections
    print("\n\nALL NODE CONNECTIONS:")
    print("-"*50)
    
    for node in dome_vectors.nodes:
        if node.type in ['FRAME']:
            continue
        
        has_connections = False
        for out in node.outputs:
            if out.is_linked:
                has_connections = True
                break
        
        if has_connections:
            print(f"\n{node.name} ({node.type}):")
            for out in node.outputs:
                if out.is_linked:
                    for link in out.links:
                        print(f"  [{out.name}] -> {link.to_node.name}.[{link.to_socket.name}]")

# Check the dome object mesh
print("\n\n" + "="*70)
print("DOME OBJECT MESH ANALYSIS")
print("="*70)

dome_obj = None
for obj in bpy.data.objects:
    if obj.name == 'HDRi_Maker_Dome':
        dome_obj = obj
        break

if dome_obj and dome_obj.type == 'MESH':
    mesh = dome_obj.data
    print(f"\nMesh: {mesh.name}")
    print(f"  Vertices: {len(mesh.vertices)}")
    print(f"  Polygons: {len(mesh.polygons)}")
    
    print("\n  Vertex positions:")
    for i, v in enumerate(mesh.vertices):
        print(f"    v{i}: ({v.co.x:.2f}, {v.co.y:.2f}, {v.co.z:.2f})")
    
    print("\n  Face normals:")
    for i, p in enumerate(mesh.polygons):
        print(f"    f{i}: normal=({p.normal.x:.2f}, {p.normal.y:.2f}, {p.normal.z:.2f})")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
The sample dome is a CUBE (8 vertices, 6 faces), not a sphere!
The material's 'Dome Vectors' node group does the math to convert
the cube's Object coordinates into proper spherical HDRI coordinates.

Key insight: The TEX_COORD node uses "Object" output with a reference
object, and the node group transforms these coordinates mathematically
to create the spherical projection.
""")
