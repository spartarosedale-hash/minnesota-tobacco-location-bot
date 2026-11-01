"""Train and evaluate monthly revenue model from independent stores.
Usage: python train_revenue_model.py --data training_stores.csv
Requires >= 10 unique stores; holds out 25% stores; does not train on Litchfield/Zimmerman.
Never treat untrained assumptions as predictions.
"""
import argparse,csv,json,math,random,statistics
from pathlib import Path

FEATURES=("adults_21_plus","median_household_income","aadt","competitors_3mi","store_sqft","weekly_open_hours")
HOLDOUT_NAMES=("litchfield tobacco","zimmerman tobacco")

def load(path):
    with open(path,newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    seen=set();valid=[]
    for row in rows:
        store=row.get("store_name","").strip()
        if not store or store.casefold() in HOLDOUT_NAMES:
            continue
        if store.casefold() in seen:
            raise ValueError("Duplicate store: "+store)
        seen.add(store.casefold())
        try:
            features=[float(row[k]) for k in FEATURES]
            revenue=float(row["monthly_sales_excluding_tax"])
        except (KeyError,ValueError,TypeError):
            continue
        if all(math.isfinite(v) and v>=0 for v in features) and math.isfinite(revenue) and revenue>0:
            valid.append((store,features,revenue))
    return valid

def train(path,output="data/revenue_model_evaluation.json"):
    rows=load(path)
    if len(rows)<10:
        raise ValueError(f"Need at least 10 complete independent stores, got {len(rows)}. No model trained.")
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import mean_absolute_error
    except ImportError as exc:
        raise RuntimeError("Install numpy and scikit-learn") from exc
    random.Random(42).shuffle(rows)
    holdout_n=max(2,round(len(rows)*.25))
    test=rows[:holdout_n];train_rows=rows[holdout_n:]
    x_train=np.array([r[1] for r in train_rows])
    y_train=np.array([math.log1p(r[2]) for r in train_rows])
    x_test=np.array([r[1] for r in test])
    actual=np.array([r[2] for r in test])
    model=RandomForestRegressor(n_estimators=250,min_samples_leaf=2,random_state=42)
    model.fit(x_train,y_train)
    predicted=np.expm1(model.predict(x_test)).clip(min=0)
    errors=np.abs(predicted-actual)
    report={"status":"EVALUATED_NOT_DEPLOYED","features":FEATURES,"total_stores":len(rows),
            "train_stores":len(train_rows),"test_stores":len(test),
            "mae_usd":round(float(mean_absolute_error(actual,predicted)),2),
            "median_absolute_percentage_error":round(float(statistics.median(errors/actual)*100),1),
            "holdout_results":[{"store":r[0],"actual_usd":round(float(a),2),"predicted_usd":round(float(p),2)}
                for r,a,p in zip(test,actual,predicted)],
            "warning":"Small sample. Random holdout is only an initial check. Need multi-region and time-based validation; no calibrated prediction intervals."}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--data",default="training_stores.csv")
    p.add_argument("--output",default="data/revenue_model_evaluation.json")
    args=p.parse_args()
    print(json.dumps(train(args.data,args.output),indent=2))
