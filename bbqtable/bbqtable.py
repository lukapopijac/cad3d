import FreeCAD
from FreeCAD import Base, Vector
import Part
from math import pi, sin, cos


def setview():
	FreeCAD.Gui.SendMsgToActiveView('ViewFit')
	FreeCAD.Gui.activeDocument().activeView().viewAxometric()
	Gui.runCommand('Std_OrthographicCamera',0)
	Gui.runCommand('Std_PerspectiveCamera',1)


def createBox(doc, name, lwh, position):
	obj = doc.addObject('Part::Box', name)
	obj.Length = lwh[0]
	obj.Width = lwh[1]
	obj.Height = lwh[2]
	obj.Placement.Base = position
	return obj


def createShelfBase(doc, name, length, width, d1, d4):
	base_F = createBox(doc, name+'_F', (length - 2*d1, d1, d4), (-length/2 + d1, -width/2, -d4))
	base_B = createBox(doc, name+'_B', (length - 2*d1, d1, d4), (-length/2 + d1, width/2 - d1, -d4))
	base_L = createBox(doc, name+'_L', (d1, width, d4), (-length/2, -width/2, -d4))
	base_R = createBox(doc, name+'_R', (d1, width, d4), (length/2 - d1, -width/2, -d4))
	obj_fuse1 = fuse(doc, name+'fuse_1', base_F, base_L)
	obj_fuse2 = fuse(doc, name+'fuse_2', obj_fuse1, base_B)
	obj_fuse3 = fuse(doc, name, obj_fuse2, base_R)
	return obj_fuse3

hejneShelfProps = {
	'length': 770,
	'width': 471,
	'support_width': 33,
	'plank_thick': 15
}


def createHejneShelf(doc, name):
	length = hejneShelfProps['length']
	width = hejneShelfProps['width']
	support_width = hejneShelfProps['support_width']
	plank_thick = hejneShelfProps['plank_thick']

	support_full   = createBox(doc, name+'_support_full',   (support_width, width, 32), (-length/2, -width/2, -32))
	support_cutoff = createBox(doc, name+'_support_cutoff', (22, width, plank_thick), (-length/2 + 11, -width/2, -plank_thick))
	support = doc.addObject('Part::Cut', name+'_support')
	support.Base = support_full
	support.Tool = support_cutoff

	support_L = support
	support_R = doc.copyObject(support, False)
	support_R.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 180)

	plank_width = 70
	d = (width - 2*7 - 5*plank_width) / 4   # distance between planks

	plank1 = createBox(doc, name+'_plank001', (length-2*11, plank_width, plank_thick), (-length/2 + 11, -width/2 + 7, -15))

	plank2 = doc.copyObject(plank1, False)
	plank2.Placement.Base = plank1.Placement.Base + FreeCAD.Vector(0, plank_width + d, 0)

	plank3 = doc.copyObject(plank2, False)
	plank3.Placement.Base = plank2.Placement.Base + FreeCAD.Vector(0, plank_width + d, 0)

	plank4 = doc.copyObject(plank3, False)
	plank4.Placement.Base = plank3.Placement.Base + FreeCAD.Vector(0, plank_width + d, 0)

	plank5 = doc.copyObject(plank4, False)
	plank5.Placement.Base = plank4.Placement.Base + FreeCAD.Vector(0, plank_width + d, 0)

	return fuseAll(doc, name, [support_L, support_R, plank1, plank2, plank3, plank4, plank5])


def fuse(doc, name, obj1, obj2):
	obj = doc.addObject('Part::Fuse', name)
	obj.Base = obj1
	obj.Tool = obj2
	#obj1.Visibility=False
	#obj2.Visibility=False
	return obj

def fuseAll(doc, name, objs):
	prev_fuse = objs[0]
	for i in range(1, len(objs)):
		curr_fuse = doc.addObject('Part::Fuse', name)
		curr_fuse.Base = prev_fuse
		curr_fuse.Tool = objs[i]
		prev_fuse = curr_fuse
	return prev_fuse

		
	

def setTransparency(doc, tr):
	for obj in doc.Objects:
		obj.ViewObject.Transparency = tr


def main():
	print('-----------')
	doc_name = 'bbqtable'

	d1, d2, d3, d4, d6, d8 = 19, 38, 63.5, 89, 140, 184

	shelf_length        = hejneShelfProps['length']
	shelf_width         = hejneShelfProps['width']
	shelf_support_width = hejneShelfProps['support_width']
	shelf_plank_thick   = hejneShelfProps['plank_thick']

	length = shelf_length + 6
	width = shelf_width + 2*d1
	height = 800

	try:    doc = FreeCAD.getDocument(doc_name)
	except: doc = FreeCAD.newDocument(doc_name)

	FreeCAD.setActiveDocument(doc_name)

	# remove objects
	for obj in doc.Objects:
		doc.removeObject(obj.Name)


	let_FL = createBox(doc, 'let_FL', (d4, d1, height), (-length/2     , -width/2     , 0))
	let_FR = createBox(doc, 'let_FR', (d4, d1, height), ( length/2 - d4, -width/2     , 0))
	let_BL = createBox(doc, 'let_BL', (d4, d1, height), (-length/2     ,  width/2 - d1, 0))
	let_BR = createBox(doc, 'let_BR', (d4, d1, height), ( length/2 - d4,  width/2 - d1, 0))


	shelf_base_top = createShelfBase(doc, 'shelf_base_top', shelf_length - 2*shelf_support_width, shelf_width, d1, d4)
	shelf_base_top.Placement.Base = (0, 0, height - shelf_plank_thick)
	shelf_top = createHejneShelf(doc, 'shelf_top')
	shelf_top.Placement.Base = (0, 0, height)


	shelf_base_bottom = createShelfBase(doc, 'shelf_base_bottom', shelf_length - 2*shelf_support_width, shelf_width, d1, d4)
	shelf_base_bottom.Placement.Base = (0, 0, 300 - shelf_plank_thick)
	shelf_bottom = createHejneShelf(doc, 'shelf_bottom')
	shelf_bottom.Placement.Base = (0, 0, 300)


	#shelf_base_middle = createShelfBase(doc, 'shelf_base_middle', shelf_length - 2*shelf_support_width, shelf_width, d1, d4)
	#shelf_base_middle.Placement.Base = (0, 0, 500 - shelf_plank_thick)
	#shelf_middle = createHejneShelf(doc, 'shelf_middle')
	#shelf_middle.Placement.Base = (0, 0, 500)

	
	doc.recompute()
	#setTransparency(doc, 20)
	setview()


main()
