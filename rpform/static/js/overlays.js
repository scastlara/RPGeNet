/*==================================================
overlays.js - Setting the overlays of the index page
==================================================*/

var options = {
  container: 'inputgenes',
  openContainer: 'inputgenes-btn',
  scroll: false,
  align: 'center',
  width: '35%',
  background: "white", 
  closeBackground: "white",
  padding: "2%"
}
// Gene Overlay
var overlayGenes      = new StoopidOverlay(options);
options.container     = 'inputgenes2';
options.openContainer = 'inputgenes-btn2';
var overlayDist       = new StoopidOverlay(options);
// Distance Overlay
options.container     = 'genedistance';
options.openContainer = 'genedistance-btn';
var overlayDist       = new StoopidOverlay(options);
// Intlvl Overlay
options.container     = 'intlvl';
options.openContainer = 'intlvl-btn';
var overlayDist       = new StoopidOverlay(options);
options.container     = 'intlvl2';
options.openContainer = 'intlvl-btn2';
var overlayDist2      = new StoopidOverlay(options);

// Genexp Overlay
// Intlvl Overlay
options.container     = 'genexp';
options.openContainer = 'genexp-btn';
var overlayGexp       = new StoopidOverlay(options);
options.container     = 'genexp2';
options.openContainer = 'genexp-btn2';
var overlayGexp2      = new StoopidOverlay(options);
//options.container = 'genedistance';
//options.openContainer = 'genedistance-btn';
//var myOverlay2 = new StoopidOverlay(options);