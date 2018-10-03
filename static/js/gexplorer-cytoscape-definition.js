/*==================================================
gexplorer-cytoscape-definition.js - 
    Definition of cytoscape options for gexplorer
==================================================*/

// Cytoscape style definition
var stylesheet = cytoscape.stylesheet()
    
    .selector('node')
        .css({
            'content': 'data(name)',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'background-color': 'data(color)',
            "font-size": 14,
            'text-outline-width': 2,
            "text-outline-color": "#FFFFFF",
            "color": "#404040",
            "border-width": 8,
            "min-zoomed-font-size": 3,
            'width':  'mapData(nvariants, 1, 500, 25, 200)',
            'height': 'mapData(nvariants, 1, 500, 25, 200)',
        })
    .selector(':selected')
        .css({
            "background-color": "#3A9F88",
            "font-size": 18,
            "color": "#3A9F88",
            "text-background-opacity": 1,
            "text-background-color": "#ccc",
            "text-background-shape": "roundrectangle",

        })
    .selector('.driver')
        .css({
            'border-color': '#793d71',
        })
    .selector('.syndromic')
        .css({
            'shape': 'rectangle',
        })
    .selector('.non-syndromic')
        .css({
            'shape': 'diamond',
        })
    .selector('.both')
        .css({
            'shape': 'star',
        })
    .selector('.skeleton')
     .css({
        "border-color": "#CCCCCC",
        })
    .selector('.lvl1')
     .css({
        "border-color": "#C0EFBA",
        })
    .selector('.lvl2')
     .css({
        "border-color": "#5AD55A",
        })
    .selector('.lvl3')
     .css({
        "border-color": "#0A945C",
        })
    .selector('.lvl4')
     .css({
        "border-color": "#426A2B",
        })
    .selector('.lvl5')
     .css({
        "border-color": "#1E3610",
    })
    .selector('edge')
        .css({
            'color': "#4F8ABA",
            'line-color': '#4F8ABA',
            'curve-style': 'bezier',
            'target-arrow-color': '#4F8ABA',
            'target-arrow-shape': 'triangle',
            "width": "mapData(ewidth, 1, 9, 1, 5)",
            "opacity": "mapData(ewidth, 1, 9, 0.75, 1)",
        })
    .selector('.physical')
        .css({
            'line-color': '#FF8A8A',
            'target-arrow-color': '#FF8A8A',
        })
    .selector('.genetic')
        .css({
            'line-color': '#6885d0',
            'target-arrow-color': '#6885d0',
        })
    .selector('.unknown')
        .css({
            'line-color': '#5B5B5B',
            'target-arrow-color': '#5B5B5B',
        })
    .selector(':selected')
        .css({
            'line-color': '#3A9F88',
            'target-arrow-color': '#3A9F88',
        })
    .selector('.no-node-size')
        .css({
            'width':  '30',
            'height': '30'
        });
    


// Cytoscape variable definition
var cy = cytoscape({
    style: stylesheet,
    layout: { name: 'preset' },
    container: document.getElementById('cyt'),
    boxSelectionEnabled: true,  
    ready: function() {}
});
var urOptions = {
            isDebug: false, // Debug mode for console messages
            actions: {},// actions to be added
            undoableDrag: true, // Whether dragging nodes are undoable can be a function as well
            stackSizeLimit: 5, // Size limit of undo stack, note that the size of redo stack cannot exceed size of undo stack
            ready: function () { // callback when undo-redo is ready

    }
};
var ur = cy.undoRedo(urOptions);
