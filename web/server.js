var express = require('express')
var app = express()
var unirest = require('unirest');
var util = require('util');

app.use(express.static('public'))

app.get('/query', function (req, res) {
	var query = util.format(`
MATCH allShortestPaths((s:Chemical)<-[r:has_reactant*1..%d]->(t:Chemical {id: 'CHEBI:%d'}))
WITH s, r, t, range(0, size(r)-2) as idx
WHERE ALL (i IN idx WHERE r[i]['stoichiometry'] * r[i+1]['stoichiometry'] < 0)
AND s.monoisotopic_mass > %d
RETURN s`,
	req.query.max_length, req.query.chebi, req.query.min_mw);
	console.log(query);

	unirest.post('http://biochem4j.org/db/data/transaction/commit')
		.headers({'accept': 'application/json', 'content-type': 'application/json'})
		.send({"statements":[{"statement": query}]})
		.end(function (response) {
			console.log(response);
			if (response.error) {
				console.log("ERROR")
			} else {
	  			res.send(response.body);
	  		}
		});
});

app.listen(8080, () => console.log('Listening on port 8080!'))
