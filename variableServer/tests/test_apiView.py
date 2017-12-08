import django.test
from django.urls.base import reverse
from variableServer.utils.utils import SPECIAL_NONE, updateVariables
from variableServer.models import Variable, Application, Version,\
    TestEnvironment, TestCase
import time
import datetime
from datetime import timezone

class test_FileUploadView(django.test.TestCase):
    fixtures = ['varServer.yaml']

    
    def setUp(self):
        pass
    
#     def test__updateVariables(self):
#         """
#         check that updateVariable keeps the variable from additionalQuerySet parameters when it overrides one from sourceQuerySet
#         """
#         sourceQuerySet = Variable.objects.filter(application=None, version=None, environment=None, test=None)
#         additionalQuerySet = Variable.objects.filter(application=None, version=None, environment=1, test=None)
#         
#         resultingQS = updateVariables(sourceQuerySet, additionalQuerySet)
#         
#         self.assertEquals(resultingQS.get(name='proxyPassword').value, 'devPassword')
#     
#     def test_severalUpdateVariables(self):
#         """
#         check that several updateVariables calls can be chained
#         """
#         sourceQuerySet = Variable.objects.filter(application=None, version=None, environment=None, test=None)
#         additionalQuerySet = Variable.objects.filter(application=None, version=None, environment=1, test=None)
#         
#         resultingQS = updateVariables(sourceQuerySet, additionalQuerySet)
#         otherQuerySet = Variable.objects.filter(application=2, version=None, environment=None, test=None)
#         resultingQS = updateVariables(resultingQS, otherQuerySet)
#         
#         self.assertEquals(resultingQS.get(name='proxyPassword').value, 'devPassword')
#         self.assertEquals(resultingQS.get(name='appName').value, 'myApp')

    def _convertToDict(self, responseData):
        variableDict = {}
        for variable in responseData:
            variableDict[variable['name']] = variable
            
        return variableDict
    
    def test_getAllVariables(self):
        """
        Check a reference is created when non is found
        """
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        
        # check filtering is correct. We should not get any variable corresponding to an other environment, test or version
        for variable in response.data:
            self.assertTrue(variable['environment'] in [1, 3, None], "variable %s should not be get as environment is different from 1, 3 and None" % variable['name'])
            self.assertTrue(variable['version'] in [2, None], "variable %s should not be get as version is different from 2 and None" % variable['name'])
            self.assertTrue(variable['test'] in [1, None], "variable %s should not be get as test is different from 1 and None" % variable['name'])
            
        # check we get variables from the generic environment
        for variable in response.data:
            if variable['name'] == 'logs' and variable['environment'] == 1:
                break
        else:
            self.fail("No variable from generic environment get");
        
        
        
    def test_getAllVariablesWithReleaseDate(self):
        """
        Check that release dates are correctly managed
        variable is returned if
        - releaseDate is None
        - releaseDate is in the past (then it should be set to None)
        """
        version = Version.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application, version=version).save()
        Variable(name='var1', value='value1', application=version.application, version=version, releaseDate=datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(seconds=60)).save()
        Variable(name='var2', value='value2', application=version.application, version=version, releaseDate=datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(seconds=60)).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': 3, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check we only get variable where release date is before now and variables without release date
        self.assertTrue('var2' in allVariables)                 # release date in the past, should be removed
        self.assertIsNone(allVariables['var2']['releaseDate'])  # release date should be reset
        self.assertFalse('var1' in allVariables)                # release date in the future  
        self.assertTrue('var0' in allVariables)                 # no release date
        
    def test_getVariablesOverrideGlobal(self):
        """
        Check that global variables are overriden by application specific variables
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        Variable(name='var0', value='value0').save()
        Variable(name='var0', value='value1', application=version.application).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
        
    def test_getVariablesOverrideAppSpecific(self):
        """
        Check that application specific variables are overriden by application/version specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application).save()
        Variable(name='var0', value='value1', application=version.application, version=version).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
        
    def test_getVariablesOverrideVersionSpecific(self):
        """
        Check that application/version specific variables are overriden by environment specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application, version=version).save()
        Variable(name='var0', value='value1', environment=env).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
            
    def test_getVariablesOverrideGenericEnvironment(self):
        """
        Check that application/version specific variables are overriden by environment specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        genEnv = TestEnvironment.objects.get(pk=1)
        Variable(name='var0', value='value0', environment=genEnv).save()
        Variable(name='var0', value='value1', environment=env).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
            
    def test_getVariablesOverrideEnvironment(self):
        """
        Check that environment specific variables are overriden by test specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        test = TestCase.objects.get(pk=1)
        Variable(name='var0', value='value0', environment=env).save()
        Variable(name='var0', value='value1', application=version.application, test=test).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
            
    def test_getVariablesOverrideTest(self):
        """
        Check that test specific variables are overriden by application/env specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        test = TestCase.objects.get(pk=1)
        Variable(name='var0', value='value0', test=test).save()
        Variable(name='var0', value='value1', application=version.application, environment=env).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
            
    def test_getVariablesOverrideAppEnv(self):
        """
        Check that application/env specific variables are overriden by application/version/env specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application, environment=env).save()
        Variable(name='var0', value='value1', application=version.application, version=version, environment=env).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
            
    def test_getVariablesOverrideAppVersionEnv(self):
        """
        Check that application/version/env specific variables are overriden by application/version/env/test specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        test = TestCase.objects.get(pk=1)
        Variable(name='var0', value='value0', application=version.application, version=version, environment=env).save()
        Variable(name='var0', value='value1', application=version.application, version=version, environment=env, test=test).save()
        
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
        
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
        
    def test_getAllVariablesWithSameName(self):
        """
        Check we get only one value for the variable 'dupVariable'
        """
        response = self.client.get(reverse('variableApi'), data={'version': 4, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        
        self.assertEqual(1, len([v for v in response.data if v['name'] == 'dupVariable']), "Only one value should be get")
        
        allVariables = self._convertToDict(response.data)
        self.assertEqual(None, allVariables['dupVariable']['releaseDate'], 'releaseDate should be null as variable is not reservable')
            
    def test_reserveVariable(self):
        """
        Check we get only one value for the variable 'login' and this is marked as reserved (release date not null)
        """
        response = self.client.get(reverse('variableApi'), data={'version': 4, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
      
        self.assertEqual(1, len([v for v in response.data if v['name'] == 'login']), "Only one value should be get")
        allVariables = self._convertToDict(response.data)
        self.assertNotEqual(None, allVariables['login']['releaseDate'], 'releaseDate should not be null as variable is reserved')
        
    def test_reservableStateCorrection(self):
        version = Version.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application, reservable=True).save()
        
        response = self.client.post(reverse('variableApi'), data={'name': 'var0', 'value': 'value1', 'application': version.application.id, 'reservable': False})
        self.assertEqual(response.status_code, 201, 'status code should be 200: ' + str(response.content))
      
        for v in Variable.objects.filter(name='var0'):
            self.assertFalse(v.reservable)
         
        
        
        