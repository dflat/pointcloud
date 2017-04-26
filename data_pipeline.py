import peewee
from db_config import air_login
from db_config import ground_login
from collections import namedtuple
import threading
#from queue import Queue
import queue
import time

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


# def decode(a,b):
# 	high = (a-128) << 7
# 	low = (b-128)
# 	return high + low

# def preprocess(input):
# 	output = medfilt( recovered, 5 ) # median filter
# 	output = output - min(output)
# 	output = output / max(output)	# normalized intensity from 0 to 1
# 	return output

# def colorParse(signature):

# 	blue = sum( signature[219,315] )	# max  96
# 	green = sum( signature[316,475] )		# 159 
# 	red = sum( signature[580,849] )			# 269

# 	blue = 255 * blue / 96
# 	green = 255 * green / 159
# 	red = 255 * red / 269

# 	return red, green, blue

# 	# start = 350
# 	# end = 800
# 	# vals = 950

# 	# blue = 450-495	
# 		# og 248-344	
# 		#    219-315	minus 29 for trim
# 	# green= 495-570
# 		# og 345-504
# 		#    316-475
# 	# red  = 620-750
# 		# og 609-878
# 		#	 580-849

# def correct():



# def get_rgb(decoded):
# 		return color_parse(correct(preprocess(decoded)))

def Process(signature):
	print('proccessing..', signature)
	r,g,b = 255,0,0
	return r,g,b

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


def monitor(scan_id): #accepts scan_id from RAMS 
	last_seen = None
	while True:
		latest = get_latest_spectrum(scan_id, last_seen) # check db for its latest spectrum entry
		print(f'received {latest} from Scan {scan_id}..')
		if latest and latest.id != last_seen: # if there is a record, and its new
			last_seen = latest.id
			spectrum_queue.put(latest) # Put the new spectrum on the queue
		else:
			time.sleep(POLL_INTERVAL) # nothing new, check back in 400ms..


def commit_voxels_for(spectrum, ground_scan_id):
	rams_cursor = RAMS.execute_sql(f'SELECT * FROM voxel WHERE spectrum_id = {spectrum.id};')
	voxels = map( Voxel._make, rams_cursor.fetchall() )
	
	#######################################
	## add processing here to get R G B  ##
	# 								      #
	#	Process is a stub         		  #
	#######################################
	R,G,B = Process(spectrum.signature)

	inserted = GROUND.execute_sql(f"INSERT INTO spectrum\
									(time, signature, red, green, blue, scan_id) VALUES\
						({spectrum.time}, {spectrum.signature}, {R},{G},{B}, {ground_scan_id});")

	new_spec_id = inserted.lastrowid
	print(f'inserted Spectrum {new_spec_id} to GROUND with Scan {ground_scan_id}')
	
	with GROUND.atomic():
		for v in voxels:
			GROUND.execute_sql(f'INSERT INTO voxel (time, x, y, z, spectrum_id, scan_id)\
								VALUES ({v.time},{v.x},{v.y},{v.z},{new_spec_id},{ground_scan_id});')
	print(f'inserted voxel-set to GROUND for Spectrum {new_spec_id}')	
def consume_spectra(ground_scan_id):
	finished_spectrum = None
	while True:
		if finished_spectrum == None:
			finished_spectrum = spectrum_queue.get() # Dont progress til grab first spectrum
			print('queued first spectrum..')
		try:
			latest_spectrum = spectrum_queue.get(timeout=TIMEOUT) # block execution until grab second
		except queue.Empty:
			commit_voxels_for(finished_spectrum, ground_scan_id)
			print('scan completed.')
			break

		print('calling commit..')
		commit_voxels_for(finished_spectrum, ground_scan_id) # Antecedent spectrum

		finished_spectrum = latest_spectrum


####### end data flow for db transfer ############################

POLL_INTERVAL = 0.4 # Seconds
TIMEOUT = 10 # Seconds
spectrum_queue = queue.Queue()

