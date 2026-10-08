import json,sys
from pathlib import Path
p=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results')
name=sys.argv[1] if len(sys.argv)>1 else 'combat_baseline';a=json.loads((p/(name+'_server.json')).read_text());b=json.loads((p/(name+'_client.json')).read_text())
normalized=lambda inventories:{key:sorted(value,key=lambda item:item['id']) for key,value in inventories.items()}
result={'distinct_processes':a['process_id']!=b['process_id'],'all_cases_pass':a['passed']==a['total'] and b['passed']==b['total'],'exact_inventory_convergence':normalized(a['inventories'])==normalized(b['inventories']),'server':a['process_id'],'client':b['process_id'],'network':a['network']}
(p/(name+'-comparison.json')).write_text(json.dumps(result,indent=2));print(result)

