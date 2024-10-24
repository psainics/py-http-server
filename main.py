# pip install "fastapi[standard]" uvicorn jinja2
# uvicorn main:app --reload
# prod : 
# uvicorn main:app --host 0.0.0.0

# python3 -m venv venv
# source venv/bin/activate

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, JSONResponse 
import datetime
app = FastAPI()

request_logs = []

# csv data for patch testing
csv_data = """id,name,age
1,Alice,20
2,Bob,25
3,Charlie,30
4,Dave,35
5,Eve,40"""


def add_log_entry(path, method, body, auth_header, content_type, response_code):
    time_zone_kolkata = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    request_logs.append({
        "path": path,
        "method": method,
        "body": body,
        "auth_header": auth_header,
        "content_type": content_type,
        "timestamp": datetime.datetime.now(tz=time_zone_kolkata).strftime("%Y-%m-%d %H:%M:%S"), # format time IST
        "response_code": response_code 
    })


@app.delete("/api/{rest_of_path:path}")
async def read_item(request: Request, rest_of_path: str):
    api_path = request.url.path
    add_log_entry(api_path, "DELETE", await request.body(), request.headers.get("Authorization"), request.headers.get("Content-Type"), 200)
    return {"message": "ok!"}

@app.get("/api/{rest_of_path:path}")
async def read_item(request: Request, rest_of_path: str):
    api_path = request.url.path
    add_log_entry(api_path, "GET", await request.body(), request.headers.get("Authorization"), request.headers.get("Content-Type"), 200)
    return {"message": "ok!"}

import random as rand
@app.post("/api/{rest_of_path:path}")
async def read_item(request: Request, rest_of_path: str):
    api_path = request.url.path
    return_code = 200
    # one in 10 chance of returning 500
    random_num = rand.randint(1, 10)
    if random_num == 1:
        return_code = 400
    add_log_entry(api_path, "POST", await request.body(), request.headers.get("Authorization"), request.headers.get("Content-Type"), return_code)
    if return_code == 400:
        return JSONResponse(content='{ "message": "error!" }', status_code=400)
    return {"message": "ok!"}

@app.put("/api/{rest_of_path:path}")
async def read_item(request: Request, rest_of_path: str):
    api_path = request.url.path
    add_log_entry(api_path, "PUT", await request.body(), request.headers.get("Authorization"), request.headers.get("Content-Type"), 200)
    return {"message": "ok!"}

@app.patch("/api/{rest_of_path:path}")
async def read_item(request: Request, rest_of_path: str):
    api_path = request.url.path
    add_log_entry(api_path, "PATCH", await request.body(), request.headers.get("Authorization"), request.headers.get("Content-Type"), 200)
    if rest_of_path == "data":
        # return as csv
        return PlainTextResponse(content="".join(csv_data), media_type="text/csv")
    return {"message": "ok!"}


## Reject API
rejectMessageMap = {}
reject_num_msg = 5 
reject_count = 5
@app.post("/retry")
async def read_item(request: Request):
    api_path = request.url.path
    body = await request.body()
    if len(request_logs) < reject_num_msg:
        add_log_entry(api_path, "POST", body, request.headers.get("Authorization"), request.headers.get("Content-Type"), 200)
        return {"message": "ok!"}
    else:
        request_body = body.decode("utf-8")
        rejected_count = rejectMessageMap.get(request_body, 0)  
        if rejected_count >= reject_count:
            add_log_entry(api_path, "POST", body, request.headers.get("Authorization"), request.headers.get("Content-Type"), 200)
            return {"message": "ok!"}
        else:
            rejectMessageMap[request_body] = rejected_count + 1
            reject_code = 429
            add_log_entry(api_path, "POST", body, request.headers.get("Authorization"), request.headers.get("Content-Type"), reject_code)
            return JSONResponse(content='{ "message": "rejected!" }', status_code=reject_code)
        
@app.patch("/retry")
async def read_item(request: Request):
    api_path = request.url.path
    body = await request.body()
    if len(request_logs) < reject_num_msg:
        add_log_entry(api_path, "PATCH", body, request.headers.get("Authorization"), request.headers.get("Content-Type"), 200)
        return {"message": "ok!"}
    else:
        request_body = body.decode("utf-8")
        rejected_count = rejectMessageMap.get(request_body, 0)  
        if rejected_count >= reject_count:
            add_log_entry(api_path, "PATCH", body, request.headers.get("Authorization"), request.headers.get("Content-Type"), 200)
            return {"message": "ok!"}
        else:
            rejectMessageMap[request_body] = rejected_count + 1
            reject_code = 429
            add_log_entry(api_path, "PATCH", body, request.headers.get("Authorization"), request.headers.get("Content-Type"), reject_code)
            return Response(content='{ "message": "rejected!" }', status_code=reject_code, media_type="application/json") 


# Dashboard API
@app.get("/dash/", response_class=PlainTextResponse)
async def read_item(request: Request):
    out_logs = "##### DASHBOARD #####\n\n\n\n\n"
    for log in request_logs:
        body_utf_8 = log["body"].decode("utf-8")
        if body_utf_8 == "":
            body_utf_8 = "None"
        out_logs += "----------REQ-START----------\n"
        out_logs += f"Timestamp: {log['timestamp']}\n\n"
        out_logs += f"Method: {log['method']} {log['path']}\n"
        out_logs += f"Response Code: {log['response_code']}\n"
        out_logs += f"Auth Header: {log['auth_header']}\n"
        out_logs += f"Content-Type: {log['content_type']}\n"
        out_logs += f"Body: ⬇️\n"
        out_logs += f"{body_utf_8}\n"
        out_logs += "----------REQ---END----------\n\n\n\n\n"
    return out_logs

@app.get("/dash/reset", response_class=PlainTextResponse)
async def read_item(request: Request):
    global request_logs
    request_logs = []
    global rejectMessageMap
    rejectMessageMap = {}
    return "Logs cleared!"