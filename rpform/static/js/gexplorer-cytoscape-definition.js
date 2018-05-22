/*==================================================
gexplorer-cytoscape-definition.js - 
    Definition of cytoscape options for gexplorer
==================================================*/

// Cytoscape style definition
var stylesheet = cytoscape.stylesheet()
    
    .selector('node')
        .css({
            'content': 'data(name)',
            'text-valign': 'top',
            'text-halign': 'center',
            'background-color': '#2CA089',
            "font-size": 14,
            'text-outline-width': 2,
            "text-outline-color": "#FFFFFF",
            "color": "#404040",
            "border-color": "#CCCCCC",
            "border-width": 8,
            "min-zoomed-font-size": 3,
            'width':  'mapData(nvariants, 1, 500, 25, 200)',
            'height': 'mapData(nvariants, 1, 500, 25, 200)',
        })
    .selector(':selected')
        .css({
            'background-color': 'black',
            'color': 'black',
        })
    .selector('.driver')
        .css({
            'border-color': '#793d71',
        })
    .selector('edge')
        .css({
            'color': "#4F8ABA",
            'line-color': '#4F8ABA',
            'target-arrow-color': '#4F8ABA',
            'target-arrow-shape': 'triangle',
            "width": "data(width)"
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
    


// Cytoscape variable definition
var cy = cytoscape({
    style: stylesheet,
    layout: { name: 'preset' },
    container: document.getElementById('cyt'),
    boxSelectionEnabled: true,  
    ready: function() {}
});
