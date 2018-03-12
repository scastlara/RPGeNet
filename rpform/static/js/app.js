// GLOBALS
window.clickBehaviourOpts = {"addition":1, "deletion":2, "properties":3}
window.clickBehaviour = window.clickBehaviourOpts.addition;
Object.freeze(window.clickBehaviourOpts);
window.cy;


// FUNCTIONS

/*
 * Changes the click behaviour mode
 */
changeClickBehaviour = function(this, mode) {
	$(".behaviour-btn").removeClass("active");
	$(this).addClass("active");
	window.clickBehaviour = window.clickBehaviourOpts[mode];
};

/*
 * Change Layout
 */
 changeLayout = function(cy, layout) {
 	cy.layout( { name: layout } );
 }


/*
 * Save Image of Graph
 */
 saveImg = function(cy, link) {
	var graph_png = cy.png();
	link.attr('href', graph_png);
 };


/*
 * Fit Graph to screen
 */
 fitScreen = function(cy) {
	cy.center();
    cy.fit();
 };

/*
 * Exports graph as a TBL file
 */
 exportTBL = function(cy) {
 	var jsonGraph = cy.json().elements;
 	var nodes     = {};
 	var edges     = {};
 	for (var key in jsonGraph.nodes) {
 		var node = jsonGraph.nodes[key].data.id;
 		nodes[node] = 1;
 	}
    nodes = Object.keys(nodes).join("\n"); // to string

    for (var ekey in jsonGraph.edges) {
        var edge = jsonGraph.edges[ekey].data.id;
        edge = edge.replace("-", "\t");
        edge = edge + "\t" + jsonGraph.edges[ekey].data.probability;
        edges[edge] = 1;
    }
    edges = Object.keys(edges).join("\n"); // to string
    tblString = nodes + "\n" + edges;
    var blob = new Blob([tblString], {type: "text/plain;charset=utf-8"});
    saveAs(blob, "graph-export.tbl");
};

/*
 * Exports graph as a JSON file, ready to be uploaded
 */
exportJSON = function(cy) {
	var jsonGraph = JSON.stringify(cy.json().elements);
    var blob = new Blob([jsonGraph], {type: "text/plain;charset=utf-8"});
    saveAs(blob, "graph-export.json");
}

// BUTTON EVENTS
$("#node-addition-btn").on("click", changeClickBehaviour(this, "addition"));
$("#node-deletion-btn").on("click", changeClickBehaviour(this, "deletion"));
$("#node-properties-btn").on("click", changeClickBehaviour(this, "properties"))
$("#change-layout li").on("click", changeLayout(window.cy, $(this).text().toLowerCase()));
$("#fitscreen-btn").on("click", fitScreen(window.cy));
$("#save-img").on("click", saveImg(window.cy, $('#save-image-link')));
$("#export-tbl").on("click", exportTBL(window.cy));
$("#export-json").on("click", exportJSON(window.cy));
