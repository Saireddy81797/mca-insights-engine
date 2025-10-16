# src/api.py
from flask import Flask, request, jsonify
import pandas as pd
app = Flask(__name__)
master = pd.read_csv("data/processed/mca_master.csv")

@app.route("/search_company")
def search_company():
    q = request.args.get("q","").strip().upper()
    if not q:
        return jsonify({"error":"query param q required"}), 400
    res = master[ master['CIN'].str.upper().str.contains(q) | master['COMPANY_NAME'].str.upper().str.contains(q) ]
    return jsonify(res.head(50).to_dict(orient='records'))

if __name__=="__main__":
    app.run(port=8000, debug=True)
