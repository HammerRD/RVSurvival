import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
json.dump({'name':'final_material_client','driver':'client','network':False},open(B+'case.json','w'))
exec(open(B+'run_suite.py').read(),{'__name__':'__main__'})
