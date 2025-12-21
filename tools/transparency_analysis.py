"""
Deep analysis of sample dome TRANSPARENCY and rendering settings
"""

import bpy

dome_blend_path = r"e:\Projects\HDRI_editor\sample\hdri_maker\addon_resources\blendfiles\materials\HDRi_Maker_Dome.blend"

print("\n" + "="*70)
print("SAMPLE DOME TRANSPARENCY ANALYSIS")
print("="*70)

# Load everything
with bpy.data.libraries.load(dome_blend_path, link=False) as (data_from, data_to):
    data_to.materials = data_from.materials[:]
    data_to.node_groups = data_from.node_groups[:]
    data_to.objects = data_from.objects[:]

# Find the dome material
dome_mat = None
for mat in data_to.materials:
    if 'Dome' in mat.name:
        dome_mat = mat
        break

if dome_mat:
    print(f"\n1. MATERIAL SETTINGS:")
    print("-"*50)
    print(f"  Name: {dome_mat.name}")
    print(f"  Blend Method: {dome_mat.blend_method}")
    print(f"  Shadow Method: {dome_mat.shadow_method}")
    print(f"  Backface Culling: {dome_mat.use_backface_culling}")
    print(f"  Show Transparent Back: {dome_mat.show_transparent_back}")
    print(f"  Use Screen Refraction: {dome_mat.use_screen_refraction}")
    print(f"  Alpha Threshold: {dome_mat.alpha_threshold}")
    
    # Check viewport display settings
    print(f"\n2. VIEWPORT DISPLAY:")
    print("-"*50)
    print(f"  Roughness: {dome_mat.roughness}")
    print(f"  Metallic: {dome_mat.metallic}")
    
    # Analyze node tree for transparency-related nodes
    print(f"\n3. TRANSPARENCY-RELATED NODES:")
    print("-"*50)
    
    def find_transparency_nodes(node_tree, prefix=""):
        for node in node_tree.nodes:
            if node.type in ['BSDF_TRANSPARENT', 'MIX_SHADER', 'HOLDOUT', 'EMISSION']:
                print(f"{prefix}[{node.type}] {node.name}")
                # Show inputs
                for inp in node.inputs:
                    if inp.is_linked:
                        for link in inp.links:
                            print(f"{prefix}  <- {inp.name} from {link.from_node.name}")
                    elif hasattr(inp, 'default_value'):
                        try:
                            val = list(inp.default_value) if hasattr(inp.default_value, '__iter__') else inp.default_value
                            if inp.name in ['Fac', 'Strength', 'Factor']:
                                print(f"{prefix}  {inp.name} = {val}")
                        except:
                            pass
            
            # Check node groups
            if node.type == 'GROUP' and node.node_tree:
                print(f"{prefix}[GROUP] {node.name} -> {node.node_tree.name}")
                find_transparency_nodes(node.node_tree, prefix + "    ")
    
    find_transparency_nodes(dome_mat.node_tree)
    
    # Look at what connects to Material Output
    print(f"\n4. MATERIAL OUTPUT CONNECTIONS:")
    print("-"*50)
    
    for node in dome_mat.node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL':
            for inp in node.inputs:
                if inp.is_linked:
                    for link in inp.links:
                        print(f"  {inp.name} <- {link.from_node.name}.{link.from_socket.name}")

# Check the Dome Color node group specifically
print(f"\n5. DOME COLOR NODE GROUP (contains transparency):")
print("-"*50)

for ng in bpy.data.node_groups:
    if ng.name == 'Dome Color':
        print(f"  Node Group: {ng.name}")
        
        # Find the output and trace back
        for node in ng.nodes:
            if node.type == 'GROUP_OUTPUT':
                print(f"\n  Group Output connections:")
                for inp in node.inputs:
                    if inp.is_linked:
                        for link in inp.links:
                            print(f"    {inp.name} <- {link.from_node.name}")
        
        # Find Mix Shader and Transparent nodes
        for node in ng.nodes:
            if node.type == 'MIX_SHADER':
                print(f"\n  MIX_SHADER: {node.name}")
                for inp in node.inputs:
                    if inp.is_linked:
                        for link in inp.links:
                            print(f"    {inp.name} <- {link.from_node.name}")
                    elif inp.name == 'Fac':
                        print(f"    Fac = {inp.default_value}")
            
            elif node.type == 'BSDF_TRANSPARENT':
                print(f"\n  TRANSPARENT BSDF: {node.name}")
            
            elif node.type == 'NEW_GEOMETRY':
                print(f"\n  GEOMETRY NODE: {node.name}")
                for out in node.outputs:
                    if out.is_linked:
                        print(f"    {out.name} -> connected")

# Check object settings
print(f"\n6. OBJECT SETTINGS:")
print("-"*50)

for obj in data_to.objects:
    print(f"\n  Object: {obj.name}")
    print(f"    Display Type: {obj.display_type}")
    print(f"    Show In Front: {obj.show_in_front}")
    print(f"    Hide Render: {obj.hide_render}")
    
    # Check object visibility
    if hasattr(obj, 'visible_camera'):
        print(f"    Visible Camera: {obj.visible_camera}")
    if hasattr(obj, 'visible_diffuse'):
        print(f"    Visible Diffuse: {obj.visible_diffuse}")
    
    # Ray visibility
    if obj.type == 'MESH':
        cycles_vis = obj.cycles_visibility if hasattr(obj, 'cycles_visibility') else None
        if cycles_vis:
            print(f"    Cycles Visibility:")
            print(f"      Camera: {cycles_vis.camera}")
            print(f"      Diffuse: {cycles_vis.diffuse}")
            print(f"      Glossy: {cycles_vis.glossy}")

print("\n" + "="*70)
print("KEY FINDINGS")
print("="*70)
