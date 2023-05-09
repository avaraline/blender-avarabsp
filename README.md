avarabsp-blender-exporter
=========================

It makes that _thing_ into _JSON!_ This is an importer/exporter for Avara JSON BSPs. We use a format adapted from the original resource fork geometry data used in the original game. This Blender plugin allows you to make a scene with all of your custom Avara shapes and export them to a format that can be included alongside level sets and used in the game.


Copy the `io_scene_avarabsp` folder into the Blender `<version>/scripts/addons` folder. Then you can see the plugin in the addons list! Check the box to install it and use the `File -> Export...` and `File -> Import...` menu options _!!_

Exports
=======
A separate file with `_<Object Name>` appended to what you input is written for each object in the scene. IE exporting a file `foo.avarabsp.json` with an object named `Cube`, you will get a file named `foo_Cube.avarabsp.json` and so on for every Mesh object in the scene. Keep in mind that Blender is "Z-up" and Avara is "Y-up", so the +Y direction will become the "top" of your model in Avara.

It will attempt to export vertex colors, but more than one color in a single polygon/set of triangles sharing a normal/face are not supported. 

You take these files and put them in the `bsps` directory of your Avara level. Then you can add them to the `BSPT` section of your `set.json` file. This is where you map the file to a numeric ID that you can refer to in an ALF file.


Imports
=======
For imports, the plugin will create an object named `filename` (minus the `.json`) with the mesh data (including vertex colors) from the JSON file that was input. The plugin will automatically rotate the imported geometry from "Y-up" to "Z-up" used by Blender (by rotating it along the X axis by 90 degrees). 

Vertex colors will not appear in the normal 3D viewport "Object View", you must select the "Texture Painting" tab and then switch the right viewport to "Vertex Paint" mode with an object selected in order to preview the vertex colors. You can also update the colors via the Vertex Paint feature, but keep in mind that the only one color per face is supported in Avara.