/************************ scene initialization ***************************/
var scene, camera, renderer;
//make main div
container = document.createElement('div');
container.style.position = "fixed";
container.style.zIndex = -1;
document.body.appendChild(container);

//init camera
camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 2000);
camera.position.z = 200; //old 1200

//init scene
scene = new THREE.Scene();
//add fog, duh
scene.fog = new THREE.FogExp2(0x000000, 0.0007);

//init renderer
renderer = new THREE.WebGLRenderer();
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);

//attach renderer to dom
container.appendChild(renderer.domElement);

//init mouse coords
var mouseX = 0;
var mouseY = 0;
var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;

/********************** mouse event listeners ******************************/
document.addEventListener('mousedown', on_drag_start, false);
document.addEventListener('mouseup', on_drag_end, false)
function on_drag_start(event) {
	event.preventDefault()
	dragging = true;
	console.log(dragging)
}
function on_drag_end(event) {
	dragging = false;
	console.log(dragging)
}
document.addEventListener('mousemove', onDocumentMouseMove, false);



function onDocumentMouseMove(event) {

  mouseX = event.clientX - windowHalfX;
  mouseY = event.clientY - windowHalfY;

}

/******** optional listeners for touch  **************************************/
document.addEventListener('touchstart', onDocumentTouchStart, false);
document.addEventListener('touchmove', onDocumentTouchMove, false);
function onDocumentTouchStart(event) {
  if (event.touches.length === 1) {
    event.preventDefault();

    mouseX = event.touches[0].pageX - windowHalfX;
    mouseY = event.touches[0].pageY - windowHalfY;
  }
}

function onDocumentTouchMove(event) {
  if (event.touches.length === 1) {
    event.preventDefault();

    mouseX = event.touches[0].pageX - windowHalfX;
    mouseY = event.touches[0].pageY - windowHalfY;
  }
}

/******************** main async loop hitting database ***********************/
var API_ROOT = 'api/points?';
var ASSET_ROOT = 'static/';
var TEXTURE_DIR = 'Textures/';
var LIMIT = 100; //batch size to grab from db each fetch
var MAX_DB_FETCHES = 10;
var dragging = true;
var texture;
$( document ).ready(function() {

	get_continuous_data(MAX_DB_FETCHES);

});

function get_continuous_data(max_fetches) {
    var fetch_count = 0;
    var previous = 0
  	var spec_id = 1
    function get_next_set() {
        $.ajax({
            url: API_ROOT + 'spectrum_id=' + spec_id, //+ '&limit=' + LIMIT + '&prev=' + previous,
            method: 'GET',
            async: true,
            success: function(data) {
        		//or lose the _if_ to never stop checking db
                if (fetch_count < max_fetches) {
                    fetch_count += 1;
                    console.log(data)
	                    if (data.length > 0) {
	                    add_mesh(data);
	                    //previous = data[data.length-1]['t'];
	                    spec_id += 1
	                    //console.log('previous :'+ previous);
	                    
	                    get_next_set();
	                	}
                }
            }
        });
    }
    get_next_set();
}

/********************* Set color and add voxels to scene *********************************/
function add_mesh(points){
	var geometry, material, mesh;
	//construct geometry
	geometry = new THREE.Geometry();
	build_points(points[0], geometry); //points [0] -> all voxels for given spectrum

	var colored = new THREE.Color();
	colored.setRGB(points[1], Math.random(), Math.random() )

	material = new THREE.PointsMaterial({ size: 2, color: colored,
										  depthWrite:true, transparent: true });
	//create mesh
	mesh = new THREE.Points( geometry, material );
	
	//add to scene
	scene.add( mesh );
}
// colors=[];

/************************ Construct voxels per Spectrum **********************************/
function build_points(points, geometry){

	for ( var i = 0; i < points.length; i ++ ) {
					console.log('points: '+points)
					var vertex = new THREE.Vector3();
					vertex.x = points[i]['x']; 
					vertex.y = points[i]['y'];
					vertex.z = points[i]['z'];
					geometry.vertices.push( vertex );
					// colors[ i ] = new THREE.Color( 0xffffff );
					// colors[ i ].setHSL( ( vertex.x + 1000 ) / 2000, 1, 1);
				}
}

/************************* Main render loop ***********************************************/
function render() {
	//main render loop
	requestAnimationFrame( render );

	//camera.position.x += (mouseX - camera.position.x) * 0.1;
  	//camera.position.y += (-mouseY - camera.position.y) * 0.1;
  	//console.log('x:'+mouseX+' y:'+mouseY)
  	if (dragging){
  		scene.rotation.y += (mouseX - camera.position.x) * 0.0001;
  		scene.rotation.x += (mouseY - camera.position.y) * 0.0001;
  	}
	renderer.render( scene, camera );
}
render();

