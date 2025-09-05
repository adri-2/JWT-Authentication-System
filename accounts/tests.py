from django.test import TestCase
import environ
# Create your tests here.

env = environ.Env(

    DEBUG=(bool, False)
)

print(env('SECRET_KEY'))
# DEBUG = env('DEBUG')