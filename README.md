# python-polygon
Expansion of the Chakin Algorithm to the 3rd dimension.

## Installation

You need to have python (version 3+) and pip installed.

Then, download the repo:
```
git clone https://github.com/Nicolas-Reyland/Chaikin3D
```

Then you will need *plotly* and *matrix*. You can install plotly with pip:
```
pip install plotly
```
To install matrix, you need to get it from [my repo](https://github.com/Nicolas-Reyland/matrix). You can simply add the matrix.py file in this project's folder, but you can also install matrix.

If you wish to only use matrix for this project (which is very likely), please enter these commands:
```
cd Chaikin3D
git clone https://github.com/Nicolas-Reyland/matrix
cp matrix/matrix.py .
```

If you are using Windows, download the matrix repo (https://github.com/Nicolas-Reyland/matrix) and copy the matrix.py file into the Chaikin3D folder.


## Some explanations first

This project supports more "exotic" polygon types. In fact, since we are going to change the polygon, raw data of the verticies isn't sufficient. We need info about which edges are important, and which are not. For example, in a cube, the diagonal edge (to split the square into two triangles) is not "important": its purpose is only to bind two vertices so that triangle can be drawn to the screen. That's why we need to distinguish *main* and *graphical* connections between our nodes (vertices).

That is why the polygonal approximation of meshes that were loaded from *.obj* files are not perfect. There is no way for me to know if a connection between two nodes is really a part of the mesh or if its only purpose is to form triangles (you can normally only draw triangles).

For examples of what I mean with "graphical" connections, try these commands: ```python3 chaikin3d.py -s cube -p full -c 0``` and ```python3 chaikin3d.py -s cube -p full -c 1```. The grapchical connections are the black lines, while the main connections are the red lines.


## Usage
Not that you can use the ```python3 chaikin3d.py -h``` command.

You will first have to select a polygon/mesh to render or use. There are two options: you can load a *.obj* file using the ```-i``` (```--input```) option and appending the path like this:
```python3 chaikin3d.py -i data/dog.obj``` (if you try this and the mesh is rotated, please add this: ```-rm true``` option).
You can also use the ```-s``` (```--shape```) option to load a predefined polygon. They are defined in the *basic_shapes.py* file. You can define your own polygons in there. You can, for example, use ```python3 chaikin3d.py -s cube``` or ```python3 chaikin3d.py -s triangle```. If you wish to add your own shapes, please take a look at the file and add your own! You only need to create a function which returns a *polygon.Polygon* object and append it's name after the ```-s``` option to load it.
If you only load a polygon, it will simply be drawn.


Then, you can choose the number of Chaikin generations (or iterations) you want to run on the given polygon. That is done using the ```-c``` (```--chakin```) option. The default value is 0. To run one iteration, you could use ```python3 chaikin3d.py -s triangle -c 1```.

You can now choose how you'd like to draw your mesh and what exactly you'd like to draw. This is done using the folloying options:
 * ```-p``` or ```--plot```
 * ```-a``` or ```--alpha```
 * ```-r``` or ```--renderer``` (PLEASE DO NOT USE YET)
 * ```-smc``` or ```--show-main-connections```
 * ```-sgc``` or ```--show-graphical-connections```
 * ```-rm``` or ```--rotate-mesh``` (only with the ```-i``` option)


