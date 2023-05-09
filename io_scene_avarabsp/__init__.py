"""
avarabsp
"""
import bpy
import os
import re
import json
from bpy.props import StringProperty, CollectionProperty
from bpy.types import PropertyGroup
from bpy_extras.io_utils import ExportHelper, ImportHelper
from functools import reduce
from math import radians
from mathutils import Vector, Euler, Matrix
from .colour import Color

bl_info = {  # pylint: disable=invalid-name
    "name": "Avarabsp Import/Export",
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


class ImportAvarabsp(bpy.types.Operator, ImportHelper):
    """Import Avara BSP JSON as a blender object"""
    bl_idname = "import_avarabsp.json"
    bl_label = "Import from Avarabsp"

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})

    files: CollectionProperty(type=PropertyGroup)

    marker_colors = ["#fefefe", "#fe0000", "#0333ff", "#929292"]

    def execute(self, context):
        directory = os.path.dirname(self.filepath)
        for c, i in enumerate(self.files, start = 1):
            fn = os.path.join(directory, i.name)
            try:
                on = i.name.split(".")[0]
                self.import_json(fn, on)
                return {'FINISHED'}
            except:
                raise
                self.report({'ERROR'}, "failed")
                return {'CANCELLED'}
        

    def import_json(self, filepath, objectname):
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        verts = [Vector(p) for p in data['points']]
        colors = []
        for c_str in data["colors"]:
            if c_str[:6] == "marker":
                midx = int(c_str[7])
                c_str = self.marker_colors[midx]
            c = Color(c_str)
            colors.append(c)

        normals = [Vector(data['normals'][p['normal']]) for p in data['polys']]

        faces = []
        faces2inputpolys = []

        for pidx, poly in enumerate(data['polys']):
            for i in range(0, len(poly['tris']), 3):
                faces.append(poly['tris'][i:i + 3])
                faces2inputpolys.append(pidx)

        mesh = bpy.data.meshes.new(name="{} mesh".format(objectname))
        mesh.from_pydata(verts, [], faces)
        
        mesh.update()
        
        obj = bpy.data.objects.new(name="{}".format(objectname), object_data=mesh)
        rot = Euler(map(radians, (90, 0, 0)), "XYZ").to_matrix().to_4x4()
        obj.matrix_basis = Matrix() @ rot


        color_layer = obj.data.vertex_colors.new()

        for poly in obj.data.polygons:
            input_poly = faces2inputpolys[poly.index]
            #poly.normal = normals[input_poly]
            for loop_index in poly.loop_indices:
                loop = obj.data.loops[loop_index]
                #vidx = loop.vertex_index
                color = colors[data['polys'][input_poly]["color"]]
                c = list(color.rgb) 
                c.append(1.0)
                color_layer.data[loop_index].color = c
        
        bpy.context.scene.collection.objects.link(obj)


class ExportAvarabsp(bpy.types.Operator, ExportHelper):
    """Selection to Avara BSP JSON"""
    bl_idname = "export_avarabsp.json"
    bl_label = "Export to Avarabsp"
    bl_options = {"PRESET"}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})

    @property
    def check_extension(self):
        return True

    def execute(self, context):
        """Begin the export"""
        try:
            if not self.filepath:
                raise Exception("filepath not set")

            return self.savebsp(self.filepath, context)
        except:
            raise
            self.report({'ERROR'}, "failed")
            return {'CANCELLED'}
        
        
    def savebsp(self, filepath, context):
        savemode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode = 'OBJECT')

        for key, obj in bpy.data.objects.items():
            if obj.type == "MESH":
                # print(out)
                fn = re.sub(r'\/(\w+)\.json', f"/\g<1>_{obj.name}.json", filepath)

                print(f"writing {fn}")
                with open(fn, "w") as f:
                    json.dump(self.obj_to_json(key, obj), f)
            
        bpy.ops.object.mode_set(mode = savemode)
        return {'FINISHED'}
    
    def obj_to_json(self, key, obj):
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

        cattribs = 0
        if len(mesh.color_attributes) > 0:
            cattribs = mesh.color_attributes[0]

        norms = []
        colors = []
        polys = []

        #loop through the polygons
        for poly in mesh.polygons:
            # get the normal index
            n_idx = len(norms)
            norm = list(poly.normal)
            if poly.normal in norms:
                n_idx = norms.index(norm)
            else:
                norms.append(norm)
            # get a color from a single vertex
            # (it should only have one across an entire poly)
            a_vert_idx = poly.vertices[0]
            c_idx = 0
            if cattribs != 0:
                color = list(cattribs.data[a_vert_idx].color)
                c_idx = len(colors)
                if color in colors:
                    c_idx = colors.index(color)
                else:
                    colors.append(color)
            # tris will be added later
            polys.append({
                "back": 65535,
                "front": 65535,
                "color": c_idx,
                "normal": n_idx,
                "tris": []
            })
        # fill out the polys with triangles
        # these are indexes into the vertex list
        for t in mesh.loop_triangles:
            for vidx in t.vertices:
                polys[t.polygon_index]["tris"].append(vidx)

        if len(colors) < 1:
            colors.append("marker(0)")

        avarabsp = {
            'points': [list(p.co) for p in mesh.vertices], # vertex list
            'bounds': {
                'min': list(min_bound),
                'max': list(max_bound),
            },
            'center': list(centroid), 
            'radius1': min_bound.length,
            'radius2': (max_bound - min_bound).length / 2,
            'colors': colors,
            'normals': norms,
            'polys': polys,
        }
        return avarabsp
    

def menu_func_import(self, context):
    self.layout.operator(ImportAvarabsp.bl_idname, text="Avarabsp (.json)")

def menu_func_export(self, context):
    self.layout.operator(ExportAvarabsp.bl_idname, text="Avarabsp (.json)")

def register():
    """Add addon to blender"""
    bpy.utils.register_class(ExportAvarabsp)
    bpy.utils.register_class(ImportAvarabsp)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    """Remove addon from blender"""
    bpy.utils.unregister_class(ExportAvarabsp)
    bpy.utils.unregister_class(ImportAvarabsp)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
