"""Rolling-origin synthetic backtest using only interest observed before each test term."""
import csv, json, math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.json').read_text(encoding='utf-8'))

def main():
    with (ROOT/'data'/'RegistrationInterest.csv').open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    terms=CFG['terms'][:-1]  # exclude current target term from historical backtest
    counts=defaultdict(lambda:defaultdict(int))
    for r in rows:
        if r['interest_status'] in ('SUBMITTED','CONFIRMED') and r['term'] in terms:
            counts[r['course_id']][r['term']]+=1
    weights=CFG['forecast_weights']
    actuals=[]; predictions=[]; detail=[]
    # At each origin, use up to the previous three terms only; no target-term leakage.
    for idx in range(1,len(terms)):
        target=terms[idx]
        prior=terms[max(0,idx-3):idx]
        active_weights=weights[-len(prior):]
        norm=sum(active_weights)
        active_weights=[w/norm for w in active_weights]
        for course_id, by_term in counts.items():
            history=[by_term[t] for t in prior]
            pred=max(0, math.ceil(sum(v*w for v,w in zip(history,active_weights))))
            actual=by_term[target]
            actuals.append(actual); predictions.append(pred)
            detail.append({'course_id':course_id,'test_term':target,'history_terms':'|'.join(prior),
                           'forecast':pred,'actual_interest':actual,'absolute_error':abs(pred-actual)})
    abs_errors=[abs(a-p) for a,p in zip(actuals,predictions)]
    mae=sum(abs_errors)/len(abs_errors) if abs_errors else 0
    rmse=math.sqrt(sum((a-p)**2 for a,p in zip(actuals,predictions))/len(actuals)) if actuals else 0
    denom=sum(actuals)
    wape=sum(abs_errors)/denom if denom else 0
    summary={'evaluation_type':'rolling_origin_synthetic_backtest','target_terms_tested':terms[1:],
             'observations':len(actuals),'MAE':round(mae,4),'RMSE':round(rmse,4),
             'WAPE':round(wape,4),'WAPE_percent':round(wape*100,2),
             'data_note':'Synthetic registration-interest counts; not actual enrollment or real-world forecast accuracy.',
             'leakage_control':'Each test-term prediction uses only earlier terms; target-term interest is excluded.'}
    out=ROOT/'outputs'; out.mkdir(exist_ok=True)
    with (out/'forecast_backtest.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(detail[0]) if detail else ['course_id','test_term','history_terms','forecast','actual_interest','absolute_error']); w.writeheader(); w.writerows(detail)
    (out/'forecast_backtest_metrics.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return summary
if __name__=='__main__': main()
