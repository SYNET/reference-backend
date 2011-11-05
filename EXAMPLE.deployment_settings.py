# this should be a random key
# generate one with : 
#  openssl rand -hex 16
#
SYNET_API_KEY = ''


# Absolute path to the directory static files should be collected to.
STATIC_ROOT = '/var/synet/www/static'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'synet',                      # Or path to database file if using sqlite3.
        'USER': 'synet',                      # Not used with sqlite3.
        'PASSWORD': 'synet',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'epg': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'epg',                      # Or path to database file if using sqlite3.
        'USER': 'synet',                      # Not used with sqlite3.
        'PASSWORD': 'synet',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
