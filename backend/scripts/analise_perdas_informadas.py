"""Estatísticas das perdas informadas pelos usuários (somente leitura).

Uso: python backend/scripts/analise_perdas_informadas.py [caminho/municipios_editados.json]
"""
import json, sys, collections, statistics as st
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'backend/municipios_editados.json'))
NOMES = ["eSF/eAP","Saúde Bucal","eMulti","ACS","Demais programas","Manut. valor nominal","Promoção à saúde","pos7","pos8"]
UF = {'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
rows=[(k.split('_')[0],k.split('_')[1],v['perda_recurso_mensal'],v.get('data_edicao','')) for k,v in D.items()]
print("TOTAL",len(rows),"municípios",len({r[0] for r in rows}),"competências",len({r[1] for r in rows}))
print("\nPOR COMPETÊNCIA", sorted(collections.Counter(r[1] for r in rows).items()))
print("POR UF", collections.Counter(UF.get(r[0][:2],'?') for r in rows).most_common())
print("TAMANHO ARRAY", sorted(collections.Counter(len(r[2]) for r in rows).items()))
print("\nPOR POSIÇÃO: n>0 | mediana | máx | total mensal | múltiplos")
for i in range(9):
    vals=[r[2][i] for r in rows if len(r[2])>i and r[2][i] and r[2][i]>0]
    if not vals: continue
    def m(u): return sum(1 for v in vals if abs(v/u-round(v/u))<1e-6)
    print(f"{i} {NOMES[i]:<20} {len(vals):>4} | {st.median(vals):>12,.2f} | {max(vals):>14,.2f} | {sum(vals):>16,.2f} | x4000:{m(4000)} x6000:{m(6000)} x12000:{m(12000)} x3242:{m(3242)} centavos:{sum(1 for v in vals if v!=int(v))}")
    print("   top:", [(f"{v:,.2f}",c) for v,c in collections.Counter(vals).most_common(6)])
print("\nTOTAL MENSAL INFORMADO:", f"{sum(sum(x for x in r[2] if x) for r in rows):,.2f}")
tot=sorted(((sum(x for x in r[2] if x),r[0],r[1]) for r in rows),reverse=True)
print("MAIORES TOTAIS:", [(f"{t:,.0f}",m,c) for t,m,c in tot[:6]])
print("MENORES >0:", [(f"{t:,.2f}",m,c) for t,m,c in sorted(x for x in tot if x[0]>0)[:4]])
print("ZERADOS:", [(m,c) for t,m,c in tot if t==0])
med=st.median([t for t,_,_ in tot if t>0]); print("mediana total/mun:",f"{med:,.0f}")
print("\nEVOLUÇÃO (municípios com >1 competência):")
by=collections.defaultdict(list)
for r in rows: by[r[0]].append(r)
for mun,rs in sorted(by.items()):
    if len(rs)>1:
        print(" ",mun,UF.get(mun[:2]),"|"," → ".join(f"{c}:{sum(x for x in p if x):,.0f}" for _,c,p,_ in sorted(rs,key=lambda r:r[1])))
print("\nEDIÇÕES POR MÊS:", sorted(collections.Counter(r[3][:7] for r in rows).items()))
