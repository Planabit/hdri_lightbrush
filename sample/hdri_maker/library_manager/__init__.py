from ..library_manager.main_pcoll import register_main_previews_collection, unregister_main_previews_collection
from ..library_manager.textures_pcoll import register_texture_collections, unregister_texture_collections

def register_library_manager():
    register_texture_collections()
    register_main_previews_collection()


def unregister_library_manager():
    unregister_texture_collections()
    unregister_main_previews_collection()



