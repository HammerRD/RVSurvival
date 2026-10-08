import wave,random,math,struct
from pathlib import Path
p=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9Validation/Prototype9mm.wav');rng=random.Random(9);rate=44100
with wave.open(str(p),'wb') as f:
 f.setparams((1,2,rate,0,'NONE','not compressed'))
 f.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,(rng.uniform(-1,1)*.65+math.sin(i/rate*2*math.pi*110)*.25)*math.exp(-i/rate*38)))*28000)) for i in range(int(rate*.28))))
