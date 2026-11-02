"""MCDA totals and weight sensitivity for ADR-0030 (live default ACT threshold)."""
import itertools
W={"safe":35,"adr":25,"kiss":25,"ux":15}
S={"A":[2,1,5,4],"B":[5,5,4,5],"C":[4,3,4,2],"D":[5,4,2,4]}
for k,v in S.items(): print(k,sum(a*b for a,b in zip(W.values(),v))*1)
wins={k:0 for k in S};n=0
for w in itertools.product(range(5,90,5),repeat=3):
  r=100-sum(w)
  if r<5: continue
  ww=list(w)+[r];n+=1
  t={k:sum(a*b for a,b in zip(ww,v)) for k,v in S.items()};m=max(t.values())
  for k in t:
    if t[k]==m: wins[k]+=1
print(n,{k:round(100*v/n) for k,v in wins.items()})
