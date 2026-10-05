import unreal,json,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
# Project-scoped Unreal Python jobs; used only for asset inspection and PIE tests.
last=0
counter=0
def poll(dt):
    global last,counter
    counter+=dt
    if counter<.2:return
    counter=0
    path=B+'job.json'
    if not os.path.exists(path):return
    data=json.load(open(path))
    if data['id']==last:return
    last=data['id']
    try:exec(open(B+data['script']).read(),{'__name__':'__main__'})
    except Exception as e:unreal.log_error('GATE3_JOB_ERROR '+str(e))
handle=unreal.register_slate_post_tick_callback(poll)
unreal.log('GATE3_JOB_RUNNER_READY')
