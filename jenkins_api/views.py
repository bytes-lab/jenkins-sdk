import random
from github import Github
from github.GithubException import GithubException

from rest_framework.decorators import api_view
from rest_framework.response import Response

from gauth.models import *
import logging
log = logging.getLogger(__name__)


@api_view(["POST"])
def signup(request):
    email = request.data.get('email', '')
    password = request.data.get('password', '')
    # first_name = request.data.get('first_name')
    # last_name = request.data.get('last_name')   

    log.debug("Get token with email:{}".format(email))
    try:
        g = Github(email, password)
        guser = g.get_user()
        email_ = guser.email
    except Exception, e:
        log.error('Github credential is not correct')
        return Response({'error': 'Please provide a valid email and password!'})

    try:
        user = User.objects.create(username=email, email=email)
        user.set_password(password)
        user.save()
        log.info('Token is created')
    except Exception, e:
        # raise
        log.error('The user already exists!')
        return Response({'error': 'The user already exists!'})

    token = guser.create_authorization(["user", "repo", "admin:org"], 
        "token for {}.{}".format(email, random.randint(1, 10000))).token
    GAuth.objects.create(user=user, token=token)

    return Response({"success": 1,
                     "token": token})


@api_view(["POST", "GET"])
def repos(request, org):
    token = request.META.get('HTTP_TOKEN')
    log.debug('Repo management')
    if not GAuth.objects.filter(token=token).exists():
        return Response({'error': 'Please provide a valid token!'})

    try:
        g = Github(token)
        org = g.get_organization(org)
    except Exception, e:
        log.error('There is no such organization')
        return Response({'error': 'Please provide a valid organization!'})

    if request.method == "POST":        # create a repo
        try:
            repo_name = request.data.get('repo_name')
            private = request.data.get('private', False)
            repo = org.create_repo(repo_name, private=private)
        except GithubException, e:
            e.data['status'] = e.status
            log.error(str(e.data))
            return Response(e.data)

        log.info('Repo is created successfully.')
        return Response({"success": 1,
                         "id": repo.id})
    else:
        repos = [{"name": item.name, "id": item.id, "private": item.private} for item in org.get_repos()]
        log.info('The list of repos is returned')
        return Response({"success": 1,
                         "repos": repos})


@api_view(["POST", "GET"])
def teams(request, org):
    token = request.META.get('HTTP_TOKEN')
    log.debug('Team management')
    if not GAuth.objects.filter(token=token).exists():
        return Response({'error': 'Please provide a valid token!'})

    try:
        g = Github(token)
        org = g.get_organization(org)
    except Exception, e:
        log.error('There is no such organization')
        return Response({'error': 'Please provide a valid organization!'})

    if request.method == "POST":        # create a team
        try:
            team_name = request.data.get('team_name')
            privacy = request.data.get('privacy', 'closed')
            team = org.create_team(team_name, privacy=privacy)
        except GithubException, e:
            e.data['status'] = e.status
            log.error(str(e.data))
            return Response(e.data)
            
        log.info('Team is created successfully')
        return Response({"success": 1,
                         "id": team.id})
    else:
        teams = [{"name": item.name, "id": item.id} for item in org.get_teams()]
        log.info('The list of teams is returned')
        return Response({"success": 1,
                         "teams": teams})


@api_view(["POST", "GET"])
def members(request, org, team):
    log.debug("Member management")
    token = request.META.get('HTTP_TOKEN')

    if not GAuth.objects.filter(token=token).exists():
        return Response({'error': 'Please provide a valid token!'})

    try:
        g = Github(token)
        org = g.get_organization(org)
    except Exception, e:
        log.error('There is no such organization')
        return Response({'error': 'Please provide a valid organization!'})

    try:
        team = org.get_team(int(team))
    except Exception, e:
        log.error('There is no such team')
        return Response({'error': 'Please provide a valid team id!'})

    if request.method == "POST":        # create a repo
        try:
            member = g.get_user(request.data.get('member_login'))
        except Exception, e:
            log.error('There is no such member')
            return Response({'error': 'Please provide a valid member login!'})
            
        action = request.data.get('action')
        if action == 'remove':
            log.info('The member is removed')
            team.remove_from_members(member)
        else:
            log.info('The member is invited')
            team.add_membership(member)

        return Response({"success": 1})
    else:
        members = [{"login": item.login, "id": item.id} for item in team.get_members()]
        log.info('The list of members is returned')
        return Response({"success": 1,
                         "members": members})


@api_view(["POST"])
def assign_repo(request, org, team):
    token = request.META.get('HTTP_TOKEN')
    log.debug('Assign a repo')
    if not GAuth.objects.filter(token=token).exists():
        return Response({'error': 'Please provide a valid token!'})

    try:
        g = Github(token)
        org = g.get_organization(org)
    except Exception, e:
        log.error('There is no such organization')
        return Response({'error': 'Please provide a valid organization!'})

    try:
        repo_name = request.data.get('repo_name')
        repo = org.get_repo(repo_name)
    except Exception, e:
        log.error('There is no such repo')
        return Response({'error': 'Please provide a valid repo name!'})

    try:
        team = org.get_team(int(team))
    except Exception, e:
        log.error('There is no such team')
        return Response({'error': 'Please provide a valid team id!'})

    permission = request.data.get('permission', 'pull')
    team.add_to_repos(repo, permission)
    log.info('The repo is assigned to the team')
    return Response({"success": 1})
