import jenkins
import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.contrib.auth import login

from jauth.models import *
import logging
log = logging.getLogger(__name__)


@api_view(["POST"])
def get_token(request):
    url = request.data.get('url')
    username = request.data.get('username')
    password = request.data.get('password')

    log.debug('get_token is called with url:{}, username:{}, password:{}' \
        .format(url, username, password))

    server = jenkins.Jenkins(url, username=username, password=password)

    try:
        user_ = server.get_whoami()
        user, created = User.objects.get_or_create(username=username, first_name=password, last_name=url)
        if created:
            user.set_password(password)
            user.save()
            token = Token.objects.create(user=user)
            log.info('Token is created')
        else:
            token = Token.objects.get(user=user)
            log.info('Token is retrieved')        
    except Exception, e:
        log.debug(e)
        return Response({"status": "failed", 
                         "msg": "The credential or server url is not correct!"})

    return Response({"status": "success",
                     "token": token.key})


def login_only(function):
    def wrap(request, *args, **kwargs):
        token = request.META.get('HTTP_TOKEN')
        token = Token.objects.filter(key=token).first()
        if token:
            login(request, token.user)
            return function(request, *args, **kwargs)
        return Response({"status": "failed", "msg": "Auth token is invalid!"})

    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap


@api_view(["POST"])
@login_only
def create_job(request):
    log.info('create_job is called')

    url = request.user.last_name
    username = request.user.username
    password = request.user.first_name
    server = jenkins.Jenkins(url, username=username, password=password)

    name = request.data.get('name', '')
    config_xml = request.data.get('config_xml') or jenkins.EMPTY_CONFIG_XML

    log.debug('create_job is called with name:{}, config_xml:{}' \
        .format(name, config_xml))

    try:
        server.create_job(name, config_xml)
        jobs = server.get_jobs()
    except Exception, e:
        log.debug(e)
        return Response({"status": "failed", 
                         "msg": e.message or "Invalid job name"})

    log.info('The job:{} is created successfully'.format(name))
    return Response({"status": "success", "jobs": jobs})


@api_view(["POST"])
@login_only
def delete_job(request):
    url = request.user.last_name
    username = request.user.username
    password = request.user.first_name
    server = jenkins.Jenkins(url, username=username, password=password)

    name = request.data.get('name', '')
    log.debug('delete_job is called with name:{}'.format(name))

    try:
        server.delete_job(name)
        jobs = server.get_jobs()
    except Exception, e:
        log.debug(e)
        return Response({"status": "failed", 
                         "msg": e.message})

    log.info('The job:{} is deleted successfully'.format(name))
    return Response({"status": "success", "jobs": jobs})


@api_view(["POST"])
@login_only
def copy_job(request):
    url = request.user.last_name
    username = request.user.username
    password = request.user.first_name
    server = jenkins.Jenkins(url, username=username, password=password)

    from_name = request.data.get('from_name', '')
    to_name = request.data.get('to_name', '')
    log.debug('copy_job is called with from_name:{}, to_name:{}'.format(from_name, to_name))

    try:
        server.copy_job(from_name, to_name)
        jobs = server.get_jobs()
    except Exception, e:
        log.debug(e)
        return Response({"status": "failed", 
                         "msg": e.message or "Invalid job names"})

    log.info('The job:{} is copyed into job:{} successfully'.format(from_name, to_name))
    return Response({"status": "success", "jobs": jobs})





    server.build_job('empty')
    server.disable_job('empty')
    server.enable_job('empty_copy')
    server.reconfig_job('empty_copy', jenkins.RECONFIG_XML)

    # build a parameterized job
    # requires creating and configuring the api-test job to accept 'param1' & 'param2'
    server.build_job('api-test', {'param1': 'test value 1', 'param2': 'test value 2'})
    last_build_number = server.get_job_info('api-test')['lastCompletedBuild']['number']
    build_info = server.get_build_info('api-test', last_build_number)
    print build_info

    # get all jobs from the specific view
    jobs = server.get_jobs(view_name='View Name')
    print jobs
