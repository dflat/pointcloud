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
scene.rotation.x = -(Math.PI / 2)

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
// document.addEventListener('mousedown', on_drag_start, false);
// document.addEventListener('mouseup', on_drag_end, false)
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
/************** raycasting setup **************************************/
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
var SPECTRUM_ROOT = 'api/spectrum?';
var ASSET_ROOT = 'static/';
var TEXTURE_DIR = 'Textures/';
var LIMIT = 99; //batch size to grab from db each fetch
var MAX_DB_FETCHES = 99; //IN PRODUCTION CHANGE THIS
var dragging = false;
var texture;
var rendering = false;
var render_lock = false;
const POLLING_INTERVAL = 500 //milliseconds
/* when document is ready, this is entry point */
$( document ).ready(function() {
	


	register_scan_selector();
	

});


function get_starting_spectrum_id(scan_id){

        $.ajax({
            url: SPECTRUM_ROOT + 'scan_id=' + scan_id, 
            method: 'GET',
            async: true,
            success: function(spectrum_data) {
            	console.log('spectrum id from api:', spectrum_data)
            	starting_spectrum_id = spectrum_data['spectrum_start_id']
            	spectrum_count = spectrum_data['spectrum_count']
            	// if(scan_id == 0)
            	// 	scan_id = spectrum_data['scan_id']
            	get_continuous_data(MAX_DB_FETCHES, scan_id, spectrum_data)   
            }
        });
}


function get_continuous_data(max_fetches, scan_id, spectrum_data, upon_termination=null) {
    var live_feed = false;
    var fetch_success = 0;
  	var spec_id = spectrum_data['spectrum_start_id']
  	var spectrum_count = spectrum_data['spectrum_count']


  	//var spec_id = start_spectrum_id;

  	if (scan_id == 0) {
  		live_feed = true
  		scan_id = spectrum_data['scan_id']; // set scan id to latest scan
  	} 
  	else {
  		max_fetches = spectrum_count; 
  	} 
  		
    function get_next_set() {
        $.ajax({
            url: API_ROOT + 'spectrum_id=' + spec_id + '&scan_id=' + scan_id, 
            method: 'GET',
            async: true,
            success: function(data) {
 
                if (live_feed || fetch_success < max_fetches) {
                    //fetch_count += 1;
                    //console.log('voxels:',data['voxels'].length, 'fetch count',fetch_count)
	                    if (data['voxels'].length > 0) {
		                    add_mesh(data);
		                    spec_id += 1
		                    fetch_success += 1;
	                   
		                    if(!render_lock){  // If not signaled to terminate
		                    	get_next_set();
		                    }
		                    else{ 
		                    	console.log('returning')
		                    	return
		                    }
	                	}
	                	else{ 					// No new data to render
	                		if(!render_lock){
	                			setTimeout(get_next_set, POLLING_INTERVAL)
	                			console.log('no data')
	                		}
	                		else 
	                			return;
	                	}
                }
            }
        });
    }
    //rendering = true
    get_next_set();
    render_lock = false
    //rendering = false
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
	//colored.setRGB(data['spectrum']['reading'], Math.random(), Math.random() )
	colored.setRGB(data.spectrum.red/255, data.spectrum.green/255, data.spectrum.blue/255 )

	material = new THREE.PointsMaterial({ size: POINT_SIZE, color: colored,
										  depthWrite:false, transparent: false });
	//create mesh
	mesh = new THREE.Points( geometry, material );
	
	//add to scene
	mesh.spectrum = data['spectrum']
	
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
const ZOOM_STEP = .3

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
	  			/*** call chart.js to update ***/
	  			updateSpectrumChart(touched);
	  	
	  			/*******************************/
	  	
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
				updateSpectrumChart(touched);
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

	// if (w_pressed && Math.sin(scene.rotation.x) <= 0) scene.rotation.x += Z_ROTATE_STEP
 //  	if (s_pressed && Math.sin(scene.rotation.x) <= 0) scene.rotation.x -= Z_ROTATE_STEP
	
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

/****************** scan selector functionality ********************************/
function register_scan_selector(){

	$("#scan-selector li").click(function() {
    	var selected_scan_id = $(this).attr('data');
    
    	//sends signal to current render to terminate
    	render_lock = true
    
    	//defer clear and reload to ensure current render has been terminated
    	//would be more robust to make this a callback instead of timeout deferred
    	setTimeout(clear_and_reload.bind(null, selected_scan_id),(POLLING_INTERVAL + 100)); 	
	
	});

}

function clear_and_reload(selected_scan_id){
	while(scene.children.length > 0){ 
    	scene.remove(scene.children[0]); 
    }
    //after clear, begin loading newly selected scan
    get_starting_spectrum_id(selected_scan_id);
}



/***8 experimental ***/


function clear_and_reload(selected_scan_id, call_when_terminated, new_scan_to_load){
	while(scene.children.length > 0){ 
    	scene.remove(scene.children[0]); 
    }
    //after clear, begin loading newly selected scan
    get_starting_spectrum_id(selected_scan_id, call_when_terminated, new_scan_to_load);
}



























