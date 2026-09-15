"""Original Blender set: small wooden bridge, stream, trees, warm lanterns."""
import bpy, math, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
random.seed(19)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,metal=0,rough=.7,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission:
  if 'Emission Color' in p.inputs:p.inputs['Emission Color'].default_value=(*color,1)
  else:p.inputs['Emission'].default_value=(*color,1)
  p.inputs['Emission Strength'].default_value=emission
 return m
wood=mat('Honey oak',(.31,.16,.075));stone=mat('Sandstone',(.44,.37,.28));grass=mat('Moss',(.12,.22,.19));water=mat('Teal water',(.025,.18,.22),.65,.18);leaf=mat('Sage foliage',(.19,.32,.25));gold=mat('Lantern glow',(1,.55,.15),emission=4)
def cube(name,loc,scale,m,bevel=.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def sphere(loc,scale,m):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=loc);o=bpy.context.object;o.scale=scale;o.data.materials.append(m);return o
cube('River',(0,0,-.18),(6,70,.3),water)
for x in [-11,11]:cube('Bank',(x,0,-.5),(16,70,1),grass)
for i in range(22):
 x=-4.8+i*.46;z=.4+.4*math.cos(x/5*math.pi/2)
 cube('Bridge plank',(x,2,z),(.43,3,.2),wood,.04)
 for y in [.5,3.5]:
  if i%3==0:cube('Railing post',(x,y,z+.8),(.16,.16,1.8),wood,.025)
for y in [.5,3.5]:cube('Top rail',(0,y,1.75),(10.4,.13,.16),wood,.025)
for i in range(18):
 x=random.choice([-1,1])*random.uniform(5.8,16);y=random.uniform(6,25)
 cube('Tree trunk',(x,y,1.8),(.45,.45,4),wood)
 for j in range(3):sphere((x+random.uniform(-.7,.7),y,3.7+j*.7),(1.5,1.4,1.4),leaf)
for x in [-5.7,5.7]:
 cube('Lantern pillar',(x,.2,1),( .5,.5,2),stone)
 cube('Lantern',(x,.2,2.2),(.45,.45,.6),gold)
 bpy.ops.object.light_add(type='POINT',location=(x,.2,2.6));bpy.context.object.data.energy=100;bpy.context.object.data.color=(1,.5,.2)
# Low hills make a complete horizon.
for x in range(-30,31,6):sphere((x,32,1),(7,7,4),grass)
bpy.ops.object.light_add(type='AREA',location=(-5,-6,12));bpy.context.object.data.energy=1800;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=10;bpy.context.object.data.color=(1,.76,.51)
bpy.ops.object.light_add(type='AREA',location=(7,10,9));bpy.context.object.data.energy=1200;bpy.context.object.data.size=12;bpy.context.object.data.color=(.42,.64,1)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.14,.19,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.ops.object.camera_add();cam=bpy.context.object;bpy.context.scene.camera=cam;cam.data.lens=42
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for i,pos in enumerate([(11,-16,9),(5,-11,5.5),(-10,-13,7)]):
 cam.location=pos;cam.rotation_euler=(Vector((0,2,1.5))-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(ROOT/'public'/f'background_{i}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output'/'bridge.blend'))
