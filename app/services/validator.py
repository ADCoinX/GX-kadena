import time, joblib, requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, XMLResponse

app = FastAPI()

# Load AI model
model = joblib.load("app/data/models/model_v1.pkl")

# Metrics
user_count = set()
validations = []

# Kadena API fallback
KADENA_APIS = [
    "https://api.kadenaexplorer.com/address/",
    "https://api.chainweb.com/v1/account/",
    "https://public.kadena.network/api/address/"
]

def fetch_kadena(address):
    for api in KADENA_APIS:
        try:
            r = requests.get(f"{api}{address}", timeout=5)
            if r.status_code == 200:
                return r.json()
        except: continue
    raise HTTPException(502, "Kadena API error")

def ai_score(features):
    return int(model.predict([features])[0])

@app.post("/validate")
async def validate(request: Request):
    body = await request.json()
    address = body.get("address")
    chain = body.get("chain")
    ip = request.client.host
    user_count.add(ip)
    kadena = fetch_kadena(address)
    features = [
        kadena.get("tx_count",0),
        kadena.get("balance",0),
        kadena.get("wallet_age_days",0),
        kadena.get("related_address_count",0),
        kadena.get("is_blacklisted",0)
    ]
    score = ai_score(features)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    validations.append({"timestamp":timestamp,"user":ip,"score":score,"address":address,"chain":chain})
    result = {"score":score,"timestamp":timestamp,"chain":chain,"address":address,"flags":[]}
    return JSONResponse(result)

@app.get("/export_iso20022")
async def export_iso20022(chain:str, address:str):
    for v in reversed(validations):
        if v["address"]==address and v["chain"]==chain:
            xml = f"""<Document>
    <Score>{v['score']}</Score>
    <Timestamp>{v['timestamp']}</Timestamp>
    <Chain>{v['chain']}</Chain>
    <Address>{v['address']}</Address>
</Document>"""
            return XMLResponse(content=xml)
    raise HTTPException(404, "No validation found.")

@app.get("/metrics")
async def get_metrics():
    return {"user_count":len(user_count), "validations":validations[-10:]}
