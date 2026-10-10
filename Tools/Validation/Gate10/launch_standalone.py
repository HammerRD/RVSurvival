"""Separate native game processes for reconnect validation; no editor map reload."""
import subprocess,time,json
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation'
case={'name':'region-standalone-road-rejoin','network':True,'difficulty':True,'rejoin':True,'rejoin_only':True,'port':17778,'standalone':True,'travel_gc':False}
session={'id':time.time(),'start':None,'config':case};(out/'process-session.json').write_text(json.dumps(session))
exe='D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
cmds='wp.Runtime.EnableServerStreaming 1,wp.Runtime.EnableServerStreamingOut 1,wp.Runtime.UseMakingVisibleTransactionRequests 1,wp.Runtime.UseMakingInvisibleTransactionRequests 1,LevelStreaming.DefaultAllowClientUseMakingVisibleTransactionRequests 1,Net PktLag=100,Net PktLoss=2,py '+str(root/'Tools/Validation/Gate10/standalone_startup.py')
common=[str(root/'RVSurvival.uproject'),'-game','-windowed','-ResX=1000','-ResY=650','-nosplash','-ExecCmds='+cmds]
processes=[]
try:
 processes.append(subprocess.Popen([exe,common[0],'/Game/Maps/WNY_PrototypeRegion?listen','-port=17778']+common[1:]+['-abslog='+str(out/(case['name']+'-server.log'))],creationflags=subprocess.CREATE_NO_WINDOW))
 time.sleep(12)
 processes.append(subprocess.Popen([exe,common[0],'127.0.0.1:17778']+common[1:]+['-abslog='+str(out/(case['name']+'-client.log'))],creationflags=subprocess.CREATE_NO_WINDOW))
 while time.time()-session['id']<240:
  if not session['start']:
   try:ready=all(json.loads((out/('standalone-ready-'+r+'.json')).read_text())['id']==session['id'] for r in ['server','client'])
   except (OSError,ValueError):ready=False
   if ready:session['start']=time.time()+4;(out/'process-session.json').write_text(json.dumps(session));print('Both native game processes ready.',flush=True)
  try:complete=all(json.loads((out/(case['name']+'-'+r+'.json')).read_text())['session']==session['id'] for r in ['server','client'])
  except (OSError,ValueError):complete=False
  if complete:
   print('Fresh receipts available; waiting for clean game shutdown.',flush=True)
   for p in processes:
    try:p.wait(timeout=35)
    except subprocess.TimeoutExpired:pass
   break
  time.sleep(2)
 else:(out/(case['name']+'-timeout.json')).write_text(json.dumps({'timeout':True,'started':bool(session['start'])}))
finally:
 # Quit through the normal game console in the engine-side completion callback;
 # terminate is only the bounded timeout recovery path, never editor asset work.
 for p in processes:
  if p.poll() is None:p.terminate()
 for p in processes:p.wait(timeout=20)
