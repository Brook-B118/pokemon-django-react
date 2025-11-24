from .base import *
from config.env import env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=False)

# Allow any host in dev mode
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])