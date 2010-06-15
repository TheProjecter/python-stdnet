from datetime import date, timedelta
from random import uniform, randint, choice
import string

characters = string.letters + string.digits
def_converter = lambda x : x

def populate(datatype = 'string', size  = 10,
             start = None, end = None, 
             converter = None, **kwargs):
    data = []
    converter = converter or def_converter
    if datatype == 'string':
        for s in range(size):
            data.append(converter(random_string(**kwargs)))
    elif datatype == 'date':
        date_end   = end or date.today()
        date_start = start or date(1990,1,1)
        delta    = date_end - date_start
        for s in range(size):
            data.append(converter(random_date(date_start, delta.days)))
    elif datatype == 'integer':
        start = start or 0
        end = end or 1000000
        for s in range(size):
            data.append(converter(randint(start,end)))
    elif datatype == 'float':
        start = start or 0
        end = end or 10
        for s in range(size):
            data.append(converter(uniform(start,end)))
    else:
        for s in range(size):
            data.append(converter(random_string(**kwargs)))
    return data

def random_string(min_len = 3, max_len = 20, **kwargs):
    len = randint(min_len,max_len)
    s   = [choice(characters) for s in range(len)]
    return ''.join(s)

def random_date(date_start, delta):
    return date_start + timedelta(days = randint(0,delta))
    
    
    
