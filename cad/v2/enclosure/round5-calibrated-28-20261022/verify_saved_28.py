from pathlib import Path
import FreeCAD as A,Part,MeshPart,json,math,traceback,os
R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022');V=A.Vector
try:
 d=A.openDocument(str(R/'print/Gladiator_Round5_Print.FCStd'))
 old=A.openDocument('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-print-20261022/Gladiator_Round5_Print.FCStd')
 bores={'Rear_Hood':[(f'Tablet_{side}_{y}',(x,y,70),0) for side,x in [('L',-11.8),('R',90.8)] for y in [-6,48]]+[('Aquila',(26,-34.8,68.5),1)],'Front_Left':[('Scutum_L',(16,150.8,79),1)],'Front_Right':[('Scutum_R',(63,150.8,79),1)],'Crest_Clamp':[('Crest_side',(39.5,157.8,237.8),1),('Crest_top',(39.5,163,242.15),2)],'Neck_Clamp_0':[('Neck0_side',(21.5,103.8,236.7),1),('Neck0_top',(21.5,110,241.2),2)],'Neck_Clamp_1':[('Neck1_side',(57.5,103.8,236.7),1),('Neck1_top',(57.5,110,241.2),2)]}
 report={'bores':{},'changed_part_preservation':{},'unchanged_parts':[]}
 for name,holes in bores.items():
  s=d.getObject(name).Shape;o=old.getObject(name).Shape
  assert s.isValid() and len(s.Solids)==1
  missing=o.cut(s).Volume
  assert missing<.001,(name,'original material lost',missing)
  report['changed_part_preservation'][name]={'original_material_removed_mm3':missing,'added_mm3':s.cut(o).Volume}
  for label,centre,axis in holes:
   radial=[a for a in range(3) if a!=axis];fail=[]
   for along in [-1.0,-.5,0,.5,1.0]:
    for i in range(36):
     angle=i*math.pi/18
     for radius,inside in [(1.35,False),(1.60,True)]:
      p=list(centre);p[axis]+=along;p[radial[0]]+=radius*math.cos(angle);p[radial[1]]+=radius*math.sin(angle)
      got=s.isInside(V(*p),1e-6,True)
      if got!=inside:fail.append([along,i,radius,got])
   assert not fail,(label,fail[:8])
   report['bores'][label]={'CAD_diameter_mm':2.8,'radial_samples':360,'clear_at_radius_1_35_and_material_at_1_60':True}
 names=json.loads((R/'style/validation.json').read_text())['parts']
 exceptions=set(bores)|{'Scutum_Emblem_L','Scutum_Emblem_R','Scutum_Boss_L','Scutum_Boss_R'}
 for name in names:
  s=d.getObject(name).Shape;assert s.isValid() and len(s.Solids)==1
  if name not in exceptions:
   o=old.getObject(name).Shape
   err=abs(s.Volume-o.Volume);assert err<.001,(name,err)
   assert (s.CenterOfMass-o.CenterOfMass).Length<.0001,name
   report['unchanged_parts'].append(name)
 step=A.newDocument('SavedCalibratedStepCheck');Part.insert(str(R/'print/Gladiator_Round5_PrintParts.step'),step.Name)
 solids=[s for o in step.Objects if hasattr(o,'Shape') for s in o.Shape.Solids]
 assert len(solids)==22 and all(s.isValid() for s in solids)
 report['STEP_valid_solid_count']=22
 for side in ['L','R']:
  emblem=d.getObject('Scutum_Emblem_'+side).Shape;field=d.getObject('Scutum_Field_'+side).Shape
  assert abs(emblem.Volume-1052.4)<.2
  assert emblem.common(field).Volume<.001
 report['stronger_insets_v2_in_saved_native']=True
 report['passed']=True
 (R/'saved-cad-verification.json').write_text(json.dumps(report,indent=2))
except BaseException:(R/'SAVED_CAD_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
