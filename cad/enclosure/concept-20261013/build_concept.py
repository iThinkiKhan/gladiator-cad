import FreeCAD as A, FreeCADGui as G, Part, json, traceback, zipfile
from pathlib import Path
R=Path('/home/buralien/projects/gladiator-cad'); O=R/'cad/enclosure/concept-20261013'; O.mkdir(parents=True,exist_ok=True)
try:
 src=A.openDocument(str(R/'cad/master/Gladiator_Master.FCStd'))
 z=zipfile.ZipFile(R/'cad/master/Gladiator_Master.FCStd')
 d=A.newDocument('Gladiator_Enclosure_Concept')
 refs=[]; shells=[]
 def add(name,s,color):
  o=d.addObject('Part::Feature',name);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=(.12,.14,.16);o.ViewObject.DisplayMode='Flat Lines';o.ViewObject.Visibility=True;return o
 def source(n):
  o=src.getObject(n)
  if o and hasattr(o,'Shape'): return o.Shape.copy()
  s=Part.Shape();s.importBrepFromString(z.read(n+'.Shape.brp').decode());return s
 names=['ChassisDeck','SideRailLeft','SideRailRight','UpperDeck','MastBase','MastTube','BatteryBox','BatteryCells','S3Board','Breadboard']+['DrvV5_'+n+'_'+s for n in ['Base','Wedge','Board','Fins'] for s in ['L','R']]
 for n in names:
  color=(.22,.24,.27)
  if n in ['S3Board','Breadboard'] or 'Board_' in n: color=(.19,.42,.34)
  if 'Fins' in n: color=(.52,.55,.58)
  refs.append(add('Ref_'+n,source(n),color))
 for f in ['cad/power-board/v5-tray/PowerBoardTray_v5.FCStd','cad/power-board/ina-cassette-v2/INA226_Cassette_v2.FCStd','cad/power-switch/v1b/PowerSwitchHolder_v1b.FCStd']:
  temp=A.openDocument(str(R/f))
  for o in temp.Objects:
   if o.TypeId=='Part::Feature' and hasattr(o,'Shape') and not o.Shape.isNull(): refs.append(add('Ref_'+o.Name,o.Shape.copy(),(.3,.35,.38)))
  A.closeDocument(temp.Name)
 def section(y,broad,inner=False):
  if inner:
   pts=[(-6.6,0),(85.6,0),(85.6,28),(113.6 if broad else 85.6,50),(113.6 if broad else 85.6,94.6),(81,105.6),(-2,105.6),(-34.6 if broad else -6.6,94.6),(-34.6 if broad else -6.6,50),(-6.6,28)]
  else:
   pts=[(-9,14),(88,14),(88,28),(116 if broad else 88,50),(116 if broad else 88,96),(82,108),(-3,108),(-37 if broad else -9,96),(-37 if broad else -9,50),(-9,28)]
  vs=[A.Vector(x,y,z) for x,z in pts];return Part.makePolygon(vs+[vs[0]])
 outer=Part.makeLoft([section(y,b) for y,b in [(-32,False),(72,False),(90,True),(148,True)]],True,True)
 inner=Part.makeLoft([section(y,b,True) for y,b in [(-29.6,False),(72,False),(90,True),(145.6,True)]],True,True)
 s=outer.cut(inner)
 # Keep all heatsink reference solids exposed with an expanded through opening.
 for n in ['DrvV5_Fins_L','DrvV5_Fins_R','DrvV5_Board_L','DrvV5_Board_R']:
  keep=source(n).makeOffsetShape(4 if 'Fins' in n else 2,0.05)
  s=s.cut(keep)
 # Mast exit: 26 mm opening, split between the two front panels.
 s=s.cut(Part.makeCylinder(13,150,A.Vector(39.5,113,0)))
 # Switch access at current +Y front, on the high-X side.
 s=s.cut(Part.makeBox(19,12,23,A.Vector(47,141,20)))
 # Rear SMA connector land, nominal 7 mm trial cut, actual connector check pending.
 s=s.cut(Part.makeCylinder(3.5,12,A.Vector(63,-37,82),A.Vector(0,1,0)))
 # Rear high vent openings; hidden lower edge provides intake.
 for x in [4,18,32]: s=s.cut(Part.makeBox(8,8,3,A.Vector(x,-35,91)))
 # Three cosmetic panels, 0.6 mm seams. No attachment detail implied.
 regions=[('Rear_Hood',Part.makeBox(300,285.7,200,A.Vector(-100,-200,0)),(.32,.38,.40)),('Front_Left',Part.makeBox(139.2,150,200,A.Vector(-100,86.3,0)),(.40,.46,.48)),('Front_Right',Part.makeBox(200,150,200,A.Vector(39.8,86.3,0)),(.40,.46,.48))]
 checks={'status':'CONCEPT ONLY - NOT PRINT RELEASE','source':'current native master plus tray v5, INA cassette v2, switch v1b','assumptions':{'roof_z':108,'wall_nominal':2.4,'lower_edge_z':14,'heatsink_opening_offset':4,'seam':0.6},'panels':[],'collisions':[]}
 for name,reg,col in regions:
  sh=s.common(reg).removeSplitter();o=add(name,sh,col);shells.append(o)
  checks['panels'].append({'name':name,'valid':sh.isValid(),'solids':len(sh.Solids),'volume_mm3':sh.Volume})
  for r in refs:
   if sh.BoundBox.intersect(r.Shape.BoundBox):
    vol=sh.common(r.Shape).Volume
    if vol>0.01: checks['collisions'].append({'panel':name,'reference':r.Name,'volume_mm3':vol})
 # Explicit simplified track context, not measured swept envelopes.
 tracks=[]
 for x in [-50,79]:
  tracks.append(add('Track_Approx',Part.makeBox(50,170,43,A.Vector(x,-15,-36)),(.13,.15,.17)))
  for y in [-5,145]:
   tracks.append(add('Wheel_Approx',Part.makeCylinder(19,51,A.Vector(x-.5,y,-15),A.Vector(1,0,0)),(.35,.37,.39)))
 # Exterior antenna visual: proposed rear-facing bulkhead then vertical whip.
 ant=[add('Antenna_Proposed_Base',Part.makeCylinder(5,10,A.Vector(63,-42,82),A.Vector(0,1,0)),(.12,.13,.14)),add('Antenna_Proposed_Whip',Part.makeCylinder(3.5,69,A.Vector(63,-40,82)),(.12,.13,.14))]
 head=A.openDocument(str(R/'cad/head/master/Gladiator_Head_Master.FCStd'));headobjs=[]
 for o in head.Objects:
  if o.TypeId=='Part::Feature' and not o.Shape.isNull() and o.Name!='Ctx_MastTube': headobjs.append(add('Head_'+o.Name,o.Shape.copy(),(.54,.58,.6)))
 for panel in shells:
  for h in headobjs:
   if panel.Shape.BoundBox.intersect(h.Shape.BoundBox):
    vol=panel.Shape.common(h.Shape).Volume
    if vol>0.01: checks['collisions'].append({'panel':panel.Name,'reference':h.Name,'volume_mm3':vol})
 A.closeDocument(head.Name);A.closeDocument(src.Name)
 A.setActiveDocument(d.Name);d.recompute()
 (O/'validation.json').write_text(json.dumps(checks,indent=2))
 d.Comment='Review concept only. Current source geometry copied read-only; simplified tracks and proposed antenna. Attachments, wiring, removal sweeps and print orientation remain unresolved.'
 d.saveAs(str(O/'Gladiator_Enclosure_Concept.FCStd'))
 Part.export(shells,str(O/'Gladiator_Enclosure_Shell_CONCEPT.step'))
 Part.export(refs+shells+headobjs,str(O/'Gladiator_Enclosure_Assembly_CONCEPT.step'))
 G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui()
 G.activeDocument().activeView().saveImage(str(O/'assembled.png'),1400,1400,'White')
 for o in headobjs:o.ViewObject.Visibility=False
 G.activeDocument().activeView().fitAll();G.updateGui();G.activeDocument().activeView().saveImage(str(O/'body.png'),1400,1100,'White')
 for o in shells:o.ViewObject.Transparency=78
 G.updateGui();G.activeDocument().activeView().saveImage(str(O/'clearance.png'),1400,1100,'White')
 for o in shells:o.ViewObject.Transparency=0
 for o in headobjs:o.ViewObject.Visibility=True
 d.recompute();d.save()
except:
 (O/'build-error.txt').write_text(traceback.format_exc())
import os; os._exit(0)


