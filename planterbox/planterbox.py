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


def setTransparency(doc, tr):
	for obj in doc.Objects:
		obj.ViewObject.Transparency = tr

def loop(doc, prefix, lwh, position_start, axis_idx, distance):
	k = axis_idx

	a = Vector(0, 0, 0)
	a[k] = lwh[k]

	n = int(distance//a[k])

	b = Vector(0, 0, 0)    # gap
	b[k] = (distance - n*a[k])/(n+1)
	print(prefix, b[k])
	
	pos = Vector(position_start)
	for i in range(0, n):
		createBox(doc, prefix + str(i), lwh, pos + b + i*(a+b))




def main():
	print('-----------')
	doc_name = 'planterbox'

	d1, d2, d3, d4, d6, d8 = 19, 38, 63.5, 89, 140, 184

	# base box: length * width * height (planter box except upper frame)
	#length = 1025  # base (not the whole planter box)
	#width = 500    # base (not the whole planter box)
	
	#length = 461
	#width = 359

	length = 630
	width = 620
	height = 500   # base (2x4s, not the whole planter box)
	
	b = 9  # distance from 1x4s to outer face of base box
	floor_offset = 50
	slack = 2
	overlap = 30  # how much a face ovarlaps with sceleton for screwing

	try:
		doc = FreeCAD.getDocument(doc_name)
	except:
		doc = FreeCAD.newDocument(doc_name)

	FreeCAD.setActiveDocument(doc_name)

	# remove objects
	for obj in doc.Objects:
		doc.removeObject(obj.Name)

	FL = createBox(doc, 'FL', (d4, d2, height), (-length/2     , -width/2     , 0))
	FR = createBox(doc, 'FR', (d4, d2, height), ( length/2 - d4, -width/2     , 0))
	BL = createBox(doc, 'BL', (d4, d2, height), (-length/2     ,  width/2 - d2, 0))
	BR = createBox(doc, 'BR', (d4, d2, height), ( length/2 - d4,  width/2 - d2, 0))

	FD = createBox(doc, 'FD', (length - 2*d4, d1, d4), (-length/2 + d4, -width/2      + b, floor_offset))
	BD = createBox(doc, 'BD', (length - 2*d4, d1, d4), (-length/2 + d4,  width/2 - d1 - b, floor_offset))
	FU = createBox(doc, 'FU', (length - 2*d4, d1, d4), (-length/2 + d4, -width/2      + b, height - d4))
	BU = createBox(doc, 'BU', (length - 2*d4, d1, d4), (-length/2 + d4,  width/2 - d1 - b, height - d4))

	LD = createBox(doc, 'LD', (d1, width - 2*d2, d4), (-length/2      + b, -width/2 + d2, floor_offset))
	RD = createBox(doc, 'RD', (d1, width - 2*d2, d4), ( length/2 - d1 - b, -width/2 + d2, floor_offset))
	LU = createBox(doc, 'LU', (d1, width - 2*d2, d4), (-length/2      + b, -width/2 + d2, height - d4))
	RU = createBox(doc, 'RU', (d1, width - 2*d2, d4), ( length/2 - d1 - b, -width/2 + d2, height - d4))

	Ls = createBox(doc, 'Lsupport', (d2, width - 2*d2, d1), (-length/2 + d1      + b, -width/2 + d2, floor_offset + 2))
	Rs = createBox(doc, 'Rsupport', (d2, width - 2*d2, d1), ( length/2 - d1 - d2 - b, -width/2 + d2, floor_offset + 2))
	#Ms = createBox(doc, 'Msupport', (d2, width - 2*d1 - 2*b, d1), (-d2/2, -width/2 + d1 + b, floor_offset + 2))

	
	face_z0 = floor_offset + d4 - overlap
	face_z1 = height - d4 + overlap

	loop(
		doc, 'Floor', 
		(length - 2*d1 - 2*b - 2*slack, d6, d1), 
		(-length/2 + d1 + b + slack, -width/2 + d2, floor_offset + 2 + d1),
		1,
		width - 2*d2
	)

	loop(doc, 'Lface',
		(d1/2, d4, face_z1 - face_z0),
		(-length/2 + d1 + b, -width/2 + d2, face_z0),
		1,
		width - 2*d2
	)

	loop(doc, 'Rface',
		(d1/2, d6, face_z1 - face_z0),
		(length/2 - d1 - b - d1/2, -width/2 + d2, face_z0),
		1,
		width - 2*d2
	)

	loop(doc, 'Fface',
		(d4, d1/2, face_z1 - face_z0),
		(-length/2 + d4, -width/2 + b + d1, face_z0),
		0,
		length - 2*d4
	)

	loop(doc, 'Bface',
		(d6, d1/2, face_z1 - face_z0),
		(-length/2 + d4, +width/2 - b - d1 - d1/2, face_z0),
		0,
		length - 2*d4
	)

	#setTransparency(doc, 20)
	#setview()






















def main2():
	doc_name = 'planterbox2'

	d1, d2, d3, d4, d6, d8 = 19, 38, 63.5, 89, 140, 184

	# base box: length * width * height (planter box except upper frame)
	length = 950  # base (not the whole planter box)
	width = 500    # base (not the whole planter box)
	height = 500   # base (2x4s, not the whole planter box)
	
	b = 5  # distance from 1x4s to outer face of base box (an inset?)
	floor_offset = 50
	slack = 2

	try:
		doc = FreeCAD.getDocument(doc_name)
	except:
		doc = FreeCAD.newDocument(doc_name)

	FreeCAD.setActiveDocument(doc_name)

	# remove objects
	for obj in doc.Objects:
		doc.removeObject(obj.Name)

	FL = createBox(doc, 'FL', (d2, d4, height), (-length/2     , -width/2     , 0))
	FR = createBox(doc, 'FR', (d2, d4, height), ( length/2 - d2, -width/2     , 0))
	BL = createBox(doc, 'BL', (d2, d4, height), (-length/2     ,  width/2 - d4, 0))
	BR = createBox(doc, 'BR', (d2, d4, height), ( length/2 - d2,  width/2 - d4, 0))

	FD = createBox(doc, 'FD', (length-2*d2, d1, d4), (-length/2 + d2, -width/2      + b, floor_offset))
	BD = createBox(doc, 'BD', (length-2*d2, d1, d4), (-length/2 + d2,  width/2 - d1 - b, floor_offset))
	FU = createBox(doc, 'FU', (length-2*d2, d1, d4), (-length/2 + d2, -width/2      + b, height - d4))
	BU = createBox(doc, 'BU', (length-2*d2, d1, d4), (-length/2 + d2,  width/2 - d1 - b, height - d4))

	LD = createBox(doc, 'LD', (d1, width-2*d4, d4), (-length/2      + b, -width/2 + d4, floor_offset))
	RD = createBox(doc, 'RD', (d1, width-2*d4, d4), ( length/2 - d1 - b, -width/2 + d4, floor_offset))
	LU = createBox(doc, 'LU', (d1, width-2*d4, d4), (-length/2      + b, -width/2 + d4, height - d4))
	RU = createBox(doc, 'RU', (d1, width-2*d4, d4), ( length/2 - d1 - b, -width/2 + d4, height - d4))

	Fs = createBox(doc, 'Fsupport', (length-2*d2, d2, d1), (-length/2 + d2, -width/2 + d1      + b, floor_offset))
	Bs = createBox(doc, 'Bsupport', (length-2*d2, d2, d1), (-length/2 + d2, +width/2 - d1 - d2 - b, floor_offset))

	#x1 = -length/2 + d2
	#x2 =  length/2 - d2

	loop(
		doc, 'Floor', 
		(d6, width - 2*d1 - 2*b - 2*slack, d1), 
		(-length/2 + d2 + slack, -width/2 + d1 + b + slack, floor_offset + d1),
		0,
		length - 2*d2 - 2*slack
	)

	#createBox(doc, 'Floor0', (d6, width - 2*d1 - 2*b - 2*slack, d1), (x1 + 0*(d6 + slack), -width/2 + d1 + b + slack, floor_offset + d1))
	#createBox(doc, 'Floor1', (d6, width - 2*d1 - 2*b - 2*slack, d1), (x1 + 1*(d6 + slack), -width/2 + d1 + b + slack, floor_offset + d1))
	#createBox(doc, 'Floor2', (d6, width - 2*d1 - 2*b - 2*slack, d1), (x1 + 2*(d6 + slack), -width/2 + d1 + b + slack, floor_offset + d1))
	#createBox(doc, 'Floor3', (d6, width - 2*d1 - 2*b - 2*slack, d1), (x1 + 3*(d6 + slack), -width/2 + d1 + b + slack, floor_offset + d1))


	#setTransparency(doc, 80)

	#setview()



main()
#main2()
