from flask import Flask, render_template, jsonify, url_for, request
import peewee
from . import init_db
from .init_db import *

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('points.html')

@app.route('/api/points')
def sql_json():
	#### TO-DO ### HANDLE IF SPECTRUM_ID DOES NOT EXIST #########
	# Get requested spectrum_id
	spectrum_id = int(request.args.get('spectrum_id', 1))

	# Get spectrum data
	db = init_db.db
	spectrum = Spectrum.get(Spectrum.id == spectrum_id)
	
	# Get associated voxels
	cursor = db.execute_sql(f'SELECT x,y,z,time FROM voxel WHERE spectrum_id = {spectrum_id};')
	results = cursor.fetchall()

	# Package data in clean dictionaries
	fields = ('x','y','z','time')
	voxel_data = [{field:value for field,value in zip(fields,result)} for result in results]

	spectrum_fields = ('spectrum_id', 'reading')
	spectrum_values = (spectrum.id, spectrum.reading)
	spectrum_data = dict(zip(spectrum_fields, spectrum_values))

	# Package into json-ready dictionary
	packed = { }
	packed['voxels'] = voxel_data
	packed['spectrum'] = spectrum_data
	# Send off 
	return jsonify(packed)

@app.route('/api/spectrum')
def get_first_spectrum():
	db = init_db.db
	scan_id = int(request.args.get('scan_id', 1))
	cursor = db.execute_sql(f"SELECT id FROM spectrum WHERE scan_id = {scan_id} LIMIT 1;")
	spectrum_start_id = 

############ alt query ################################
#this sql query would ship redundant data over network, 
#but only one db call instead of two
"""
f'select x,y,z,voxel.time,spectrum.reading from voxel 
left join spectrum on voxel.spectrum_id = spectrum.id 
where voxel.spectrum_id = {spectrum_id};
"""
#######################################################
