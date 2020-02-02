"""
avarabsp
"""
import math
import bpy
import re
import json
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper
from functools import reduce
from mathutils import Vector

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

            return save(self.filepath, context)
        except:
            raise
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


def save(filepath, context):

    for key, obj in bpy.data.objects.items():
        if obj.type == "MESH":
            # print(out)
            fn = re.sub(r'\/(\w+)\.avarabsp\.json', f"/\g<1>_{obj.name}.avarabsp.json", filepath)

            print(f"writing {fn}")
            with open(fn, "w") as f:
                json.dump(obj_to_json(key, obj), f)

    return {'FINISHED'}

def obj_to_json(key, obj):
    print(f"export the {key}")
    bounds = [Vector(list(x)) for x in list(obj.bound_box)]
    # print(f"bbox: {bounds}")
    min_bound = reduce(lambda x,y: x if sum(map(lambda v: v[0] < v[1], zip(x, y))) else y, bounds)
    # print(f"min_bound: {min_bound}")
    max_bound = reduce(lambda x,y: x if sum(map(lambda v: v[0] > v[1], zip(x, y)))  else y, bounds)
    # print(f"max_bound: {max_bound}")

    centroid = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    # print(f"centroid: {centroid}")
    mesh = obj.to_mesh()
    # we need the triangles
    mesh.calc_loop_triangles()
    tris = list(mesh.loop_triangles)
    points = []
    for v in mesh.vertices:
        points.append(v.co)

    colors = []
    if mesh.vertex_colors.active is None:
        print("I cannot find the vertex colors. You get white")
        colors = [[1, 1, 1, 1] for x in range(0, len(tris))]
    else:
        colors = mesh.vertex_colors.active.data

    polys = [poly_record(p, tris, colors) for p in mesh.polygons]

    return {
        'points': [list(p) for p in points],
        'bounds': {
            'min': list(min_bound),
            'max': list(max_bound),
        },
        'center': list(centroid),
        'radius1': 1.0,
        'radius2': (max_bound - min_bound).length / 2,
        'polys': polys,
    }

def poly_record(p, tris, colors):
    start = p.loop_start
    end = p.loop_start + p.loop_total
    poly_tris = [x for x in tris if x.polygon_index == p.index]
    color = [math.floor(x * 255) for x in list(colors[p.loop_start].color)]
    rgb = ((color[0] & 0x0ff) << 16) | ((color[1] & 0x0ff) << 8) | (color[2] & 0x0ff)
    return {
        "color": rgb,
        "normal": list(p.normal),
        "tris": [list(t.vertices) for t in poly_tris]
    }

if __name__ == "__main__":
    register()