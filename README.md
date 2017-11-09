### chemdb

Basic prototype of a chemoinformatics server for searching biosynthetic pathways.

Available on AWS at http://chemdb2.us-west-1.elasticbeanstalk.com.

This app allows search for new molecules that could potentially be made via a biosynthetic pathway. It has 3 pages:
1. The main page lets you search for a pathway from a start chemical (using a CHEBI or MNX id), filtering by minimum molecular weight and length of the pathway.
2. Submitting the above page feeds to the chemical results page which displays a table with some information about the resulting chemicals that are potentially synthesizable.
3. Clicking on the `Path Length` link at the end of any row on the above page shows a graph visualization of the pathway including chemical intermediates and MNX reaction ids.

It uses the data put together by this paper http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0179130 as the backend graph DB store. This is currently used remotely at http://biochem4j.org but it could be loaded into a docker container for customization and hosted on AWS.
