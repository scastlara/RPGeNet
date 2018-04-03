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
            "font-size": 8,
            'text-outline-width': 2,
            "text-outline-color": "#FFFFFF",
            "color": "#404040",
            "border-color": "#CCCCCC",
            "border-width": 8,
            "min-zoomed-font-size": 6,
        })
    .selector(':selected')
        .css({
            'background-color': '#FDDB4F',
            'color': 'black',
        })
    .selector('.driver')
        .css({
            'border-color': '#8D65EC',
        })
    .selector('edge')
        .css({
            'font-size': 6,
            'width': 1,
            'color': "#4F8ABA",
            'line-color': '#4F8ABA',
            'target-arrow-color': '#4F8ABA',
            'target-arrow-shape': 'triangle',
            "min-zoomed-font-size": 6,
        })
    


// Cytoscape variable definition
var cy = cytoscape({
    style: stylesheet,
    layout: { name: 'preset' },
    container: document.getElementById('cyt'),
    boxSelectionEnabled: true,  
    ready: function() {}
});
