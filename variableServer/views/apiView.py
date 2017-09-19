'''
Created on 15 sept. 2017

@author: s047432
'''
from rest_framework import mixins, generics
 
from variableServer.views.serializers import VariableSerializer
from variableServer.models import Variable, TestEnvironment, Version, TestCase
from variableServer.utils.utils import SPECIAL_NONE, SPECIAL_NOT_NONE,\
    updateVariables
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from seleniumRobotServer.wsgi import application
from django.shortcuts import get_object_or_404
import datetime
import time

class VariableList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  generics.GenericAPIView):
    
    serializer_class = VariableSerializer
    
    def _resetPastReleaseDates(self):
        for var in Variable.objects.filter(releaseDate__lte=time.strftime('%Y-%m-%d %H:%M:%S')):
            var.releaseDate = None
            var.save()
        
    
    def get_queryset(self):
        """

        """
        versionId = self.request.query_params.get('version', None)
        if not versionId:
            raise ValidationError("version parameter is mandatory")
        version = get_object_or_404(Version, pk=versionId)
        
        environmentId = self.request.query_params.get('environment', None)
        if not environmentId:
            raise ValidationError("environment parameter is mandatory")
        environment = get_object_or_404(TestEnvironment, pk=environmentId)
        
        testId = self.request.query_params.get('test', None)
        if not testId:
            raise ValidationError("test parameter is mandatory")
        test = get_object_or_404(TestCase, pk=testId)
        
        variables = Variable.objects.filter(application=None, version=None, environment=None, test=None)
        
        # variables specific to one of the parameters, the other remain null
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=None, environment=None, test=None))
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=version, environment=None, test=None))
        
        # for each queryset depending on environment, we will first get the generic environment related variable and then update them
        # with the specific environment ones
        if environment.genericEnvironment:
            genericEnvironment = environment.genericEnvironment
        else:
            genericEnvironment = environment
        
        variables = updateVariables(variables, Variable.objects.filter(application=None, version=None, test=None, environment=genericEnvironment))
        variables = updateVariables(variables, Variable.objects.filter(application=None, version=None, test=None, environment=environment))
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=None, environment=None, test=test))
        
        # more precise variables
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=None, environment=genericEnvironment, test=None))
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=None, environment=environment, test=None))
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=version, environment=genericEnvironment, test=None))
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=version, environment=environment, test=None))
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=version, environment=genericEnvironment, test=test))
        variables = updateVariables(variables, Variable.objects.filter(application=version.application, version=version, environment=environment, test=test))
        
        return variables.filter(releaseDate=None)
        

    def get(self, request, *args, **kwargs):
        """
        Get all variables corresponding to requested args
        """
        # reset 
        self._resetPastReleaseDates()
        
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    