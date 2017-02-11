"""jenkins_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from jauth.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/get_token/$', get_token, name="get_token"),
    url(r'^api/v1/create_job/$', create_job, name="create_job"),
    url(r'^api/v1/copy_job/$', copy_job, name="copy_job"),    
    url(r'^api/v1/reconfig_job/$', reconfig_job, name="reconfig_job"), 
    url(r'^api/v1/status_job/$', status_job, name="status_job"),            
    url(r'^api/v1/start_build/$', start_build, name="start_build"), 
    url(r'^api/v1/stop_build/$', stop_build, name="stop_build"),                    
    url(r'^api/v1/delete_job/$', delete_job, name="delete_job"),
]
