#!/usr/bin/env python3
"""Databricks helper for the ABF project — avoids heredocs/$(...) that trigger
permission prompts. Reads host+token from ~/.tubi-sql/config.yml itself.

Usage:
  python3 abf_db.py sql "<inline sql>"          # run SQL, print JSON rows
  python3 abf_db.py sqlfile <path.sql>          # run SQL from a file, print JSON rows
  python3 abf_db.py upload <local.py> <ws_path> # import a notebook (SOURCE/PYTHON, overwrite)
  python3 abf_db.py run <ws_path> <run_name>    # submit serverless run, poll 60s, print exit result
  python3 abf_db.py mkdir <ws_path>             # create workspace folder
  python3 abf_db.py copy <src_ws> <dst_ws>      # export+import a notebook copy (archive)
"""
import sys, json, time, base64, urllib.request, urllib.error, os, re

CFG = os.path.expanduser("~/.tubi-sql/config.yml")
WAREHOUSE_ID = "34148fb208740945"


def _cfg():
    host = token = None
    with open(CFG) as f:
        for line in f:
            m = re.match(r'\s*databricks_host:\s*(.+)\s*$', line)
            if m:
                host = m.group(1).strip().strip('"\'')
            m = re.match(r'\s*databricks_token:\s*(.+)\s*$', line)
            if m:
                token = m.group(1).strip().strip('"\'')
    if not host.startswith("http"):
        host = "https://" + host
    return host.rstrip("/"), token


HOST, TOKEN = _cfg()


def _api(path, payload=None, method=None, params=None):
    url = HOST + path
    if params:
        from urllib.parse import urlencode
        url += "?" + urlencode(params)
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.stderr.write(e.read().decode() + "\n")
        raise


def run_sql(sql):
    r = _api("/api/2.0/sql/statements/", {
        "warehouse_id": WAREHOUSE_ID, "statement": sql, "wait_timeout": "50s",
        "format": "JSON_ARRAY", "disposition": "INLINE",
    })
    sid = r["statement_id"]
    while r["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(2)
        r = _api("/api/2.0/sql/statements/" + sid)
    st = r["status"]["state"]
    if st != "SUCCEEDED":
        print(json.dumps(r["status"], indent=2)); sys.exit(1)
    cols = [c["name"] for c in r["manifest"]["schema"]["columns"]]
    rows = r.get("result", {}).get("data_array", []) or []
    print(json.dumps({"columns": cols, "rows": rows}, default=str, indent=2))


def upload(local, ws_path):
    content = base64.b64encode(open(local, "rb").read()).decode()
    _api("/api/2.0/workspace/import", {
        "path": ws_path, "format": "SOURCE", "language": "PYTHON",
        "overwrite": True, "content": content})
    print("uploaded ->", ws_path)


def submit_run(ws_path, run_name, base_parameters=None):
    notebook_task = {"notebook_path": ws_path}
    if base_parameters:
        notebook_task["base_parameters"] = base_parameters
    r = _api("/api/2.1/jobs/runs/submit", {
        "run_name": run_name,
        "tasks": [{"task_key": run_name.replace("/", "_")[:80],
                   "notebook_task": notebook_task,
                   "environment_key": "serverless"}],
        "environments": [{"environment_key": "serverless", "spec": {"client": "2"}}]})
    run_id = r["run_id"]
    print("run_id:", run_id, flush=True)
    while True:
        s = _api("/api/2.1/jobs/runs/get", params={"run_id": run_id})
        life = s["state"]["life_cycle_state"]
        print(time.strftime("%H:%M:%S"), "life:", life, flush=True)
        if life in ("TERMINATED", "INTERNAL_ERROR", "SKIPPED"):
            print("result:", s["state"].get("result_state"))
            tr = s["tasks"][0]["run_id"]
            out = _api("/api/2.1/jobs/runs/get-output", params={"run_id": tr})
            no = out.get("notebook_output", {})
            print("EXIT_RESULT:", no.get("result", ""))
            if out.get("error"):
                print("ERROR:", out["error"][:2000])
            break
        time.sleep(60)


def mkdir(ws_path):
    _api("/api/2.0/workspace/mkdirs", {"path": ws_path}); print("mkdir ok:", ws_path)


def delete(ws_path):
    _api("/api/2.0/workspace/delete", {"path": ws_path, "recursive": False})
    print("deleted:", ws_path)


def copy(src, dst):
    e = _api("/api/2.0/workspace/export", params={"path": src, "format": "SOURCE"})
    _api("/api/2.0/workspace/import", {
        "path": dst, "format": "SOURCE", "language": "PYTHON",
        "overwrite": True, "content": e["content"]})
    print("copied", src, "->", dst)


def export_run(run_id, dst_ws):
    """Pull the rendered HTML (code + outputs) of a completed job run and import it
    into the workspace as an HTML notebook (outputs visible inline)."""
    r = _api("/api/2.1/jobs/runs/export", params={"run_id": run_id, "views_to_export": "CODE"})
    views = r.get("views", [])
    if not views:
        print("no views for run", run_id); return
    html = views[0]["content"]            # raw HTML string from runs/export
    enc = base64.b64encode(html.encode("utf-8")).decode()
    _api("/api/2.0/workspace/import", {
        "path": dst_ws, "format": "HTML", "language": "PYTHON",
        "overwrite": True, "content": enc})
    print("exported run", run_id, "->", dst_ws)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sql":
        run_sql(sys.argv[2])
    elif cmd == "sqlfile":
        run_sql(open(sys.argv[2]).read())
    elif cmd == "upload":
        upload(sys.argv[2], sys.argv[3])
    elif cmd == "run":
        # optional 4th arg: notebook base_parameters as either inline JSON, or @path to a JSON file
        bp = None
        if len(sys.argv) > 4:
            a = sys.argv[4]
            bp = json.load(open(a[1:])) if a.startswith("@") else json.loads(a)
        submit_run(sys.argv[2], sys.argv[3], bp)
    elif cmd == "mkdir":
        mkdir(sys.argv[2])
    elif cmd == "copy":
        copy(sys.argv[2], sys.argv[3])
    elif cmd == "export_run":
        export_run(sys.argv[2], sys.argv[3])
    elif cmd == "delete":
        delete(sys.argv[2])
    else:
        print(__doc__); sys.exit(1)
