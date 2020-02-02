"""
avarabsp
"""

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper
from . import export_avarabsp

bl_info = {  # pylint: disable=invalid-name
    "name": "Avarabsp Exporter",
    "author": "Andy Halstead (@assertivist)",
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": ("Export all geometry as an avarabsp json file"),
    "warning": "",
    "wiki_url": ("https://github.com/assertivist/avarabsp-blender-exporter"),
    "tracker_url": "https://github.com/assertivist/avarabsp-blender-exporter",
    "support": "COMMUNITY",
    "category": "Import-Export"
}


class ExportAvarabsp(bpy.types.Operator, ExportHelper):
    """Selection to Godot"""
    bl_idname = "export_avarabsp.json"
    bl_label = "Export to Avarabsp"
    bl_options = {"PRESET"}

    filename_ext = ".avarabsp.json"
    filter_glob: StringProperty(default="*.avarabsp.json", options={"HIDDEN"})

    @property
    def check_extension(self):
        return True

    def execute(self, context):
        """Begin the export"""
        try:
            if not self.filepath:
                raise Exception("filepath not set")

            return export_avarabsp.save(self, context)
        except:
            self.report({'ERROR'}, "failed")
            return {'CANCELLED'}


def menu_func(self, context):
    """Add to the menu"""
    self.layout.operator(ExportAvarabsp.bl_idname, text="Avarabsp (.avarabsp.json)")


def register():
    """Add addon to blender"""
    bpy.utils.register_class(ExportAvarabsp)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)


def unregister():
    """Remove addon from blender"""
    bpy.utils.unregister_class(ExportAvarabsp)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()