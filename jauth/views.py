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


def get_server(request):
    url = request.user.last_name
    username = request.user.username
    password = request.user.first_name
    return jenkins.Jenkins(url, username=username, password=password)


@api_view(["POST"])
@login_only
def create_job(request):
    server = get_server(request)

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
    server = get_server(request)

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
    server = get_server(request)

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


@api_view(["POST"])
@login_only
def reconfig_job(request):
    server = get_server(request)

    name = request.data.get('name', '')
    config_xml = request.data.get('config_xml') or jenkins.RECONFIG_XML

    log.debug('reconfig_job is called with name:{}, config_xml:{}' \
        .format(name, config_xml))

    try:
        server.reconfig_job(name, config_xml)
        jobs = server.get_jobs()
    except Exception, e:
        log.debug(e)
        return Response({"status": "failed", 
                         "msg": e.message or "Invalid job name"})

    log.info('The job:{} is reconfigured successfully'.format(name))
    return Response({"status": "success", "jobs": jobs})


@api_view(["POST"])
@login_only
def status_job(request):
    server = get_server(request)

    name = request.data.get('name', '')
    depth = int(request.data.get('depth', 0))
    fetch_all_builds = request.data.get('fetch_all_builds', False)

    log.debug('status_job is called with name:{}, depth:{}, fetch_all_builds:{}' \
        .format(name, depth, fetch_all_builds))

    try:
        info = server.get_job_info(name, depth=depth, fetch_all_builds=fetch_all_builds)
    except Exception, e:
        log.debug(e)
        return Response({"status": "failed", 
                         "msg": e.message or "Invalid job name"})

    log.info('The job ({}) status is retrieved successfully'.format(name))
    return Response({"status": "success", "job_info": info})


@api_view(["POST"])
@login_only
def start_build(request):
    server = get_server(request)

    name = request.data.get('name', '')
    params = request.data.get('params')

    log.debug('start_build is called with name:{}, params:{}' \
        .format(name, params))

    try:
        next_build_number = server.get_job_info(name)['nextBuildNumber']
        server.build_job(name, params)
    except Exception, e:
        log.debug(e)
        return Response({"status": "failed", 
                         "msg": e.message or "Invalid job name"})

    log.info('The build of the job ({}) is started successfully'.format(name))
    return Response({"status": "success", "build_number": next_build_number})
    

@api_view(["POST"])
@login_only
def stop_build(request):
    server = get_server(request)

    name = request.data.get('name', '')
    number = request.data.get('build_number')

    log.debug('stop_build is called with name:{}, number:{}' \
        .format(name, number))

    try:
        server.stop_build(name, number)
    except Exception, e:
        log.debug(e)
        return Response({"status": "failed", 
                         "msg": e.message})

    log.info('The build of the job ({}) is stoped successfully'.format(name))
    return Response({"status": "success", "msg": "build stoped"})
