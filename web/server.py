from flask import Flask, render_template
from flask import request as req
import requests

app = Flask(__name__)

# Root path (static)
@app.route("/")
@app.route("/index")
def index():
       return render_template('index.html')

# Render a table of chemicals reachable from a start chemical by querying the
# biochem4j.org graph DB. The final column contains a link to the /pathway link.
@app.route("/chemical")
def chemical():
    # create the graph DB query
    max_length_chems = int(req.args.get("max_len", "0"))
    max_length_rels = (max_length_chems - 1) * 2
    query = """
MATCH shortestPath((s:Chemical)<-[r:has_reactant*1..%d]->(t:Chemical {id: '%s'}))
WITH s, r, t, range(0, size(r)-2) as idx
WHERE ALL (i IN idx WHERE r[i]['stoichiometry'] * r[i+1]['stoichiometry'] < 0)
AND s.monoisotopic_mass > %s
RETURN s.name, s.id, s.formula, size(r) as len""" % (max_length_rels, req.args.get("chem_id", ""),
        req.args.get("min_mw", ""))
    print(query)

    # send the graph DB query request
    r = requests.post('http://biochem4j.org/db/data/transaction/commit',
        headers={'accept': 'application/json', 'content-type': 'application/json'},
        json={"statements":[{"statement": query}]})
    if r.status_code != 200:
        return "Error (%d): %s" % (r.status_code, r.text)
    
    # populate info needed for rendering the table
    fromChemical = {"id": req.args.get("chem_id", "")}
    chemicals = []
    for row_data in r.json()["results"][0]["data"]:
        row = row_data["row"]
        chemicals.append({"name": row[0], "id": row[1], "formula": row[2],
            "path_length": int(row[3] / 2 + 1)})

    return render_template('chemicals.html', fromChemical=fromChemical, chemicals=chemicals)

# Render an interactive graph visualization with vis.js of the pathway between two chemicals.
@app.route("/pathway")
def pathway():
    # create the graph DB query
    path_length_chems = int(req.args.get("path_len", "0"))
    max_length_rels = (path_length_chems - 1) * 2
    query = """
MATCH p=shortestPath((s:Chemical {id:'%s'})<-[r:has_reactant*1..%d]->(t:Chemical {id: '%s'}))
WITH p, s, r, t, range(0, size(r)-2) as idx
WHERE ALL (i IN idx WHERE r[i]['stoichiometry'] * r[i+1]['stoichiometry'] < 0)
RETURN p""" % (req.args.get("id1", ""), max_length_rels, req.args.get("id2", ""))
    print(query)

    # send the graph DB query request
    r = requests.post('http://biochem4j.org/db/data/transaction/commit',
        headers={'accept': 'application/json', 'content-type': 'application/json'},
        json={"statements":[{"statement": query}]})
    if r.status_code != 200:
        return "Error (%d): %s" % (r.status_code, r.text)

    meta = {"fromId": req.args.get("id1", ""), "toId": req.args.get("id2", ""),}

    # populate nodes and edges need for rendering the graph view
    i = 0
    nodes = []
    edges = []
    for row_data in r.json()["results"][0]["data"]:
        for elem in row_data["row"][0]:
            if "smiles" in elem: # chemical node
                nodes.append({"index": i, "name": elem["name"], "color": "cyan"})
                if i > 0:
                    edges.append({"node1": i - 1, "node2": i})
                i = i + 1
            elif "balance" in elem: # reaction node
                nodes.append({"index": i, "name": elem["id"], "color": "red"})
                if i > 0:
                    edges.append({"node1": i - 1, "node2": i})
                i = i + 1
            else: # other node or reference
                pass

    return render_template('pathway.html', meta=meta, nodes=nodes, edges=edges)

# Path for the AWS load balancer to ping to check health status
@app.route("/ping")
def ping():
    return "OK"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