# These are micro-classes to use as models instead of peewee models, way more efficient
# they just map returned db records to field names and are part of standard library
Scan = namedtuple('Scan', ['id','start_time','white_bal']) 
Spectrum = namedtuple('Spectrum', ['id', 'time', 'exposure', 'signature','scan_id'])
Voxel = namedtuple('Voxel', ['id','time','x','y','z','scan_id','spectrum_id'] )

## starts by fetching latest spectrum in the db from the time this program starts
## what if theres already been a few entered? well, they get sadly ignored..
## problem: don't ignore the good folks! 
## solution: start at the first record for the latest scan id, track last seen and +1

def main():
	while True:
		try:
			rams_cursor = RAMS.execute_sql("SELECT * FROM scan ORDER BY id DESC LIMIT 1;") # Latest scan
			latest_scan = Scan._make( rams_cursor.fetchone() ) # Turn into Scan object
			break
		except TypeError:
			print(f'no scans found in RAMS db..')
			time.sleep(.5)
			
			
	
	### process scan white balance here ####
	

	# Put scan in ground db
	#print(latest_scan.white_bal)
	rams_scan_id = latest_scan.id

	inserted = GROUND.execute_sql(f'INSERT INTO scan (start_time, white_bal)\
									VALUES ( {latest_scan.start_time},"{latest_scan.white_bal}" );')
	ground_scan_id = inserted.lastrowid
	print(f'Transmitting Scan # {ground_scan_id}..')

	t = threading.Thread(target=monitor, args=(rams_scan_id,))
	t.daemon = True
	t.start()

	consume_spectra(ground_scan_id) # Run forever (terminate on TIMEOUT)




	# w = Scan.white_bal
	# recovered_white_bal = [ decode(w[2*i], w[2*i+1]) 
	# 						for i in range(29,980) ] # python iteration sugar

	#rams_cursor = RAMS.execute_sql(f"SELECT * FROM spectum WHERE scan = {latest_scan.id};")


	#spectra = map(Spectrum._make, rams_cursor.fetchall()) # Turn all records into Spectrum objects




	



	
	

### Models to represent records in DB as objects ######################################    
# class BaseModel(Model):
#     class Meta:
#         database = RAMS
# class Scan(BaseModel):
#     start_time = IntegerField()
#     white_bal = TextField()
# class Spectrum(BaseModel):
# 	scan = ForeignKeyField(Scan, related_name='id')
#     time = IntegerField()
#     spectrum = TextField()
# class Voxel(BaseModel):
# 	scan = ForeignKeyField(Scan, related_name='id')
# 	spectrum = ForeignKeyField(Spectrum, related_name='id')
#     time = IntegerField()
#     x = IntegerField()
#     y = IntegerField()
#     z = IntegerField()


# class RamsBase(Model):
# 	class Meta:
# 	        database = RAMS

# class Scan(RamsBase):
# 	start_time = IntegerField()
#     white_bal = TextField()
# class Spectrum(RamsBase):
# 	time = IntegerField()
# 	signature = TextField()
# 	scan_id = ForeignKeyField(Scan, related_name='spectra')
# class Voxel(RamsBase):
# 	time = IntegerField()
# 	x = SmallIntegerField()
# 	y = SmallIntegerField()
# 	z = SmallIntegerField()
# 	spectrum_id = ForeignKeyField(Spectrum, related='voxels')
# 	scan_id = ForeignKeyField(Scan, related ='voxels')


#define CREATE_SCANS "CREATE TABLE scans( id INT NOT NULL AUTO_INCREMENT, start_time INT, white_bal TEXT, PRIMARY KEY(id) )"
#define CREATE_SPECTRA "CREATE TABLE spectra( id INT NOT NULL AUTO_INCREMENT, scan INT REFERENCES scans(id), time INT, exposure INT, spectrum TEXT, PRIMARY KEY(id) )"
#define CREATE_VOXELS "CREATE TABLE voxels( scan INT REFERENCES scans(id), spectrum INT REFERENCES spectra(id), time INT, x INT, y INT, z INT )"


if __name__ == "__main__":
	main()	


#	c language decoder
#
# 	for(int i=0; i<PIXELS; i++){
#		high = (string[2*i]-start)<<7;
#		low = (string[2*i+1]) - start;
#		output[i] = high + low;
#	}


