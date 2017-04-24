/************************ scene initialization ***************************/
var scene, camera, renderer;
//make main div
container = document.createElement('div');
container.style.position = "fixed";
container.style.zIndex = -1;
document.body.appendChild(container);

//init camera
camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 2000);
var orbit_radius = 150
camera.position.z = orbit_radius; //old 1200


//init scene
scene = new THREE.Scene();

var axisHelper = new THREE.AxisHelper( 75 );
//scene.add( axisHelper );

//inital rotation for better viewing
// scene.rotation.x = 1.75;
// scene.rotation.y = .12;
// scene.rotation.z = 10.77;

//add fog, duh
scene.fog = new THREE.FogExp2(0x000000, 0.0017);

//initial rotation
scene.rotation.x = Math.PI / 2

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
/***** key listener for camera controls ************************************/
const W = 87;
const S = 83;
const A = 65;
const D = 68;
const T = 84;
const UP = 38;
const DOWN = 40;

var w_pressed = false;
var s_pressed = false;
var a_pressed = false;
var d_pressed = false;
var up_pressed = false;
var down_pressed = false;
var toggle_spin = false;
document.addEventListener('keydown', function(e)
        {

            var key = e.keyCode; 
            console.log(key)       
            switch( key )
            {
                case W:
                	w_pressed = true
                    break;
                case S:
                	s_pressed = true
                    break;
                case A:
                	a_pressed = true
                    break;
                case D:
                	d_pressed = true
                    break; 
                case UP:
                	up_pressed = true
                    break;  
                case DOWN:
                	down_pressed = true
                    break;                                                       
            }
        });

document.addEventListener('keyup', function(e)
        {
            var key = e.keyCode;        
            switch( key )
            {
                case W:
                	w_pressed = false
                    break;
                case S:
                	s_pressed = false
                    break;  
                case A:
                	a_pressed = false
                    break;
                case D:
                	d_pressed = false
                    break; 
                case T:
                	toggle_spin = !toggle_spin
                    break;
                case UP:
                	up_pressed = false
                    break;  
                case DOWN:
                	down_pressed = false
                    break;                                
            }
        });

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
/************** clickable functionality **************************************/
//register mouse postion
var POINT_THRESHOLD = 1;
var raycaster = new THREE.Raycaster();
raycaster.params.Points.threshold = POINT_THRESHOLD;
var mouse = new THREE.Vector2();
mouse.x = -1; // set mouse originally to top left
mouse.y = 1;  // mouse vectors are normalized -1 -> 1
function onMouseMove( event ) {

	// calculate mouse position in normalized device coordinates
	// (-1 to +1) for both components

	mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
	mouse.y = - ( event.clientY / window.innerHeight ) * 2 + 1;

}

window.addEventListener( 'mousemove', onMouseMove, false );

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
var MAX_DB_FETCHES = 100;
var dragging = false;
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
                    //console.log(data)
	                    if (data['voxels'].length > 0) {
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
var spectra = []
var materials = []
var POINT_SIZE = .5
var SELECTED_POINT_SIZE = .8
function add_mesh(data){
	var geometry, material, mesh;
	//construct geometry
	geometry = new THREE.Geometry();
	build_points(data['voxels'], geometry); //->send all voxels for current spectrum

	var colored = new THREE.Color();
	colored.setRGB(data['spectrum']['reading'], Math.random(), Math.random() )

	material = new THREE.PointsMaterial({ size: POINT_SIZE, color: colored,
										  depthWrite:false, transparent: false });
	//create mesh
	mesh = new THREE.Points( geometry, material );
	
	//add to scene
	mesh.spectrum = data['spectrum']
	console.log('spect_id',mesh.spectrum_id)
	scene.add( mesh );
	

	//just to access outside function
	spectra.push(mesh)
	materials.push(material)

	// var line = new THREE.Line( geometry, 
	// 		   new THREE.LineBasicMaterial( { color: 0x222222, opacity: 0.5 } ) );
	// scene.add( line );
	

}
// colors=[];

/************************ Construct voxels per Spectrum **********************************/
function build_points(points, geometry){

	for ( var i = 0; i < points.length; i ++ ) {
					//console.log('points: '+points)
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
var touched = null;
var real_color = null;
var locked = false;
var intersects;
var origin = new THREE.Vector3(0,0,0);
var rotation = 0;
const ROTATION_STEP = (Math.PI) / (60 * 2)//.01;
var POLAR_BOUNDARY = orbit_radius - 1;
const Z_ROTATE_STEP = (Math.PI) / (60 * 2)
const RADIUS_STEP = (Math.PI) / 16 // ~ 0.1, was 0.1 originally
const ZOOM_STEP = .1

function render() {
	// orbit_radius -= .01
	// camera.position.z -= .01
	// POLAR_BOUNDARY = orbit_radius - 1;
	//camera
	//main render loop
	requestAnimationFrame( render );
	//get mouse
	raycaster.setFromCamera( mouse, camera );
	intersects = raycaster.intersectObjects( scene.children );

	if(intersects.length){
	  	if(intersects[0].object != touched){
	  		if(touched == null){ 
	  			//store original color and set color to white
	  			touched = intersects[0].object
	  			touched.original_color = touched.material.color.getHex()
	  			touched.material.color.setRGB(1,1,1);

	  			touched.material.size = SELECTED_POINT_SIZE;
	  	
	  		}
	  		else { //touched is last touched spectrum
	  		
	  			//replace original color of last touched
			  	touched.material.color.setHex( touched.original_color )
			  	touched.material.size = POINT_SIZE
			  	//register new touched and store its color
				touched = intersects[0].object
				touched.original_color = touched.material.color.getHex()

				//set new touched to white
				touched.material.color.setRGB(1,1,1);
				touched.material.size = SELECTED_POINT_SIZE;
			}
	
		}
	}	
	
		
			
	
	if (w_pressed && camera.position.y < POLAR_BOUNDARY){ 
		rotation += ROTATION_STEP
		camera.position.y = orbit_radius * Math.sin(rotation)
		camera.position.z = orbit_radius * Math.cos(rotation)
	}
	if (s_pressed && camera.position.y > -POLAR_BOUNDARY){ 
		rotation -= ROTATION_STEP
		camera.position.y = orbit_radius * Math.sin(rotation)
		camera.position.z = orbit_radius * Math.cos(rotation)
	}
	camera.lookAt(origin)

	if (toggle_spin) {
		scene.rotation.z += Math.PI / (60 * 16)
	}
	if (up_pressed){
		orbit_radius -= ZOOM_STEP
		camera.position.z -= ZOOM_STEP
		POLAR_BOUNDARY = orbit_radius - 1;
	}
	if (down_pressed){
		orbit_radius += ZOOM_STEP
		camera.position.z += ZOOM_STEP
		POLAR_BOUNDARY = orbit_radius - 1;
	}
	// 	orbit_radius -= RADIUS_STEP
	// 	camera.position.z = orbit_radius;
	// }
	// if (up_pressed){
	//  orbit_radius += RADIUS_STEP
	//  camera.position.z = orbit_radius;
	// }
	
  	if (a_pressed) scene.rotation.z += Z_ROTATE_STEP
  	if (d_pressed) scene.rotation.z -= Z_ROTATE_STEP
  	//scene.rotation.z += Math.PI / (60 * 16)
  	
  	if (dragging){
  		scene.rotation.y += (mouseX - camera.position.x) * 0.0001;
  		scene.rotation.x += (mouseY - camera.position.y) * 0.0001;

  	}
	renderer.render( scene, camera );
}
render();

