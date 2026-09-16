"""Keep the authored text and borrow only timing from ASR."""
import re, unicodedata
from difflib import SequenceMatcher

def norm(s):
 return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode())
def align_words(text, recognized, duration):
 target=text.split()
 if not recognized:
  return [{'text':w,'start':i*duration/len(target),'end':(i+1)*duration/len(target)} for i,w in enumerate(target)]
 result=[]
 matcher=SequenceMatcher(a=[norm(w) for w in target],b=[norm(w['text']) for w in recognized],autojunk=False)
 for tag,a,b,c,d in matcher.get_opcodes():
  if a==b: continue
  if tag=='equal':
   result.extend({'text':target[k],'start':recognized[c+k-a]['start'],'end':recognized[c+k-a]['end']} for k in range(a,b))
  else:
   start=recognized[c]['start'] if c<len(recognized) else recognized[-1]['end']
   end=recognized[d-1]['end'] if d>c else (recognized[c]['start'] if c<len(recognized) else duration)
   if end<=start: start=max(0,start-.16*(b-a));end=max(end,start+.05*(b-a))
   weights=[max(1,len(norm(w))) for w in target[a:b]];total=sum(weights);cursor=start
   for word,weight in zip(target[a:b],weights):
    finish=cursor+(end-start)*weight/total
    result.append({'text':word,'start':cursor,'end':finish});cursor=finish
 return result
