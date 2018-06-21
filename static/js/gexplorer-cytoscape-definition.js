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
            'background-color': '#2CA089',
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
            'background-color': 'black',
            'color': 'black',
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
        "border-color": "#E0FFE8",
        })
    .selector('.lvl2')
     .css({
        "border-color": "#86DD9C",
        })
    .selector('.lvl3')
     .css({
        "border-color": "#59BC72",
        })
    .selector('.lvl4')
     .css({
        "border-color": "#2C9B48",
        })
    .selector('.lvl5')
     .css({
        "border-color": "#007A1F",
    })
    .selector('edge')
        .css({
            'color': "#4F8ABA",
            'line-color': '#4F8ABA',
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
    


// Cytoscape variable definition
var cy = cytoscape({
    style: stylesheet,
    layout: { name: 'preset' },
    container: document.getElementById('cyt'),
    boxSelectionEnabled: true,  
    ready: function() {}
});
