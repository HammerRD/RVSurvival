$t=Get-Content Saved/Gate3Validation/suite.py -Raw;$offset=$t.IndexOf('rows=[];results=[]');$t=(Get-Content Saved/Gate3Validation/process_header.txt -Raw)+$t.Substring($offset)
$t=$t.Replace("def cmd(pc,s):unreal.SystemLibrary.execute_console_command(pc,s,pc)","def cmd(pc,s):`n if pc:unreal.SystemLibrary.execute_console_command(pc,s,pc)`ndef look(pc,r):`n if pc:pc.set_control_rotation(r)")
$t=$t.Replace('walker.set_control_rotation(','look(walker,').Replace('driver.set_control_rotation(','look(driver,')
$t=$t.Replace('swp.set_actor_location(sv.get_actor_transform()', 'if isServer:swp.set_actor_location(sv.get_actor_transform()')
$t=$t.Replace(';p.set_actor_location(pos,False,True);',"`n if isServer:p.set_actor_location(pos,False,True)`n ")
$t=$t.Replace("driver.get_controlled_pawn()==(sv if role=='host' else cv)","(driver.get_controlled_pawn()==v if driver else any(s.get_editor_property('bDriverSeat') and s.get_editor_property('Occupant')==(hp if role=='host' else cp) for s in v.get_seats()))")
$t=$t.Replace('elapsed+=dt;sample_acc+=dt',"elapsed=time.time()-session['start'];sample_acc+=dt`n if elapsed<0:return")
$t=$t.Replace("{'config':config,'results':results,'samples':rows,'anchors':anchors}","{'config':config,'process_id':os.getpid(),'authority':isServer,'station_counts':{n:a.get_editor_property('InteractionCount') for n,a in st.items()},'results':results,'samples':rows,'anchors':anchors}")
Set-Content Saved/Gate3Validation/process_suite.py $t
