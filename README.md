avarabsp-blender-exporter
=========================

It makes that _thing_ into _JSON!_


Copy the `io_scene_avarabsp` folder into the blender `<version>/scripts/addons` folder. Then you can see the plugin in the addons list! Check the box to install it and use the `File -> Export...` menu option _!!_

This will export every separate mesh object as its own file with `_<Object Name>` appended to what you input. IE exporting a file `foo.avarabsp.json` with an object named `Cube`, you will get a file named `foo_Cube.avarabsp.json` and so on for every Mesh object in the scene.