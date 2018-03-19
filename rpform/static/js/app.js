/*==================================================
app.js - Main script for the basic functionality of 
         Netengine graph visualizations.
==================================================*/


// GLOBALS
//==================================================
window.clickBehaviourOpts = {"properties":1, "addition":2, "deletion":3 }
window.clickBehaviour = window.clickBehaviourOpts.addition;
Object.freeze(window.clickBehaviourOpts);
window.cy;


// FUNCTIONS
//==================================================

/*
 * Change Click Behaviour
 */
changeClickBehaviour = function() {
    var behaviour = $('input[name=behaviour]:checked', '#behaviour-form').val();
    window.clickBehaviour = window.clickBehaviourOpts[behaviour];
}

/*
 * Change Layout
 */
 changeLayout = function(cy, layout) {
    layout = layout.toLowerCase();
 	cy.layout( { name: layout } );
 }

/*
 * Converts base64 img to Blob
 */
function b64ToBlob(b64Data, contentType, sliceSize) {
  contentType = contentType || '';
  sliceSize = sliceSize || 512;

  var byteCharacters = atob(b64Data);
  var byteArrays = [];

  for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    var slice = byteCharacters.slice(offset, offset + sliceSize);

    var byteNumbers = new Array(slice.length);
    for (var i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    var byteArray = new Uint8Array(byteNumbers);

    byteArrays.push(byteArray);
  }

  var blob = new Blob(byteArrays, {type: contentType});
  return blob;
}


/*
 * Save Image of Graph
 */
 saveImg = function(cy, link) {
    var b64key = 'base64,';
    var b64 = cy.png().substring( cy.png().indexOf(b64key) + b64key.length );
    var imgBlob = b64ToBlob( b64, 'image/png' );
    saveAs( imgBlob, 'graph.png' );
 };


/*
 * Fit Graph to screen
 */
 fitScreen = function(cy) {
	cy.center();
    cy.fit();
 };

 /*
 * ChangeDrag
 */
 changeDrag = function(cy, event, elem) {
    event.preventDefault;
    if (elem.hasClass('active')) {
        // Disable drag, enable boxselection
        cy.boxSelectionEnabled( true );
        elem.removeClass('active');
    } else {
        // Disable boxselection, enable drag
        cy.boxSelectionEnabled( false );
        elem.addClass('active');
    }
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

/*
 * Initializes graph
 */
 initGraph = function(cy, withpos) {
    cy.add(window.jsongraph);
    if (! withpos) {
        cy.layout({ name:  $("#layout").val().toLowerCase() });
    }
    window.jsongraph = {};
 }



// BUTTON EVENTS
//==================================================
$('#behaviour-form').on("change", changeClickBehaviour);
$("#layout").on("change", function() { changeLayout(window.cy, $(this).val())});
$("#fitscreen-btn").on("click", function() { fitScreen(window.cy) });
$("#save-img").on("click", function() { saveImg(window.cy, $('#save-image-link')) });
$("#export-tbl").on("click", function() { exportTBL(window.cy) });
$("#export-json").on("click", function() { exportJSON(window.cy) });
$('#drag-btn').on("click", function(event) { changeDrag(window.cy, event, $(this)) });

// INITIALIZING CYTOSCAPE GRAPH
//==================================================
initGraph(window.cy, window.withpos);