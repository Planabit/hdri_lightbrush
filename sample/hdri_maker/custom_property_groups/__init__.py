#  #
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version
#   of the License, or (at your option) any later version.
#  #
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#  #
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#  #
#  Copyright 2024(C) Andrea Donati
import bpy
from bpy.props import PointerProperty
from bpy.types import Scene, Object, Material, World, Image, Node, Texture, NodeTree, Brush, Collection, Mesh

if bpy.app.version < (4, 0, 0):
    from bpy.types import NodeSocketInterface
else:
    from bpy.types import NodeTreeInterfaceSocket

from .brush.brush_props import HdriMakerBrushProperties
from .collection.collection import HdirMakerCollection
from .image.image_props import HdirMakerImageProperty
from .material.material_props import HdriMakerMaterialProperty
from .mesh.mesh import HdriMakerMeshProperty
from .node.node_props import HdriMakerNodeProperty
from .node_tree.node_tree_props import HdriMakerNodeTreeProperties
from .object.objects_props import HdriMakerObjectProperty
from .scene.scene_props import HdriMakerSceneProperty
from .socket.socket_callback import HdriMakerEnumSocketInt
from .socket.socket_props import HdriMakerSocketProperties, HdriMakerRandomSocketProperties
from .texture.texture_props import HdriMakerTextureProperty
from .world.world_props import HdriMakerWorldProperty


def register_custom_property_groups():
    Scene.hdri_prop_scn = PointerProperty(type=HdriMakerSceneProperty, options={'HIDDEN'},
                                          name="HDRi Maker Scene Properties")
    Object.hdri_prop_obj = PointerProperty(type=HdriMakerObjectProperty, options={'HIDDEN'},
                                           name="HDRi Maker Object Properties")
    Material.hdri_prop_mat = PointerProperty(type=HdriMakerMaterialProperty, options={'HIDDEN'},
                                             name="HDRi Maker Material Properties")
    World.hdri_prop_world = PointerProperty(type=HdriMakerWorldProperty, options={'HIDDEN'},
                                            name="HDRi Maker World Properties")
    Image.hdri_prop_image = PointerProperty(type=HdirMakerImageProperty, options={'HIDDEN'},
                                            name="HDRi Maker Image Properties")
    Node.hdri_prop_nodes = PointerProperty(type=HdriMakerNodeProperty, options={'HIDDEN'},
                                           name="HDRi Maker Node Properties")
    Texture.hdri_prop_texture = PointerProperty(type=HdriMakerTextureProperty, options={'HIDDEN'},
                                                name="HDRi Maker Texture Properties")
    NodeTree.hdri_prop_nodetree = PointerProperty(type=HdriMakerNodeTreeProperties, options={'HIDDEN'},
                                                  name="HDRi Maker Node Tree Properties")
    Brush.hdri_prop_brush = PointerProperty(type=HdriMakerBrushProperties, options={'HIDDEN'},
                                            name="HDRi Maker Brush Properties")
    if bpy.app.version < (4, 0, 0):
        NodeSocketInterface.hdri_prop_socket = PointerProperty(type=HdriMakerRandomSocketProperties, options={'HIDDEN'},
                                                               name="HDRi Maker Socket Properties")
        NodeSocketInterface.hdri_prop_socket = PointerProperty(type=HdriMakerSocketProperties, options={'HIDDEN'},
                                                               name="HDRi Maker Socket Properties")
    else:
        NodeTreeInterfaceSocket.hdri_prop_socket = PointerProperty(type=HdriMakerRandomSocketProperties,
                                                                   options={'HIDDEN'},
                                                                   name="HDRi Maker Socket Properties")
        NodeTreeInterfaceSocket.hdri_prop_socket = PointerProperty(type=HdriMakerSocketProperties, options={'HIDDEN'},
                                                                   name="HDRi Maker Socket Properties")

    Collection.hdri_prop_collection = PointerProperty(type=HdirMakerCollection, options={'HIDDEN'},
                                                      name="HDRi Maker Collection Properties")
    Mesh.hdri_prop_mesh = PointerProperty(type=HdriMakerMeshProperty, options={'HIDDEN'},
                                          name="HDRi Maker Mesh Properties")


custom_property_groups_classes = [HdriMakerSceneProperty,
                                  HdriMakerObjectProperty,
                                  HdriMakerMaterialProperty,
                                  HdriMakerWorldProperty,
                                  HdirMakerImageProperty,
                                  HdriMakerNodeProperty,
                                  HdriMakerTextureProperty,
                                  HdriMakerNodeTreeProperties,
                                  HdriMakerBrushProperties,
                                  HdriMakerEnumSocketInt,
                                  HdriMakerRandomSocketProperties,
                                  HdriMakerSocketProperties,
                                  HdirMakerCollection,
                                  HdriMakerMeshProperty]
