import dj_database_url
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

INSTALLED_APPS = [
    'django_ledger',
    'core.apps.CoreConfig',
    # ... outros apps ...
]

# Configurações adicionais para PyNFe e outros
PYNFE_CONFIG = {
    'certificado': config('PYNFE_CERTIFICADO', default=''),
    'senha': config('PYNFE_SENHA', default=''),
}