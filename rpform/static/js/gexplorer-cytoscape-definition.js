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
            'background-color': 'blue',
            "font-size": 8,
            'text-outline-width': 2,
            "text-outline-color": "#FFFFFF",
            "color": "#404040",
            "border-color": "data(colorNODE)",
            "border-width": 2,
            "min-zoomed-font-size": 6,
        })
    .selector(':selected')
        .css({
            'background-color': 'yellow',
            'color': 'red',
        })
    .selector('.driver')
        .css({
            'border-color': '#6785d0',
        })
    .selector('edge')
        .css({
            'content': 'data(probability)',
            'font-size': 6,
            'width': 1,
            'color': "#404040",
            'text-background-opacity': 1,
            'text-background-color': '#F8F8F8',
            'text-background-shape': 'roundrectangle',
            'text-border-color': '#404040',
            'text-border-width': 0.1,
            'text-border-opacity': 0.5,
            'line-color': 'data(colorEDGE)',
            'target-arrow-color': 'data(colorEDGE)',
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
