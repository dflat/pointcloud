from flask import Flask, render_template, jsonify, url_for, request
import peewee
from . import init_db
from .init_db import *
import random, math
import json

app = Flask(__name__)


@app.route('/')
def index():
	db = init_db.db
	cursor = db.execute_sql(f'SELECT id FROM scan;')
	results =  cursor.fetchall()
	scans = [row[0] for row in results]
	#print(scans)
	return render_template('points.html', scans=scans)

@app.route('/api/points')
def sql_json():
	# Get requested spectrum_id
	spectrum_id = int(request.args.get('spectrum_id', 1))
	scan_id = int(request.args.get('scan_id', 1))
	# Get spectrum data
	db = init_db.db

	try:
		spectrum = Spectrum.get(Spectrum.id == spectrum_id)
	except Spectrum.DoesNotExist:
		return jsonify({'voxels':[]})
	
	# Get associated voxels
	#cursor = db.execute_sql(f'SELECT x,y,z,time FROM voxel WHERE spectrum_id = {spectrum_id};')
	#results = cursor.fetchall()

	cursor = db.execute_sql(\
	f'SELECT voxel.*, spectrum.scan_id FROM voxel\
	LEFT JOIN spectrum ON voxel.spectrum_id = spectrum.id\
	WHERE voxel.spectrum_id = {spectrum_id} AND spectrum.scan_id = {scan_id};')

	results = cursor.fetchall()

	# Package data in clean dictionaries
	fields = ('id','time', 'x','y','z')
	voxel_data = [{field:value for field,value in zip(fields,result)} for result in results]

	spectrum_fields = ('spectrum_id', 'reading', 'red','green','blue')
	spectrum_values = (spectrum.id, spectrum.signature,spectrum.red,spectrum.green,spectrum.blue)
	print(spectrum_values)
	spectrum_data = dict(zip(spectrum_fields, spectrum_values))

	# Package into json-ready dictionary
	packed = { }
	packed['voxels'] = voxel_data
	# spectrum_data['reading'] = [(i/980) - random.random() for i in range(29,980)]
	spectrum_data['reading'] = json.loads(spectrum_data['reading'])
	packed['spectrum'] = spectrum_data
	# Send off 

	return jsonify(packed)

@app.route('/api/spectrum')
def get_first_spectrum():
	LIVE = 0
	db = init_db.db
	scan_id = int(request.args.get('scan_id', 1))
	if(scan_id == LIVE): 
		# fetch first spectrum id for last recorded scan (the live one)
		cursor = db.execute_sql('SELECT id, scan_id FROM spectrum\
								 ORDER BY scan_id DESC, id ASC LIMIT 1;')
		results = cursor.fetchone()
		spectrum_start_id = results[0]
		scan_id = results[1]
		spectrum_count = 0
	else: #already completed scan
		cursor = db.execute_sql(f"SELECT id FROM spectrum WHERE scan_id = {scan_id} LIMIT 1;")
		spectrum_start_id = cursor.fetchone()[0]
		cursor = db.execute_sql(f'SELECT COUNT(id) FROM spectrum WHERE scan_id = {scan_id};')
		spectrum_count = cursor.fetchone()[0]
	return jsonify({'spectrum_start_id':spectrum_start_id, 
					'spectrum_count':spectrum_count,
					'scan_id': scan_id })

############ alt query ################################
#this sql query would ship redundant data over network, 
#but only one db call instead of two
"""
f'select x,y,z,voxel.time,spectrum.reading from voxel 
left join spectrum on voxel.spectrum_id = spectrum.id 
where voxel.spectrum_id = {spectrum_id};
"""
#######################################################
