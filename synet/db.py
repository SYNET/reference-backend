#
# Makes objects from epg.models live in separate database
# 
class Router(object):
    """A router to control all database operations on models in
    the myapp application"""

    def db_for_read(self, model, **hints):
        "Point all operations on myapp models to 'other'"
        if model._meta.app_label == 'epg':
            return 'epg'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on myapp models to 'other'"
        if model._meta.app_label == 'epg':
            return 'epg'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'epg' or obj2._meta.app_label == 'epg':
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the epg data only appears on the 'epg' db"
        if db == 'epg':
            return model._meta.app_label == 'epg'
        elif model._meta.app_label == 'epg':
            return False
        return None