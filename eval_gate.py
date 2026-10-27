"""Small Homework 6-compatible release gate for this prototype."""
import argparse, hashlib, importlib, json, statistics, re

def cases(): return [json.loads(x) for x in open('eval_set.jsonl') if x.strip()]
def eval_hash(cs): return hashlib.sha256(json.dumps(sorted(cs,key=lambda x:x['id']),sort_keys=True,ensure_ascii=True).encode()).hexdigest()[:12]
def check(a, kind, arg):
    if kind == 'contains': return arg.lower() in a.lower()
    if kind == 'not_contains': return arg.lower() not in a.lower()
    if kind == 'cites': return a.rstrip().endswith(f'[{arg}]')
    if kind == 'refuses': return 'cannot investigate' in a.lower() or 'do not have' in a.lower()
    return re.search(arg, a) is not None
def run(system, cs, seed):
    rows={}
    for c in cs:
        try: a=system.answer(c['question'], seed=seed); ok=all(check(a,k,v) for k,v in c['checks'])
        except Exception: a=''; ok=False
        rows[c['id']]={'pass':ok,'tokens':max(1,round(len(a)/4))}
    by={}
    for c in cs: by.setdefault(c['category'],[]).append(rows[c['id']]['pass'])
    out={k:sum(v)/len(v) for k,v in by.items()}; out['overall']=sum(x['pass'] for x in rows.values())/len(rows); out['tokens']=statistics.mean(x['tokens'] for x in rows.values())
    return out
def main():
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument('--hash',action='store_true'); g.add_argument('--aa',action='store_true'); g.add_argument('--gate',action='store_true'); args=p.parse_args()
    cs=cases(); h=eval_hash(cs)
    if args.hash: print(h); return
    manifest=json.load(open('manifest.json'))
    if manifest['eval_set_hash'] != h: raise SystemExit(f'BLOCK: manifest hash is {manifest["eval_set_hash"]}, actual hash is {h}')
    if args.aa:
        system=importlib.import_module(manifest['adapter']); ss=[run(system,cs,i) for i in range(10)]
        mean={k:statistics.mean(x[k] for x in ss) for k in ss[0]}; sd={k:statistics.pstdev([x[k] for x in ss]) for k in ss[0] if k != 'tokens'}
        json.dump({'eval_set_hash':h,'mean':mean,'run_sd':sd},open('baseline.json','w'),indent=2); print('A/A baseline written',mean); return
    b=json.load(open('baseline.json')); system=importlib.import_module(manifest['adapter']); cand=run(system,cs,1000); reasons=[]
    rule=manifest['gate']; limit=float(rule.get('max_drop_sigma',3))
    for k in sorted(x for x in b['mean'] if x not in ('tokens',)):
        if k in rule.get('critical',[]) and cand.get(k,0) < 1:
            reasons.append(f'critical category {k} failed')
        sigma=b.get('run_sd',{}).get(k,0)
        drop=b['mean'][k]-cand.get(k,0)
        if sigma > 0 and drop > limit*sigma:
            reasons.append(f'{k} fell {drop:.1%}, beyond {limit:g} sigma')
        elif sigma == 0 and drop > 0:
            reasons.append(f'{k} fell {drop:.1%} with zero A/A noise')
    if cand['tokens'] > b['mean']['tokens']*(1+float(rule.get('max_token_increase',.2))):
        reasons.append('token increase exceeded configured limit')
    verdict='BLOCK' if reasons else 'SHIP'; json.dump({'verdict':verdict,'reasons':reasons,'baseline':b['mean'],'candidate':cand},open('gate_report.json','w'),indent=2); print(verdict, reasons or 'candidate passed')
    raise SystemExit(1 if reasons else 0)
if __name__ == '__main__': main()
