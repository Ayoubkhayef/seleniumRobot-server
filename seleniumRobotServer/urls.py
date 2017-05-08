"""seleniumRobotServer URL Configuration

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
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers

from django.conf import settings
from snapshotServer import views, viewsets
from snapshotServer.views.CompareSnapshot import SessionList, TestList, StepList, \
    PictureView
from snapshotServer.views.FileUploadView import FileUploadView


router = routers.DefaultRouter()
router.register(r'users', viewsets.UserViewSet)
router.register(r'snapshot', viewsets.SnapshotViewSet)
router.register(r'application', viewsets.ApplicationViewSet)
router.register(r'version', viewsets.VersionViewSet)
router.register(r'testcase', viewsets.TestCaseViewSet) 
router.register(r'environment', viewsets.TestEnvironmentViewSet)
router.register(r'teststep', viewsets.TestStepViewSet)
router.register(r'groups', viewsets.GroupViewSet)
router.register(r'session', viewsets.TestSessionViewSet)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^upload/(?P<filename>[^/]+)$', FileUploadView.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    url(r'^compare/$', SessionList.as_view()),
    url(r'^compare/testList/([0-9]+)/$', TestList.as_view(), name="testlistView"),  # /sessionId/
    url(r'^compare/stepList/([0-9]+)/([0-9]+)/$', StepList.as_view(), name="steplistView"), # /sessionId/testCase/
    url(r'^compare/picture/([0-9]+)/([0-9]+)/([0-9]+)/$', PictureView.as_view(), name="pictureView"), # /sessionId/testCase/testStep
    
    # add media directory
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)[0],
]