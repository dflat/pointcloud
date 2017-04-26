import MySQLdb
import peewee
from peewee import *
import random, time, math
if __name__ == '__main__':     # Have to import differently if using for initial seed
    from db_config import login, ground_login
else:
    from .db_config import login, ground_login

HOST     = login['host']
DATABASE = ground_login['database'] # use ground db
USER     = login['user']
PASS     = login['password']

db = peewee.MySQLDatabase(database=DATABASE, host=HOST, user=USER, passwd=PASS) 

def clean_slate():
    """
    drops tables if they exist
    """
    Voxel.drop_table(fail_silently=True)
    Spectrum.drop_table(fail_silently=True)
    Scan.drop_table(fail_silently=True)

def populate_tables():
    """
    seeds tables with test data
    """
    SCAN_RECORDS = 2
    X_UPPER_BOUND = 49
    VOXELS_PER_SPECTRUM = 99
    SPECTRA_PER_SCAN = 99

    db.create_tables([Scan, Spectrum, Voxel], safe=True)

    s = Seeder(Scan, n=2, groups=1)
    s = Seeder(Spectrum, n=SPECTRA_PER_SCAN, groups=2) # before was n=10, groups=2
    #s = Seeder(Voxel, n=100, groups=10)
    make_graph(X_UPPER_BOUND, f, spectrum_id_start=1)
    make_graph(X_UPPER_BOUND, g, spectrum_id_start=(SPECTRA_PER_SCAN + 1))

## experimental ##
def f(x,y):
    '''
    surface equation'''
    magnitude = math.sqrt(x**2 + y**2) # distance from origin
    return math.sin( magnitude ) * 4 - ( magnitude / 2 )  # return z component
def g(x,y):
    magnitude = math.sqrt(x**2 + y**2)
    return math.cos(magnitude) 

def make_graph(n, func, spectrum_id_start=1):
    spectrum_id = spectrum_id_start
    voxels = []
    for x in range(-n,n+1):
        for y in range(-n,n+1):
            v = Voxel()
            v.x = x
            v.y = y
            v.z = func(x,y)
            v.time = time.time()
            v.spectrum = spectrum_id
            voxels.append(v)
        spectrum_id += 1
        seed(voxels)
        voxels = []

def seed(data):
        """
        commits to db in blocks of size ( self.n )
        """
        time.sleep( random.random() ) # TO TEST temporally random data production
        with db.atomic():
            for voxel in data:
                voxel.save()
                #Voxel.save(data) ??? execute in batches?



## end experimental ##

class Seeder:
    """
    Class to generate and seed db with test data 
    """
    def __init__(self, Model, n=100, groups=1):
        self.Model = Model
        self.n = n
        self.foreign_key_count = 1
        for _ in range(groups):
            self.generate_seed_data()
            self.seed()
            self.foreign_key_count += 1

    def generate_seed_data(self):
        fields = self.Model._meta.fields
        self.data = [ { k:self.mock(type(v)) for k,v in fields.items() 
                   if not k.startswith('id') } for _ in range(self.n) ] 
                   
    def mock(self, data_type):
        """
        returns field-approriate value, randomized when necesary
        """
        if data_type is ForeignKeyField:
            #return self.Model._meta.related_models()[1].get().id 
            return self.foreign_key_count
        elif data_type is IntegerField:
            return random.randint(-100,100)
        elif data_type is DoubleField:
            return time.time()
        elif data_type is FloatField:
            return random.random()

    def seed(self):
        """
        commits to db in blocks of size ( self.n )
        """
        with db.atomic():
            for idx in range(0, len(self.data), 100):
                self.Model.insert_many(self.data[idx:idx+100]).execute()

### Models to represent records in DB as objects ######################################    
class BaseModel(Model):
    class Meta:
        database = db
class Scan(BaseModel):
    start_time = IntegerField()
    white_bal = TextField()
class Spectrum(BaseModel):
    time = IntegerField()
    signature = IntegerField()
    red = IntegerField()
    green = IntegerField()
    blue = IntegerField()
    scan = ForeignKeyField(Scan, related_name='spectra')
class Voxel(BaseModel):
    time = IntegerField()
    x = IntegerField()
    y = IntegerField()
    z = IntegerField()
    #scan = ForeignKeyField(Scan, related_name='voxels')
    spectrum = ForeignKeyField(Spectrum, related_name='voxels')

### Code to execute if run as main module ###############################################

""" 
old models for database 'test' to use with graphs (f, g) 

class BaseModel(Model):
    class Meta:
        database = db
class Scan(BaseModel):
    time = DoubleField()
class Spectrum(BaseModel):
    reading = FloatField()
    time = DoubleField()
    scan = ForeignKeyField(Scan, related_name='spectra')
class Voxel(BaseModel):
    x = IntegerField()
    y = IntegerField()
    z = FloatField()#IntegerField()
    time = DoubleField()
    spectrum = ForeignKeyField(Spectrum, related_name='voxels')

"""
if __name__ == "__main__":
    db.connect()
    clean_slate()
    populate_tables()

