import FreeCAD
from FreeCAD import Vector, Rotation
import Part
from math import pi, sin, cos, tan, asin, atan


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


def cut(doc, name, obj1, obj2):
	obj = doc.addObject('Part::Cut', name)
	obj.Base = obj1
	obj.Tool = obj2
	#obj1.Visibility=False
	#obj2.Visibility=False
	return obj


def legAngle(width, height, offset, frame_cutoff):
	# phi is angle if it was rotating around y axis (0, 1, 0)
	# solve for phi:
	# tan(phi)*(height-frame_cutoff) = offset - width/(cos(phi))
	a = offset
	b = height - frame_cutoff
	w = width
	# => b*sin(phi) = a*cos(phi) - w

	A = a*a + b*b
	B = 2*b*w
	C = w*w - a*a
	D = B*B - 4*A*C
	sin_phi = (-B + D**.5)/(2*A)
	phi = asin(sin_phi)
	
	# real angle is for rotating around vector (-1, 1, 0)
	alpha = atan(tan(phi)*2**.5)

	# add small percentage for good measure (numerical error)
	return alpha*1.006
	

def createLeg(doc, name, width, height, offset, frame_cutoff):
	stick = createBox(doc, name + '_stick', (width, width, height*2), (0, 0, 0))

	angle = legAngle(width, height, offset, frame_cutoff)
	stick.Placement.Rotation = Rotation(Vector(-1, 1, 0), angle * 180/pi)

	cut_bottom = createBox(doc, name + '_cut_bottom', (2*width, 2*width, 2*width), (-width/4, -width/4, -2*width))
	cut1 = cut(doc, name + '_cut1', stick, cut_bottom)

	cut_top = createBox(doc, name + '_cut_top',
		(7*width, 7*width, height + 1), 
		(offset - 3*width, offset - 3*width, height)
	)
	# cut2 = cut(doc, name + '_cut2', cut1, cut_top)
	return cut(doc, name, cut1, cut_top)

	"""
	cut_x = createBox(doc, name + '_cut_x',
		(4*width, 7*width, frame_cutoff + 3*width),
		(offset, offset - 3*width, height - frame_cutoff - 3*width + 1)
	)
	cut3 = cut(doc, name + '_cut3', cut2, cut_x)

	cut_y = createBox(doc, name + '_cut_y',
		(7*width, 4*width, frame_cutoff + 3*width),
		(offset - 3*width, offset, height - frame_cutoff - 3*width + 1)
	)
	cut4 = cut(doc, name, cut3, cut_y)

	return cut2
	"""

def createFrameSide(doc, name, lwh, position, cut1, cut2):
	base = createBox(doc, name + '_base', lwh, position)
	cut1_copy = doc.copyObject(cut1, False)
	cut1 = cut(doc, name + '_cut1', base, cut1_copy)
	cut2_copy = doc.copyObject(cut2, False)
	cut2 = cut(doc, name, cut1, cut2_copy)
	return cut2


def setTransparency(doc, tr):
	for obj in doc.Objects:
		obj.ViewObject.Transparency = tr


def main():
	print('-----------')
	doc_name = 'stool2'

	d1, d2, d3, d4, d6, d8 = 19, 38, 63.5, 89, 140, 184
	total_height = 280
	sit_length, sit_width, sit_height = 305, 235, d1
	leg_width = 27
	frame_width, frame_height = d1, d2
	frame_offset = 43.5

	try:    doc = FreeCAD.getDocument(doc_name)
	except: doc = FreeCAD.newDocument(doc_name)

	FreeCAD.setActiveDocument(doc_name)

	# remove objects
	for obj in doc.Objects:
		doc.removeObject(obj.Name)


	######  legs  ######
	createLeg_params = [leg_width, total_height - sit_height, frame_offset + frame_width, frame_height]

	leg_FL = createLeg(doc, 'leg_FL', *createLeg_params)
	leg_FL.Placement.Base = (-sit_length/2, -sit_width/2, 0)

	leg_FR = createLeg(doc, 'leg_FR', *createLeg_params)
	leg_FR.Placement.Rotation = Rotation(Vector(0, 0, 1), 90)
	leg_FR.Placement.Base = (sit_length/2, -sit_width/2, 0)

	leg_BR = createLeg(doc, 'leg_BR', *createLeg_params)
	leg_BR.Placement.Rotation = Rotation(Vector(0, 0, 1), 180)
	leg_BR.Placement.Base = (sit_length/2, sit_width/2, 0)
	
	leg_BL = createLeg(doc, 'leg_BL', *createLeg_params)
	leg_BL.Placement.Rotation = Rotation(Vector(0, 0, 1), -90)
	leg_BL.Placement.Base = (-sit_length/2, sit_width/2, 0)


	######  frame  ######
	frame_z = total_height - sit_height - frame_height

	frame_F = createFrameSide(doc, 'frame_F',
		(sit_length - 2*frame_offset - 2*frame_width, frame_width, frame_height),
		(-sit_length/2 + frame_offset + frame_width, -sit_width/2 + frame_offset, frame_z),
		leg_FL, leg_FR
	)
	frame_B = createFrameSide(doc, 'frame_B',
		(sit_length - 2*frame_offset - 2*frame_width, frame_width, frame_height),
		(-sit_length/2 + frame_offset + frame_width, sit_width/2 - frame_offset - frame_width, frame_z),
		leg_BL, leg_BR
	)
	frame_L = createFrameSide(doc, 'frame_L',
		(frame_width, sit_width - 2*frame_offset - 2*frame_width, frame_height),
		(-sit_length/2 + frame_offset, -sit_width/2 + frame_offset + frame_width, frame_z),
		leg_FL, leg_BL
	)
	frame_R = createFrameSide(doc, 'frame_R',
		(frame_width, sit_width - 2*frame_offset - 2*frame_width, frame_height),
		(sit_length/2 - frame_offset - frame_width, -sit_width/2 + frame_offset + frame_width, frame_z),
		leg_FR, leg_BR
	)


	######  sit  ######
	sit = createBox(doc, 'sit',
		(sit_length, sit_width, sit_height),
		(-sit_length/2, -sit_width/2, total_height - sit_height)
	)

	######  sit chamfer  ######
	sit_chamfer = doc.addObject('Part::Chamfer', 'sit_chamfer')
	sit_chamfer.Base = sit
	sit_chamfer.Edges = [(i, 4, 4) for i in range(1, 13)]
	sit.Visibility = False



	doc.recompute(None,True,True)

	#setTransparency(doc, 20)
	setview()


main()
