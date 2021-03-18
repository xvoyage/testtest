from flask import Blueprint

img = Blueprint('img', __name__)

from . import views