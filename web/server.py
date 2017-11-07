from flask import Flask, render_template
from flask import request as req
import requests
import json

app = Flask(__name__)

@app.route("/chemical")
def chemical():
    query = """
MATCH allShortestPaths((s:Chemical)<-[r:has_reactant*1..%s]->(t:Chemical {id: 'CHEBI:%s'}))
WITH s, r, t, range(0, size(r)-2) as idx
WHERE ALL (i IN idx WHERE r[i]['stoichiometry'] * r[i+1]['stoichiometry'] < 0)
AND s.monoisotopic_mass > %s
RETURN s.name, s.id, s.formula, size(r) as len""" % (req.args.get("max_length", ""), req.args.get("chebi", ""),
        req.args.get("min_mw", ""))
    print(query)

    r = requests.post('http://biochem4j.org/db/data/transaction/commit',
        headers={'accept': 'application/json', 'content-type': 'application/json'},
        json={"statements":[{"statement": query}]})
    if r.status_code != 200:
        return "Error (%d): %s" % (r.status_code, r.text)
    
    print(json.dumps(r.json(), indent=4, sort_keys=True))

    table_html = "<table id='table'><tr>\n<th>Name</th><th>Id</th><th>Formula</th><th>Path Length</th></tr>\n"
    for row_data in r.json()["results"][0]["data"]:
        row = row_data["row"]

        table_html += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td></tr>\n" % \
            (row[0], row[1], row[2], row[3], row[4])
    table_html += "</td></table>"

    return """
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="static/main.css">
</head>
<body>
%s
</body>
</html>
""" % (table_html)

@app.route("/path")
def path():
    query = """
MATCH p=allShortestPaths((s:Chemical {id:'%s'})<-[r:has_reactant*1..%s]->(t:Chemical {id: '%s'}))
WITH p, s, r, t, range(0, size(r)-2) as idx
WHERE ALL (i IN idx WHERE r[i]['stoichiometry'] * r[i+1]['stoichiometry'] < 0)
RETURN p""" % (req.args.get("id1", ""), req.args.get("max_len", ""), req.args.get("id2", ""))
    print(query)

    r = requests.post('http://biochem4j.org/db/data/transaction/commit',
        headers={'accept': 'application/json', 'content-type': 'application/json'},
        json={"statements":[{"statement": query}]})
    if r.status_code != 200:
        return "Error (%d): %s" % (r.status_code, r.text)
    
    print(json.dumps(r.json(), indent=4, sort_keys=True))

    # populate nodes and edges for graph view
    i = 0
    nodes = []
    edges = []
    for row_data in r.json()["results"][0]["data"]:
        for elem in row_data["row"][0]:
            if "smiles" in elem:
                nodes.append({"index": i, "name": elem["name"], "color": "cyan"})
                if i > 0:
                    edges.append({"node1": i - 1, "node2": i})
                i = i + 1
            elif "balance" in elem:
                nodes.append({"index": i, "name": elem["id"], "color": "red"})
                if i > 0:
                    edges.append({"node1": i - 1, "node2": i})
                i = i + 1

    # return r.text
    return render_template('pathway.html', nodes=nodes, edges=edges)
