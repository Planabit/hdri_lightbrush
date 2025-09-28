bl_info = {"name": "HDRI Editor (Safe)", "version": (1, 0, 1), "blender": (4, 0, 0), "category": "3D View"}

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, FloatProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper

def get_hdri_preview_items(self, context):
    """Safe version of preview items function with extensive error handling"""
    items = []
    
    try:
        # Safely check if bpy.data.images exists
        if not hasattr(bpy.data, 'images'):
            return [("NONE", "No Images Available", "Blender not fully loaded", 'FILE_IMAGE', 0)]
        
        # Find all HDRI images in bpy.data.images
        for idx, img in enumerate(bpy.data.images):
            if not img:
                continue
                
            # Check if it's a valid image type
            try:
                if hasattr(img, 'type') and img.type == 'IMAGE':
                    if hasattr(img, 'source') and img.source in {'FILE', 'SEQUENCE'}:
                        # Skip Blender internal images
                        if img.name.startswith('Render Result') or img.name.startswith('Viewer Node'):
                            continue
                            
                        icon_id = 'FILE_IMAGE'  # Always use safe fallback icon
                        
                        display_name = img.name.replace('.hdr', '').replace('.exr', '').replace('.jpg', '').title()
                        
                        try:
                            description = f"Size: {img.size[0]}x{img.size[1]}" if img.size[0] > 0 else "HDRI Image"
                        except:
                            description = "HDRI Image"
                            
                        items.append((img.name, display_name, description, icon_id, idx))
                        
            except Exception as e:
                # Log error but continue processing other images
                print(f"Error processing image {getattr(img, 'name', 'unknown')}: {e}")
        
    except Exception as e:
        print(f"Error in get_hdri_preview_items: {e}")
        return [("ERROR", "Error Loading Images", str(e), 'ERROR', 0)]
    
    if not items:
        items.append(("NONE", "No HDRI Loaded", "Load an HDR image first", 'FILE_IMAGE', 0))
    
    return items

class HDRI_Properties(PropertyGroup):
    hdri_preview_enum: EnumProperty(
        name="HDRI Previews",
        description="Select HDRI for display",
        items=get_hdri_preview_items
    )

class HDRI_OT_load(Operator, ImportHelper):
    bl_idname = "hdri.load"
    bl_label = "Load HDRI"
    
    filename_ext = ".hdr"
    filter_glob: StringProperty(default="*.hdr;*.exr", options={"HIDDEN"})

    def execute(self, context):
        try:
            img = bpy.data.images.load(self.filepath)
            img.pack()
            context.scene.hdri_image = img
            
            # Set the enum to this image safely
            try:
                if hasattr(context.window_manager, 'hdri_properties'):
                    context.window_manager.hdri_properties.hdri_preview_enum = img.name
            except:
                pass  # Ignore enum setting errors
            
            # NO tag_redraw() call - this was causing the context error
            
            self.report({"INFO"}, f"Loaded HDRI: {img.name}")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to load HDRI: {str(e)}")
            return {"CANCELLED"}

class HDRI_OT_prev_image(Operator):
    bl_idname = "hdri.prev_image"
    bl_label = "Previous Image"

    def execute(self, context):
        try:
            props = context.window_manager.hdri_properties
            items = get_hdri_preview_items(props, context)
            
            if len(items) <= 1:
                return {"CANCELLED"}
            
            current = props.hdri_preview_enum
            current_idx = next((i for i, item in enumerate(items) if item[0] == current), 0)
            new_idx = (current_idx - 1) % len(items)
            props.hdri_preview_enum = items[new_idx][0]
            
            return {"FINISHED"}
        except Exception as e:
            print(f"Error in prev_image: {e}")
            return {"CANCELLED"}

class HDRI_OT_next_image(Operator):
    bl_idname = "hdri.next_image"
    bl_label = "Next Image"

    def execute(self, context):
        try:
            props = context.window_manager.hdri_properties
            items = get_hdri_preview_items(props, context)
            
            if len(items) <= 1:
                return {"CANCELLED"}
            
            current = props.hdri_preview_enum
            current_idx = next((i for i, item in enumerate(items) if item[0] == current), 0)
            new_idx = (current_idx + 1) % len(items)
            props.hdri_preview_enum = items[new_idx][0]
            
            return {"FINISHED"}
        except Exception as e:
            print(f"Error in next_image: {e}")
            return {"CANCELLED"}

class HDRI_PT_panel(Panel):
    bl_label = "HDRI Editor"
    bl_idname = "HDRI_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "HDRI Editor"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("hdri.load", text="Load HDRI", icon="FOLDER_REDIRECT")
        
        if hasattr(context.scene, 'hdri_image') and context.scene.hdri_image:
            img = context.scene.hdri_image
            
            box = layout.box()
            box.label(text=f"File: {img.name}", icon="IMAGE_DATA")
            if img.size[0] > 0:
                box.label(text=f"Size: {img.size[0]} x {img.size[1]}")
            
            if img.has_data:
                preview_box = layout.box()
                preview_box.label(text="HDR Image Display:", icon="IMAGE_DATA")
                
                try:
                    hdri_props = context.window_manager.hdri_properties
                    
                    arrows_row = preview_box.row(align=True)
                    
                    left_arrow = arrows_row.row(align=True)
                    left_arrow.scale_y = 6.0
                    left_arrow.operator("hdri.prev_image", text="", icon='TRIA_LEFT_BAR')
                    
                    preview_row = arrows_row.row(align=True)
                    preview_row.scale_y = 8.0
                    preview_row.template_icon_view(
                        context.window_manager.hdri_properties, "hdri_preview_enum",
                        show_labels=True,
                        scale=8.0,
                        scale_popup=10.0
                    )
                    
                    right_arrow = arrows_row.row(align=True)
                    right_arrow.scale_y = 6.0
                    right_arrow.operator("hdri.next_image", text="", icon='TRIA_RIGHT_BAR')
                    
                except Exception as e:
                    preview_box.label(text=f"Preview Error: {str(e)}", icon='ERROR')

def register():
    bpy.utils.register_class(HDRI_Properties)
    bpy.utils.register_class(HDRI_OT_load)
    bpy.utils.register_class(HDRI_OT_prev_image)
    bpy.utils.register_class(HDRI_OT_next_image)
    bpy.utils.register_class(HDRI_PT_panel)
    
    bpy.types.Scene.hdri_image = bpy.props.PointerProperty(type=bpy.types.Image)
    bpy.types.WindowManager.hdri_properties = bpy.props.PointerProperty(type=HDRI_Properties)

def unregister():
    del bpy.types.WindowManager.hdri_properties
    del bpy.types.Scene.hdri_image
    
    bpy.utils.unregister_class(HDRI_PT_panel)
    bpy.utils.unregister_class(HDRI_OT_next_image)
    bpy.utils.unregister_class(HDRI_OT_prev_image)
    bpy.utils.unregister_class(HDRI_OT_load)
    bpy.utils.unregister_class(HDRI_Properties)

if __name__ == "__main__":
    register()