"""Synthetic finite decision check; no measured optical/LLM parameters."""
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
# Rate is normalized data units/s, not a physical modulation calibration.
# QoT is an assumed admissibility flag, not a computed physical-layer result.
ROUTES = [
    dict(name='A', free=(1, 2, 4, 6), slots=2, rate=1., setup=.2, qot=True),
    dict(name='B', free=(1, 2, 3, 4), slots=4, rate=4., setup=2., qot=True),
]
ACTIONS = [dict(name='KV', volume=8., prepare=0., compute=0.),
           dict(name='ACT', volume=2., prepare=.2, compute=1.3)]

def contiguous(free, n):
    return any(all(i + j in free for j in range(n)) for i in free)

def evaluate(routes, actions, ignore_contiguity=False):
    rows = []
    for r in routes:
        allowed = r['qot'] and (len(r['free']) >= r['slots'] if ignore_contiguity
                               else contiguous(r['free'], r['slots']))
        if allowed:
            for a in actions:
                # Explicit serial pause/copy/rebuild model; not EdgeFlow pipeline.
                t = r['setup'] + a['prepare'] + a['volume']/r['rate'] + a['compute']
                rows.append(dict(route=r['name'], action=a['name'], time=round(t, 8)))
    return rows

def best(rows):
    return min(rows, key=lambda x: (x['time'], x['route'], x['action']))

rows = evaluate(ROUTES, ACTIONS)
network_first = max(ROUTES, key=lambda r:r['rate'])['name']
results = dict(
    joint=best(rows),
    max_rate_then_adapt=best([x for x in rows if x['route']==network_first]),
    fixed_KV=best([x for x in rows if x['action']=='KV']),
    # A network oracle exposing every (rate, setup, feasible) option loses no info.
    complete_network_menu_oracle=best(rows),
    in_place_assumed_time=5.,
)
fragmented = [dict(r, free=(1,3,5,7)) if r['name']=='A' else dict(r) for r in ROUTES]
results['fragmented_A'] = best(evaluate(fragmented, ACTIONS))
results['fragmentation_ignored'] = best(evaluate(fragmented, ACTIONS, True))
results['A_QoT_failed'] = best(evaluate([dict(r,qot=False) if r['name']=='A' else r for r in ROUTES], ACTIONS))
expensive = [dict(a,compute=3.) if a['name']=='ACT' else a for a in ACTIONS]
results['costly_rebuild'] = best(evaluate(ROUTES, expensive))
assert results['joint']['time']==3.7
assert results['joint']==results['complete_network_menu_oracle']
assert results['fragmented_A']['time']==4.
assert results['costly_rebuild']['action']=='KV'
with (OUT/'choices.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=['route','action','time']);w.writeheader();w.writerows(rows)
(OUT/'results.json').write_text(json.dumps(dict(parameters=dict(routes=ROUTES,actions=ACTIONS),results=results),indent=2))
print(json.dumps(results,indent=2))
