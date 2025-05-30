from fastapi import FastAPI, Request
from pydantic import BaseModel
from twilio.rest import Client
import logging
import os

app = FastAPI()

AGENTS = {
    "vivint": {
        "account_sid": "ACbbace97fe5214af20a891058de106992",
        "auth_token": "25e904f282c41c05bf64e8987ae6aa32",
        "twiml_url": "https://handler.twilio.com/twiml/EH16d1025f49633d5a5b5de535be71a17b"
    }
}

class TransferRequest(BaseModel):
    call_sid: str

@app.post("/transfer")
async def transfer_call(request: Request):
    agent = request.query_params.get("agent")
    data = await request.json()

    call_sid = data.get("call_sid") or data.get("CallSid")

    logging.info(f"Transfer requested for agent: {agent}, call_sid: {call_sid}")

    if not agent or agent not in AGENTS:
        return {"error": "Agent not found"}
    if not call_sid:
        return {"error": "Missing call_sid"}

    try:
        twilio = Client(AGENTS[agent]["account_sid"], AGENTS[agent]["auth_token"])
        twilio.calls(call_sid).update(url=AGENTS[agent]["twiml_url"])
        return {"success": "Call transferred", "call_sid": call_sid}
    except Exception as e:
        logging.error(f"Transfer failed: {e}")
        return {"error": "Call transfer failed", "message": str(e)}
