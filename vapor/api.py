
import os
import json
import steamapi
from datetime import datetime
from pymendez.auth import auth


BACKUPFILE = os.path.expanduser('~/data/steam/gametime.json')


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj
 
def object_hook(obj):
  if 'date' in obj:
    obj['date'] = dateutil.parser.parse(obj['date']) 
  return obj


class Data(object):
    '''The json dictionary container that holds the all of the song data.'''
    def __init__(self, filename, fcn=list):
        self.filename = filename
        self.fcn = fcn
    
    def __iter__(self):
        for item in self.data:
            yield item
    
    def insert(self, index, item):
      self.data.insert(index, item)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __enter__(self, *args, **kwargs):
        try:
            self.data = json.load(open(self.filename),
                                  object_hook=object_hook)
        except Exception as e:
            print e
            print ' Failed to load: {}'.format(self.filename)
            self.data = self.fcn()
        return self
    
    def __exit__(self, *args, **kwargs):
        directory = os.path.dirname(self.filename)
        print directory
        if not os.path.exists(directory):
            os.makedirs(directory)
        json.dump(self.data, 
                  open(self.filename,'w'),
                  default=date_handler,
                  indent=2)



class Vapor(object):
    def __init__(self, key=None, username=None):
        
        if key is None:
            key,username = auth('steam',['key','username'])
        self.key = key
        self.username = username
        self.api = steamapi.core.APIConnection(api_key=key)
        self.user = steamapi.user.SteamUser(userurl=username)
    
    def games(self):
        for game in self.user.games:
            yield game.id, game.name, game.playtime_forever
    
    
    def makebackup(self):
        out = dict(date=datetime.now())
        out['games'] = {ident:[name,time] for ident,name,time in self.games()}
        return out
    
    def backup(self, filename=BACKUPFILE):
        with Data(filename) as data:
            item = [self.user.name, self.user.id, self.user.last_logoff]
            try:
                data[0] = item
            except:
                data.insert(0,item)
            data.insert(1, self.makebackup())
    
    
    
    
    