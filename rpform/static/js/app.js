/*==================================================
app.js - Main script for the basic functionality of 
         Netengine graph visualizations.
==================================================*/


// GLOBALS
//==================================================
window.clickBehaviourOpts = {"properties":1, "addition":2, "deletion":3 }
window.clickBehaviour = window.clickBehaviourOpts.addition;
Object.freeze(window.clickBehaviourOpts);
window.drag = false;
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
        window.drag = false;
        document.getElementById("cyt").style.cursor = 'auto';
        cy.boxSelectionEnabled( true );
        elem.removeClass('active');
    } else {
        // Disable boxselection, enable drag
        window.drag = true;
        document.getElementById("cyt").style.cursor = 'all-scroll';
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
 * Change Border size of nodes
 */
 changeBsize = function(cy, value) {
    cy.nodes().css({'border-width': value});
 }

/*
 * Shows error message for uploading graph again
 */
 jsonError = function() {
    $("#no-results-title").html("<span class='glyphicon glyphicon-warning-sign text-danger'></span> Not a valid graph file");
    $("#blur-effect").show();
    $("#no-results-dialog").show();
 }

/*
 * Initializes graph
 */
 initGraph = function(cy, withpos) {
    if (window.notjson) {
        jsonError();
    } else {
        if (window.jsongraph) {
            // Check that json graph file/data is correct
            try   { 
                cy.add(window.jsongraph);
            } 
            catch (error) { 
                jsonError();
            }
        }
        if (! withpos) {
            cy.layout({ name:  $("#layout").val().toLowerCase() });
        }
        window.jsongraph = {};
        var defaults = ({
            zoomFactor: 0.05, // zoom factor per zoom tick
            zoomDelay: 45, // how many ms between zoom ticks
            minZoom: 0.1, // min zoom level
            maxZoom: 10, // max zoom level
            fitPadding: 50, // padding when fitting
            panSpeed: 10, // how many ms in between pan ticks
            panDistance: 10, // max pan distance per tick
            panDragAreaSize: 75, // the length of the pan drag box in which the vector for panning is calculated (bigger = finer control of pan speed and direction)
            panMinPercentSpeed: 0.25, // the slowest speed we can pan by (as a percent of panSpeed)
            panInactiveArea: 8, // radius of inactive area in pan drag box
            panIndicatorMinOpacity: 0.5, // min opacity of pan indicator (the draggable nib); scales from this to 1.0
            autodisableForMobile: true, // disable the panzoom completely for mobile (since we don't really need it with gestures like pinch to zoom)
            // icon class names
            sliderHandleIcon: '',
            zoomInIcon: 'glyphicon glyphicon-plus',
            zoomOutIcon: 'glyphicon glyphicon-minus',
            resetIcon: 'glyphicon glyphicon-fullscreen'
        });
        if (cy.nodes().length) {
            cy.navigator({});
            cy.panzoom(defaults);
        }
    }
 }

 /*
 * AJAX call to retrieve node interactions in DB
 */
expandOnClick = function(cy, node) {
    $.ajax({
        type: "GET",
        url: "/add_neighbours",
        cache: true,
        data: {
            'gene': node.data().name,
            'level': window.level,
            'exp': window.expId,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        beforeSend: function() {
            
        },
        success : function(data) {
            cy.add(data);
            cy.layout( { name: 'cose' } );
        }, 
        statusCode: {
            404: function() {

            },
        },
        error: function() {
            alert("ERROR");
        }
    });
    //body
}

/*
 * Show node properties on click
 */ 
propertiesOnClick = function(cy, node) {
    //body
}

/*
 * Defines behaviour when clicking on node
 */
onNodeClick = function(cy, node) {
    if (window.clickBehaviour == window.clickBehaviourOpts.addition) {
        expandOnClick(cy, node);
    } else if (window.clickBehaviour == window.clickBehaviourOpts.deletion) {
        if (cy.nodes(':selected').intersection(node).length) {
            cy.nodes(':selected').remove();
        } else {
            document.getElementById("cyt").style.cursor = 'not-allowed';
        }
    } else {
        propertiesOnClick(cy, node);
    }
}

/*
 * Defines behaviour when hovering on node
 */
 onNodeMouseOver = function(cy, node) {
    if (window.clickBehaviour == window.clickBehaviourOpts.deletion) {
        if (cy.nodes(':selected').intersection(node).length) {
            document.getElementById("cyt").style.cursor = 'not-allowed';
        } else {
            document.getElementById("cyt").style.cursor = 'auto';
        }
    } else if (window.clickBehaviour == window.clickBehaviourOpts.properties) {
        if (cy.nodes(':selected').intersection(node).length == 0) {
            document.getElementById("cyt").style.cursor = 'context-menu';
        } else {
            document.getElementById("cyt").style.cursor = 'auto';
        }
    } else if (window.clickBehaviour == window.clickBehaviourOpts.addition) {
        document.getElementById("cyt").style.cursor = 'pointer';
    }
 }

 /*
 * Defines behaviour when out-hovering on node
 */
 onNodeMouseOut = function(cy, node) {
    if (window.drag) {
        document.getElementById("cyt").style.cursor = 'all-scroll';
    } else {
        document.getElementById("cyt").style.cursor = 'auto';
    }
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
$("#bsize").on("change", function() { changeBsize(window.cy, $(this).val())});
window.cy.on( 'click', 'node', function() { onNodeClick(window.cy, this) });
window.cy.on('mouseover', 'node', function() { onNodeMouseOver(window.cy, this)});
window.cy.on('mouseout', 'node', function() {onNodeMouseOut(window.cy, this)});

// INITIALIZING CYTOSCAPE GRAPH
//==================================================
initGraph(window.cy, window.withpos);