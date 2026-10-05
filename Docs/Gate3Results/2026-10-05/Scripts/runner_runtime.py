import importlib.util,sys,pathlib,time
# Keep registered callable globals owned by real modules for the editor lifetime.
def load_runner(path):
 name='rv_validation_'+pathlib.Path(path).stem+'_'+str(time.time_ns())
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module
 spec.loader.exec_module(module)
 return module

def release_runners():
 import gc
 for name in list(sys.modules):
  if name.startswith('rv_validation_'):
   module=sys.modules.pop(name)
   module.__dict__.clear()
 return gc.collect()
