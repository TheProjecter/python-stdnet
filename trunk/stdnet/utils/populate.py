from datetime import date, timedelta
from random import uniform, randint, choice
import string

characters = string.letters + string.digits

def populate(datatype = 'string', size  = 10,
             start = None, end = None, **kwargs):
    data = []
    if datatype == 'string':
        for s in range(size):
            data.append(random_string(**kwargs))
    elif datatype == 'date':
        date_end   = end or date.today()
        date_start = start or date(1990,1,1)
        delta    = date_end - date_start
        for s in range(size):
            data.append(random_date(date_start, delta.days))
    elif datatype == 'integer':
        start = start or 0
        end = end or 1000000
        for s in range(size):
            data.append(randint(start,end))
    elif datatype == 'float':
        start = start or 0
        end = end or 10
        for s in range(size):
            data.append(uniform(start,end))
    else:
        for s in range(size):
            data.append(random_string(**kwargs))
    return data

def random_string(min_len = 3, max_len = 20, **kwargs):
    len = randint(min_len,max_len)
    s   = [choice(characters) for s in range(len)]
    return ''.join(s)

def random_date(date_start, delta):
    return date_start + timedelta(days = randint(0,delta))
    
    
    
