/*==================================================
overlays.js - Setting the overlays of the index page
==================================================*/

// INPUT GENES
$(".inputgenes-btn").on("click", function() {
	$("#inputgenes-dialog").show();
});

$("#close-inputgenes-btn").on("click", function() {
	$("#inputgenes-dialog").hide();
});

// GENEDISTANCE
$(".genedistance-btn").on("click", function() {
	$("#genedistance-dialog").show();
});

$("#close-genedistance-btn").on("click", function() {
	$("#genedistance-dialog").hide();
});

// INTLVL
$(".intlvl-btn").on("click", function() {
	$("#intlvl-dialog").show();
});

$("#close-intlvl-btn").on("click", function() {
	$("#intlvl-dialog").hide();
});

// GENEXP
$(".genexp-btn").on("click", function() {
	$("#genexp-dialog").show();
});

$("#close-genexp-btn").on("click", function() {
	$("#genexp-dialog").hide();
});