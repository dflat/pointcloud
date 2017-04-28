import peewee
from db_config import air_login
from db_config import ground_login
from collections import namedtuple
import threading
import queue
import time
import numpy
import scipy.signal
import scipy
import random
import decoder_test as deco
import json

HOST     = air_login['host']
DATABASE = air_login['database']
USER     = air_login['user']
PASS     = air_login['password']
RAMS = peewee.MySQLDatabase(database=DATABASE, host=HOST, user=USER, passwd=PASS) 

HOST     = ground_login['host']
DATABASE = ground_login['database']
USER     = ground_login['user']
PASS     = ground_login['password']
GROUND = peewee.MySQLDatabase(database=DATABASE, host=HOST, user=USER, passwd=PASS) 


################ data flow for db transfer ################

def get_latest_spectrum(scan_id, last_seen):
	if last_seen is None: 
		rams_cursor = RAMS.execute_sql(f"SELECT * FROM spectrum WHERE scan_id = {scan_id}\
									ORDER BY id ASC LIMIT 1;")
	else:
		rams_cursor = RAMS.execute_sql(f"SELECT * FROM spectrum WHERE scan_id = {scan_id}\
										AND id = {last_seen+1} LIMIT 1;")
	result = rams_cursor.fetchone()
	#print('get latest',result)
	if result:
		return Spectrum._make(result)
	return None


def monitor(scan_id): # data fetching daemon 
	last_seen = None
	while True:
		latest = get_latest_spectrum(scan_id, last_seen) # check db for its latest spectrum entry
		print(f'received {latest} from Scan {scan_id}..')
		if latest and latest.id != last_seen: # if there is a record, and its new
			last_seen = latest.id
			spectrum_queue.put(latest) # Put the new spectrum on the queue
		else:
			time.sleep(POLL_INTERVAL) # nothing new, check back in 400ms..


def commit_voxels_for(spectrum, ground_scan):
	rams_cursor = RAMS.execute_sql(f'SELECT * FROM voxel WHERE spectrum_id = {spectrum.id};')
	voxels = map( Voxel._make, rams_cursor.fetchall() )
	
	#print('sig length:', len(spectrum.signature))
	processed_signature = deco.Process(spectrum.signature, ground_scan.white_bal)
	processed_signature = list(processed_signature)
	#print('processed_signature', processed_signature)
	R,G,B = deco.color_parse(processed_signature)
	print('R, G, B = ', R,G,B)
	#processed_signature = [i/950 for i in range(1,950)]
	processed_signature = json.dumps(processed_signature)


	query = "INSERT INTO spectrum (time, signature, red, green, blue, scan_id) values (%s,%s,%s,%s,%s,%s);"
	values = (spectrum.time, processed_signature, R, G, B, ground_scan.id)
	inserted = GROUND.execute_sql(query, values)

	new_spec_id = inserted.lastrowid
	print(f'inserted Spectrum {new_spec_id} to GROUND with Scan {ground_scan.id}')
	
	with GROUND.atomic():
		for v in voxels:
			GROUND.execute_sql(f'INSERT INTO voxel (time, x, y, z, spectrum_id, scan_id)\
								VALUES ({v.time},{v.x},{v.y},{v.z},{new_spec_id},{ground_scan.id});')
	print(f'inserted voxel-set to GROUND for Spectrum {new_spec_id}')	
	
def consume_spectra(ground_scan):
	finished_spectrum = None
	while True:
		if finished_spectrum == None:
			finished_spectrum = spectrum_queue.get() # Dont progress til grab first spectrum
			print('processing first spectrum..')
		try:
			latest_spectrum = spectrum_queue.get(timeout=TIMEOUT) # block execution until grab second
		except queue.Empty:
			commit_voxels_for(finished_spectrum, ground_scan)
			print('scan completed.')
			break

		print('calling commit..')
		commit_voxels_for(finished_spectrum, ground_scan) # Antecedent spectrum

		finished_spectrum = latest_spectrum


####### main ############################

POLL_INTERVAL = 0.4 # Seconds
TIMEOUT = 10 # Seconds
spectrum_queue = queue.Queue()

Scan = namedtuple('Scan', ['id','start_time','white_bal']) 
Spectrum = namedtuple('Spectrum', ['id', 'time', 'exposure', 'signature','scan_id'])
Voxel = namedtuple('Voxel', ['id','time','x','y','z','scan_id','spectrum_id'] )


def main():
	while True:
		try:
			rams_cursor = RAMS.execute_sql("SELECT * FROM scan ORDER BY id DESC LIMIT 1;") # Latest scan
			latest_scan = Scan._make( rams_cursor.fetchone() ) # Turn into Scan object
			break
		except TypeError:
			print(f'no scans found in RAMS db..')
			time.sleep(.5)
			
	decoded_white_bal = deco.find_bias(latest_scan.white_bal)
	
	rams_scan_id = latest_scan.id

	query = "INSERT INTO scan (start_time, white_bal) values (%s, %s);"
	values = (latest_scan.start_time, latest_scan.white_bal)

	inserted = GROUND.execute_sql(query, values)

	ground_scan_id = inserted.lastrowid

	ground_scan = Scan(id=ground_scan_id, 
						start_time=latest_scan.start_time, 
						white_bal=decoded_white_bal)

	print(f'Transmitting Scan # {ground_scan_id}..')

	t = threading.Thread(target=monitor, args=(rams_scan_id,))
	t.daemon = True
	t.start()

	consume_spectra(ground_scan) # Run forever (terminate on TIMEOUT)


if __name__ == "__main__":
	main()	


