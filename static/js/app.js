/*==================================================
app.js - Main script for the basic functionality of
         Netengine graph visualizations.
==================================================*/

// GLOBALS
//==================================================
window.clickBehaviourOpts = {"properties":1, "addition":2, "deletion":3 }
Object.freeze(window.clickBehaviourOpts);
window.clickBehaviour = window.clickBehaviourOpts.properties; // Default behaviour
window.ROOT = '/RPGeNet'; // '';
window.drag = false;
window.cy;
window.layout;
window.nodeSize = "ns-enable";


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
 * Change Node Size
 */
changeNodeSize = function(cy) {
    window.nodeSize = $('input[name=node-size]:checked', '#node-size-form').val();
    if (window.nodeSize == "ns-enable") {
        cy.nodes().removeClass("no-node-size");
    } else {
        cy.nodes().addClass("no-node-size");
    }
}

/*
 * Change Layout
 */
 changeLayout = function(cy, layout) {
    layout = layout.toLowerCase();
    ur.do("layout", { options: {name: layout } });
 	//var thelayout = cy.layout( { name: layout } );
    //thelayout.run();
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
    /*
 	for (var key in jsonGraph.nodes) {
 		var node = jsonGraph.nodes[key].data.id;
 		nodes[node] = 1;
 	}
    */
    nodes = Object.keys(nodes).join("\n"); // to string
    edges['Parent\tChild\tType\tLevel\tEvidences'] = 1;
    for (var ekey in jsonGraph.edges) {
        var edge = jsonGraph.edges[ekey].data.id;
        edge = edge.replace(/-/g, "\t");
        edge = edge + "\t" + jsonGraph.edges[ekey].data.level;
        edge = edge + "\t" + jsonGraph.edges[ekey].data.ewidth;
        edges[edge] = 1;
    }
    edges = Object.keys(edges).join("\n"); // to string
    tblString = edges;
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
            window.layout = cy.layout({ name:  $("#layout").val().toLowerCase() });
            window.layout.run();
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
    if (! window.expId) {
        window.expId = "Absolute";
    }
    $.ajax({
        type: "GET",
        url: window.ROOT + "/add_neighbours",
        cache: true,
        data: {
            'gene': node.data().name,
            'level': window.level,
            'exp': window.expId,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        beforeSend: function() {
            $("#loading").show();
        },
        success : function(data) {
            console.log(data);
            ur.do("add", data);
            ur.do("layout", { options: {name: 'cola'} });
            changeNodeSize(cy);
            $("#loading").hide();
            //window.layout.stop()
            //window.layout = cy.layout({ name: 'cola' });
            //window.layout.run();
        },
        statusCode: {
            404: function() {
                $("#loading").hide();
            },
        },
        error: function(request, status, error) {
            alert(request.responseText);
            $("#loading").hide();
        }
    });
    //body
}

/*
 * Show node properties on click
 */
nPropertiesOnClick = function(cy, node) {
    $.ajax({
        type: "GET",
        url: window.ROOT + "/get_properties",
        cache: true,
        data: {
            'gene': node.data().name,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        beforeSend: function() {
            $("#loading").show();
        },
        success : function(data) {
            $('.card-overlay').html(data);
            $('.card-overlay').slideToggle(450);
            $('.close-overlay').slideToggle(450);
            $("#loading").hide();
        },
        statusCode: {
            404: function() {
                $("#loading").hide();
            },
        },
        error: function(xhr, status, error) {
            alert(xhr.responseText);
            $("#loading").hide();
        }
    });
}

/*
 * Show node properties on click
 */
ePropertiesOnClick = function(cy, edge) {
    $.ajax({
        type: "GET",
        url: window.ROOT + "/get_properties",
        cache: true,
        data: {
            'interaction': edge.data().id,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        beforeSend: function() {
            $("#loading").show();
        },
        success : function(data) {
            $('.card-overlay').html(data);
            $('.card-overlay').slideToggle(450);
            $('.close-overlay').slideToggle(450);
            $("#loading").hide();
        },
        statusCode: {
            404: function() {
                $("#loading").hide();
            },
        },
        error: function(xhr, status, error) {
            alert(xhr.responseText);
            $("#loading").hide();
        }
    });
}

/*
 * Defines behaviour when clicking on edge
 */
onEdgeClick = function(cy, edge) {
    if (window.clickBehaviour == window.clickBehaviourOpts.properties) {
        ePropertiesOnClick(cy, edge);
    }
}

/*
 * Defines behaviour when clicking on node
 */
onNodeClick = function(cy, node) {
    if (window.clickBehaviour == window.clickBehaviourOpts.addition) {
        expandOnClick(cy, node);
    } else if (window.clickBehaviour == window.clickBehaviourOpts.deletion) {
        if (cy.nodes(':selected').intersection(node).length) {
            ur.do("remove", cy.nodes(':selected'));
        } else {
            document.getElementById("cyt").style.cursor = 'not-allowed';
        }
    } else {
        nPropertiesOnClick(cy, node);
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

/*
 * Gets csrftoken for AJAX+POST
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/*
 * Get node Identifiers from cytoscape
 */
 getNodeIds = function(cy) {
    var nodes     = cy.nodes();
    var node_ids  = [];
    for (var i = 0; i < nodes.length; i++) {
        node_ids.push( nodes[i].data().name );
    }
    return node_ids.join(",");
 }

/*
 * Connects genes on visualization
 */
 showConnections = function(cy) {
    var csrftoken = getCookie('csrftoken');
    var nodeIds   = getNodeIds(cy);
    $.ajax({
        type: "POST",
        url: window.ROOT + "/show_connections",
        cache: true,
        data: {
            'nodes': nodeIds,
            'level': window.level,
            'csrfmiddlewaretoken': csrftoken
        },
        beforeSend: function() {
            $("#loading").show();

        },
        success : function(data) {
            ur.do("add", data);
            cy.layout( { name: 'cola' } );
            $("#loading").hide();
        },
        statusCode: {
            404: function() {
                $("#loading").hide();
            },
        },
        error: function(xhr, status, error) {
            alert(xhr.responseText);
            $("#loading").hide();
        }
    });
 }

/*
 * Removes unconnected nodes in visualization
 */
 removeUnconnected = function(cy) {
   ur.do("remove", cy.nodes('[[degree < 1]]'));
 }

/*
 * Searches gene or genes on visualization
 */
 searchNode = function(cy, term) {
    
    $("#search-node-results").html("");

    if (term) {
        $("#search-node-results-container").show();
        var terms = term.split(RegExp("[,\\s]")).map(function(x){ return x.toUpperCase() });
        console.log(terms);
        // Add terms to list of search results
        terms.forEach(element => {
            var elementHTML = "<span class='search-term not-found'>" + element.toUpperCase() + "</span>";
            $("#search-node-results").append(elementHTML);
        });
        

        // Highlight on graph
        cy.nodes().filter(function(ele, eidx, eles) {
            if (terms.indexOf(ele.data("name").toUpperCase()) !== -1) {
                var theSpan = $(".search-term:contains('" + ele.data("name").toUpperCase() + "')");
                theSpan.removeClass('not-found');
                theSpan.addClass('found');
                theSpan.append(' <span class="glyphicon glyphicon-zoom-in"></span>')
                return true;
                
            } else {
                return false;
            }
        }).select();
    } else {
        $("#search-node-results-container").hide();
    }
 }

/*
 * Changing expression color
 */
changeExpression = function(cy, exp_id) {
    var csrftoken = getCookie('csrftoken');
    var nodeIds   = getNodeIds(cy);
    window.expId = exp_id;
    $.ajax({
        type: "POST",
        url: window.ROOT + "/change_expression",
        cache: true,
        data: {
            'nodes': nodeIds,
            'level': window.level,
            'exp_id': exp_id,
            'csrfmiddlewaretoken': csrftoken
        },
        beforeSend: function() {
            $("#loading").show();
        },
        success : function(data) {
            var nodes = cy.nodes();
            console.log(data);
            for (var i = 0; i < nodes.length; i++) {
                nodeId = nodes[i].data().name;
                if (data.hasOwnProperty(nodeId)) {
                    nodes[i].data().color = data[nodeId];
                    nodes[i].css("background-color", data[nodeId]);
                } else {
                    nodes[i].data().color = "NA";
                    nodes[i].css("background-color", "#000000");
                }
            }
            $("#loading").hide();
        },
        statusCode: {
            404: function() {
                $("#loading").hide();
            },
        },
        error: function(xhr, status, error) {
            alert(xhr.responseText);
            $("#loading").hide();
        }
    });
}

unDo = function() {
    console.log("Undoing");
    ur.undo();
    fitScreen(window.cy);
}

reDo = function() {
    console.log("Redoing");
    ur.redo();
    fitScreen(window.cy);
}

// BUTTONS AND EVENTS
//==================================================
$('#behaviour-form').on("change", changeClickBehaviour);
$('#node-size-form').on("change", function() { changeNodeSize(window.cy) });
$("#layout").on("change", function() { changeLayout(window.cy, $(this).val())});
$("#fitscreen-btn").on("click", function() { fitScreen(window.cy) });
$("#save-img").on("click", function() { saveImg(window.cy, $('#save-image-link')) });
$("#export-tbl").on("click", function() { exportTBL(window.cy) });
$("#export-json").on("click", function() { exportJSON(window.cy) });
$('#drag-btn').on("click", function(event) { changeDrag(window.cy, event, $(this)) });
$("#bsize").on("change", function() { changeBsize(window.cy, $(this).val()) });
$("#get-connections").on('click', function() { showConnections(window.cy) });
$("#remove-unconnected").on('click', function() { removeUnconnected(window.cy) });
$("#search-node-btn").on("click", function(){ searchNode(window.cy, $("#search-node-term").val()) });
$("#removesearch").on("click", function(){ window.cy.nodes().unselect(); $("#search-node-results").html(""); $("#search-node-results-container").hide();});
$("#exp-indicator").on("change", function(){ changeExpression(window.cy, $(this).val())});
$("#undo-indicator").on("click", function(){ unDo(); });
$("#redo-indicator").on("click", function(){ reDo(); });
$('body').on('click', 'span.search-term.found', function() {
    // do something
    var nodeName = $(this).text();
    nodeName = nodeName.replace(/ /g, "");
    var selectorTerm = '[name="' + nodeName + '"]';
    cy.fit( cy.nodes(selectorTerm), 100); // 30 -> padding
    
});

window.cy.on( 'click', 'node', function() { onNodeClick(window.cy, this) });
window.cy.on( 'click', 'edge', function() { onEdgeClick(window.cy, this) });
window.cy.on('mouseover', 'node', function() { onNodeMouseOver(window.cy, this) });
window.cy.on('mouseout', 'node', function() {onNodeMouseOut(window.cy, this) });

// INITIALIZING CYTOSCAPE GRAPH
//==================================================
initGraph(window.cy, window.withpos);
