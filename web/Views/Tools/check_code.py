import json

from io import BytesIO
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from utils.check_code import create_validate_code
from repository import models
def make_code(request):
    stream=BytesIO()
    img,code = create_validate_code()
    img.save(stream,'PNG')
    request.session['CheckCode']=code
    return HttpResponse(stream.getvalue())