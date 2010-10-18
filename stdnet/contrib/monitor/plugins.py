from datetime import datetime, timedelta

from django.conf import settings
from django import forms
from django.utils.dateformat import format, time_format

from djpcms.template import loader
from djpcms.plugins import DJPplugin

import redis


class RedisForm(forms.Form):
    server = forms.CharField(initial = 'localhost')
    port = forms.IntegerField(initial = 6379)
    db = forms.IntegerField(initial = 0, required = False)



def niceadd(l,name,value):
    if value is not None:
        l.append({'name':name,'value':value})

def nicedate(t):
    try:
        d = datetime.fromtimestamp(t)
        return '%s %s' % (format(d.date(),settings.DATE_FORMAT),time_format(d.time(),settings.TIME_FORMAT)) 
    except:
        return ''
    
fudge  = 1.25
hour   = 60.0 * 60.0
day    = hour * 24.0
week   = 7.0 * day
month  = 30.0 * day
def nicetimedelta(t):
    tdelta = timedelta(seconds = t)
    days    = tdelta.days
    sdays   = day * days
    delta   = tdelta.seconds + sdays
    if delta < fudge:
        return u'about a second'
    elif delta < (60.0 / fudge):
        return u'about %d seconds' % int(delta)
    elif delta < (60.0 * fudge):
        return u'about a minute'
    elif delta < (hour / fudge):
        return u'about %d minutes' % int(delta / 60.0)
    elif delta < (hour * fudge):
        return u'about an hour'
    elif delta < day:
        return u'about %d hours' % int(delta / hour)
    elif days == 1:
        return u'about 1 day'
    else:
        return u'about %s days' % days


class RedisMonitorPlugin(DJPplugin):
    form = RedisForm
    description = 'Redis monitor'
    
    def render(self, djp, wrapper, prefix,
               server = 'localhost',
               port = 6379,
               db = 0,
               **kwargs):
        r = redis.Redis(host = server, port = port, db = db)
        info = r.info()
        info1 = []
        niceadd(info1, 'Redis version', info['redis_version'])
        niceadd(info1, 'Process id', info['process_id'])
        niceadd(info1, 'Memory used', info['used_memory_human'])
        niceadd(info1, 'Up time', nicetimedelta(info['uptime_in_seconds']))
        niceadd(info1, 'Virtual Memory enabled', 'yes' if info['vm_enabled'] else 'no')
        niceadd(info1, 'Last save', nicedate(info['last_save_time']))
        niceadd(info1, 'Commands processed', info['total_commands_processed'])
        niceadd(info1, 'Connections received', info['total_connections_received'])
        return loader.render_to_string('monitor/redis_monitor.html',
                                       {'info1':info1})