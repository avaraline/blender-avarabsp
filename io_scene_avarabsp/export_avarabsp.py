import bpy

def save(blenderop, context):
    fn = blenderop.filename

    #print(dir(context.scene))
    #print("======================")
    #print(dir(context.object))
    #print("======================")
    #print(dir(context.object.data))
    print(fn)
    print(context.object.data.vertices.items())

    for key, value in bpy.data.meshes.items():
        print(f"export the {key}")
        for v in value.vertices:
            print(v.co)
            print(v.normal)


    return {'FINISHED'}
