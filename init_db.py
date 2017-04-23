import MySQLdb
import peewee
from peewee import *
import random, time, math
if __name__ == '__main__':     # Have to import differently if using for initial seed
    from db_config import login
else:
    from .db_config import login

HOST     = login['host']
DATABASE = login['database']
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
    db.create_tables([Scan, Spectrum, Voxel], safe=True)

    s = Seeder(Scan, n=2, groups=1)
    s = Seeder(Spectrum, n=100, groups=1) # before was n=10, groups=2
    #s = Seeder(Voxel, n=100, groups=10)
    make_graph(49, f)

## experimental ##
def f(x,y):
    '''
    surface equation'''
    magnitude = math.sqrt(x**2 + y**2) # distance from origin
    return math.sin( magnitude ) * 4 + ( magnitude / 2 )  # return z component

def make_graph(n, func):
    spectrum_id = 1
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
        with db.atomic():
            for voxel in data:
                voxel.save()



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

### Code to execute if run as main module ###############################################
if __name__ == "__main__":
    db.connect()
    clean_slate()
    populate_tables()

