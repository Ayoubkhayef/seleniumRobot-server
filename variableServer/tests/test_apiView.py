import django.test
from django.urls.base import reverse
from variableServer.utils.utils import SPECIAL_NONE, updateVariables
from variableServer.models import Variable, Application, Version,\
    TestEnvironment, TestCase
import time
import datetime
from django.utils import timezone

from rest_framework.test import APITestCase

class test_FileUploadView(APITestCase):
    '''
    Using APITestCase as we call the REST Framework API
    Client handles patch / put cases
    '''
    fixtures = ['varServer.yaml']

    
    def setUp(self):
        pass
    
    def test__updateVariables(self):
        """
        check that updateVariable keeps the variable from additional_query_set parameters when it overrides one from source_query_set
        """
        source_query_set = Variable.objects.filter(application=None, version=None, environment=None, test=None)
        additional_query_set = Variable.objects.filter(application=None, version=None, environment=1, test=None)
         
        resulting_qs = updateVariables(source_query_set, additional_query_set)
         
        self.assertEquals(resulting_qs.get(name='proxyPassword').value, 'azerty')
     
    def test_severalUpdateVariables(self):
        """
        check that several updateVariables calls can be chained
        """
        source_query_set = Variable.objects.filter(application=None, version=None, environment=None, test=None)
        additional_query_set = Variable.objects.filter(application=None, version=None, environment=1, test=None)
         
        resulting_qs = updateVariables(source_query_set, additional_query_set)
        other_query_set = Variable.objects.filter(application=2, version=None, environment=None, test=None)
        resulting_qs = updateVariables(resulting_qs, other_query_set)
         
        self.assertEquals(resulting_qs.get(name='proxyPassword').value, 'azerty')
        self.assertEquals(resulting_qs.get(name='appName').value, 'myOtherApp')

    def _convertToDict(self, responseData):
        variable_dict = {}
        for variable in responseData:
            variable_dict[variable['name']] = variable
             
        return variable_dict
     
    def test_get_all_variables(self):
        """
        Check a reference is created when none is found
        """
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
             
        # check filtering is correct. We should not get any variable corresponding to an other environment, test or version
        for variable in response.data:
            self.assertTrue(variable['environment'] in [1, 3, None], "variable %s should not be get as environment is different from 1, 3 and None" % variable['name'])
            self.assertTrue(variable['version'] in [2, None], "variable %s should not be get as version is different from 2 and None" % variable['name'])
            self.assertTrue(variable['test'] in [[1], []], "variable %s should not be get as test is different from 1 and []" % variable['name'])
                 
        # check we get variables from the generic environment
        for variable in response.data:
            if variable['name'] == 'logs' and variable['environment'] == 1:
                break
        else:
            self.fail("No variable from generic environment get")
            
        print("taille ---" + str(len(response.data)))
        self.assertTrue(len(response.data) > 5)
            
         
    def test_get_all_variables_with_name(self):
        """
        Check we filter variables by name and get only one variable
        """
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1, 'name': 'proxyPassword'})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
             
        # check filtering is correct. We should not get any variable corresponding to an other environment, test or version
        for variable in response.data:
            self.assertEquals(variable['name'], 'proxyPassword')
        
        self.assertEquals(len(response.data), 1)
        
    def test_get_all_variables_with_value(self):
        """
        Check we filter variables by value and get only one variable
        """
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1, 'value': 'logs_dev'})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
             
        # check filtering is correct. We should not get any variable corresponding to an other environment, test or version
        for variable in response.data:
            self.assertEquals(variable['value'], 'logs_dev')
            self.assertEquals(variable['name'], 'logs')
        
        self.assertEquals(len(response.data), 1)
    
    def test_get_all_variables_with_name_and_value(self):
        """
        Check we filter variables by value/name and get only one variable
        """
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1, 'name': 'logs', 'value': 'logs_dev'})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
             
        # check filtering is correct. We should not get any variable corresponding to an other environment, test or version
        for variable in response.data:
            self.assertEquals(variable['value'], 'logs_dev')
            self.assertEquals(variable['name'], 'logs')
        
        self.assertEquals(len(response.data), 1)
    
    def test_get_all_variables_with_name_and_value_reserved(self):
        """
        Check we filter variables by value/name and get only one variable
        """
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1, 'name': 'login'})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
             
        # check filtering is correct. We should not get any variable corresponding to an other environment, test or version
        for variable in response.data:
            self.assertEquals(variable['name'], 'login')
            
        self.assertTrue(Variable.objects.get(pk=response.data[0]['id']), "returned variable should be reserved")

             
    def test_getAllVariablesWithoutTest(self):
        """
        Check that test parameter is not mandatory
        """
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
            
        # check filtering is correct. We should not get any variable corresponding to an other environment, test or version
        for variable in response.data:
            self.assertTrue(variable['environment'] in [1, 3, None], "variable %s should not be get as environment is different from 1, 3 and None" % variable['name'])
            self.assertTrue(variable['version'] in [2, None], "variable %s should not be get as version is different from 2 and None" % variable['name'])
            self.assertTrue(variable['test'] in [[1], []], "variable %s should not be get as test is different from 1 and []" % variable['name'])
                
        # check we get variables from the generic environment
        for variable in response.data:
            if variable['name'] == 'logs' and variable['environment'] == 1:
                break
        else:
            self.fail("No variable from generic environment get")
             
    def test_getAllVariablesWithoutEnvironment(self):
        """
        Check that environment parameter is  mandatory
        """
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'test': 1})
        self.assertEqual(response.status_code, 400, 'status code should be 400: ' + str(response.content))
         
    def test_getAllVariablesWithoutVersion(self):
        """
        Check that environment parameter is  mandatory
        """
        response = self.client.get(reverse('variableApi'), data={'test': 1, 'environment': 3})
        self.assertEqual(response.status_code, 400, 'status code should be 400: ' + str(response.content))
            
       
    def test_getAllVariablesWithText(self):
        """
        Check Variables are get when requesting them with environment name, application name, test name, ...
        """
        response = self.client.get(reverse('variableApi'), data={'application': 'app1', 'version': '2.5', 'environment': 'DEV1', 'test': 'test1 with some spaces'})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
            
        # check filtering is correct. We should not get any variable corresponding to an other environment, test or version
        for variable in response.data:
            self.assertTrue(variable['environment'] in [1, 3, None], "variable %s should not be get as environment is different from 1, 3 and None" % variable['name'])
            self.assertTrue(variable['version'] in [2, None], "variable %s should not be get as version is different from 2 and None" % variable['name'])
            self.assertTrue(variable['test'] in [[1], []], "variable %s should not be get as test is different from 1 and None" % variable['name'])
                
        # check we get variables from the generic environment
        for variable in response.data:
            if variable['name'] == 'logs' and variable['environment'] == 1:
                break
        else:
            self.fail("No variable from generic environment get");
              
    def test_getAllVariablesWithTextMissingApplication(self):
        """
        Check error is raised when application name is missing (mandatory for finding version from its name)
        """
        response = self.client.get(reverse('variableApi'), data={'version': '2.5', 'environment': 'DEV1', 'test': 'test1 with some spaces'})
        self.assertEqual(response.status_code, 400, 'status code should be 400: ' + str(response.content))
   
            
    def test_getAllVariablesWithReleaseDate(self):
        """
        Check that release dates are correctly managed
        variable is returned if
        - releaseDate is None
        - releaseDate is in the past (then it should be set to None)
        """
        version = Version.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application, version=version).save()
        Variable(name='var1', value='value1', application=version.application, version=version, releaseDate=timezone.now() + datetime.timedelta(seconds=60)).save()
        Variable(name='var1', value='value2', application=version.application, version=version, releaseDate=timezone.now() - datetime.timedelta(seconds=60)).save()
             
        response = self.client.get(reverse('variableApi'), data={'version': 3, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        self.assertEqual(1, len([v for v in response.data if v['name'] == 'var1']), "Only one value should be get")
             
        all_variables = self._convertToDict(response.data)
             
        # check we only get variable where release date is before now and variables without release date
        self.assertTrue('var1' in all_variables)                 # release date in the past, should be removed
        self.assertEqual("value2", all_variables['var1']['value'])
        self.assertIsNone(all_variables['var1']['releaseDate'])  # release date should be reset 
        self.assertTrue('var0' in all_variables)                 # no release date
             
    def test_getVariablesOverrideGlobal(self):
        """
        Check that global variables are overriden by application specific variables
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        Variable(name='var0', value='value0').save()
        Variable(name='var0', value='value1', application=version.application).save()
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        all_variables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(all_variables['var0']['value'], 'value1')
             
    def test_getVariablesOverrideAppSpecific(self):
        """
        Check that application specific variables are overriden by application/version specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application).save()
        Variable(name='var0', value='value1', application=version.application, version=version).save()
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        all_variables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(all_variables['var0']['value'], 'value1')
             
    def test_getVariablesOverrideVersionSpecific(self):
        """
        Check that application/version specific variables are overriden by environment specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application, version=version).save()
        Variable(name='var0', value='value1', environment=env).save()
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        all_variables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(all_variables['var0']['value'], 'value1')
                 
    def test_getVariablesOverrideGenericEnvironment(self):
        """
        Check that application/version specific variables are overriden by environment specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        gen_env = TestEnvironment.objects.get(pk=1)
        Variable(name='var0', value='value0', environment=gen_env).save()
        Variable(name='var0', value='value1', environment=env).save()
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        all_variables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(all_variables['var0']['value'], 'value1')
                 
    def test_getVariablesOverrideEnvironment(self):
        """
        Check that environment specific variables are overriden by test specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        test = TestCase.objects.get(pk=1)
        Variable(name='var0', value='value0', environment=env).save()
        var1 = Variable(name='var0', value='value1', application=version.application)
        var1.save()
        var1.test.add(test)
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        all_variables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(all_variables['var0']['value'], 'value1')
                 
    def test_getVariablesOverrideTest(self):
        """
        Check that test specific variables are overriden by application/env specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        test = TestCase.objects.get(pk=1)
        var0 = Variable(name='var0', value='value0')
        var0.save()
        var0.test.add(test)
        Variable(name='var0', value='value1', application=version.application, environment=env).save()
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        all_variables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(all_variables['var0']['value'], 'value1')
                 
    def test_getVariablesOverrideAppEnv(self):
        """
        Check that application/env specific variables are overriden by application/version/env specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application, environment=env).save()
        Variable(name='var0', value='value1', application=version.application, version=version, environment=env).save()
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        all_variables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(all_variables['var0']['value'], 'value1')
                 
    def test_getVariablesOverrideAppVersionEnv(self):
        """
        Check that application/version/env specific variables are overriden by application/version/env/test specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        test = TestCase.objects.get(pk=1)
        Variable(name='var0', value='value0', application=version.application, version=version, environment=env).save()
        var1 = Variable(name='var0', value='value1', application=version.application, version=version, environment=env)
        var1.save()
        var1.test.add(test)
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        allVariables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(allVariables['var0']['value'], 'value1')
                 
    def test_getVariablesOverrideAppEnvTest(self):
        """
        Check that application/version/env specific variables are overriden by application/env/test specific
        Order is (bottom take precedence):
        - global (no app, no env, no version, no test)
        - specific to on of the parameter (matching app or matching version or matching env or matching test in this order)
        - specific to tuple (application / environment)
        - specific to tuple (application / version / environment)
        - specific to tuple (application / environment / test)
        - specific to tuple (application / version / environment / test)
        """
        version = Version.objects.get(pk=3)
        env = TestEnvironment.objects.get(pk=3)
        test = TestCase.objects.get(pk=1)
        Variable(name='var0', value='value0', application=version.application, version=version, environment=env).save()
        var1 = Variable(name='var0', value='value1', application=version.application, environment=env)
        var1.save()
        var1.test.add(test)
             
        response = self.client.get(reverse('variableApi'), data={'version': version.id, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
        all_variables = self._convertToDict(response.data)
             
        # check overriding of variables
        self.assertEqual(all_variables['var0']['value'], 'value1')
             
    def test_getAllVariablesWithSameName(self):
        """
        Check we get only one value for the variable 'dupVariable'
        """
        response = self.client.get(reverse('variableApi'), data={'version': 4, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
             
        self.assertEqual(1, len([v for v in response.data if v['name'] == 'dupVariable']), "Only one value should be get")
             
        all_variables = self._convertToDict(response.data)
        self.assertIsNone(all_variables['dupVariable']['releaseDate'], 'releaseDate should be null as variable is not reservable')
                 
    def test_reserveVariable(self):
        """
        Check we get only one value for the variable 'login' and this is marked as reserved (release date not null)
        """
        response = self.client.get(reverse('variableApi'), data={'version': 4, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
           
        self.assertEqual(1, len([v for v in response.data if v['name'] == 'login']), "Only one value should be get")
        all_variables = self._convertToDict(response.data)
        self.assertIsNotNone(all_variables['login']['releaseDate'], 'releaseDate should not be null as variable is reserved')
             
    def test_reservable_state_correction(self):
        """
        Check that when a variable is added with the same characteristics of another, reservable state is set to the newly created variable
        """
        version = Version.objects.get(pk=3)
        Variable(name='var0', value='value0', application=version.application, reservable=True).save()
             
        response = self.client.post(reverse('variableApi'), data={'name': 'var0', 'value': 'value1', 'application': version.application.id, 'reservable': False})
        self.assertEqual(response.status_code, 201, 'status code should be 201: ' + str(response.content))
           
        for v in Variable.objects.filter(name='var0'):
            self.assertFalse(v.reservable)
              
             
    def test_reservable_state_correction_with_test(self):
        """
        Check that when a variable is added with the same characteristics of another, reservable state is set to the newly created variable
        Check with test as ManyToMany relationship must be treated seperately
        """
        test = TestCase.objects.get(pk=1)
        version = Version.objects.get(pk=3)
        var0 = Variable(name='var0', value='value0', application=version.application, reservable=True)
        var0.save()
        var0.test.add(test)
             
        response = self.client.post(reverse('variableApi'), data={'name': 'var0', 'value': 'value1', 'application': version.application.id, 'reservable': False, 'test': [1]})
        self.assertEqual(response.status_code, 201, 'status code should be 201: ' + str(response.content))
           
        for v in Variable.objects.filter(name='var0'):
            self.assertFalse(v.reservable)
            
    def test_update_reservable_state_correction_with_test(self):
        """
        Check that when a variable is changed with the same characteristics of another, reservable state is set to the updated variable
        Check with test as ManyToMany relationship must be treated seperately
        """
        test = TestCase.objects.get(pk=1)
        version = Version.objects.get(pk=3)
        var0 = Variable(name='var0', value='value0', application=version.application, reservable=True)
        var0.save()
        var0.test.add(test)
        var1 = Variable(name='var0', value='value0', application=version.application, reservable=True)
        var1.save()
            
        response = self.client.patch(reverse('variableApiPut', args=[var1.id]), {'reservable': False, 'test': [1]})
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
          
        for v in Variable.objects.filter(name='var0'):
            self.assertFalse(v.reservable)
              
          
    def test_variableAlreadyReserved(self):
        """
        When variable cannot be reserved because all are alrealdy taken by other test, an error should be raised
        """
        # login variable is defined twice, reserve it 3 times
        self.client.get(reverse('variableApi'), data={'version': 4, 'environment': 3, 'test': 1})
        self.client.get(reverse('variableApi'), data={'version': 4, 'environment': 3, 'test': 1})
        response = self.client.get(reverse('variableApi'), data={'version': 4, 'environment': 3, 'test': 1})
        self.assertEqual(response.status_code, 423, 'status code should be 423: ' + str(response.content))
        self.assertTrue(b'login' in response.content)
           
        
    def test_destroyOldVariables(self):
        """
        Check that if a variable reached its max number of days, it's automatically removed
        """
            
        version = Version.objects.get(pk=2)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='oldVar', value='oldValue', application=version.application, version=version, environment=env, 
                 creationDate=datetime.datetime.now() - datetime.timedelta(2), 
                 timeToLive=1).save()
            
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1})
            
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
            
        all_variables = self._convertToDict(response.data)
           
        self.assertNotIn('oldVar', all_variables, "oldVar should be removed, as it's too old")
            
    def test_doNotdestroyNotsoOldVariables(self):
        """
        Check that if a variable did not reach its max number of days, it's not removed
        """
            
        version = Version.objects.get(pk=2)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='oldVar', value='oldValue', application=version.application, version=version, environment=env, 
                 creationDate=datetime.datetime.now() - datetime.timedelta(1), 
                 timeToLive=1).save()
            
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1})
            
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
            
        all_variables = self._convertToDict(response.data)
           
        self.assertIn('oldVar', all_variables, "oldVar should not be removed, as it's not old enough")
    
    def test_returnVariablesOlderThanXDays(self):
        """
        Check that we get only variables older than X days
        """
             
        version = Version.objects.get(pk=2)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='oldVar', value='oldValue1', application=version.application, version=version, environment=env, 
                 creationDate=datetime.datetime.now() - datetime.timedelta(2), 
                 timeToLive=5).save()
        Variable(name='oldVar2', value='oldValue2', application=version.application, version=version, environment=env, 
                 creationDate=datetime.datetime.now() - datetime.timedelta(1), 
                 timeToLive=5).save()
             
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1, 'olderThan': 1})
             
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
             
        all_variables = self._convertToDict(response.data)
            
        self.assertIn('oldVar', all_variables, "oldVar should be get as it's older than requested")
        self.assertNotIn('oldVar2', all_variables, "oldVar2 should not be get as it's younger than requested")
    
    def test_returnAllVariablesIfNoOlderThanProvided(self):
        """
        Check that we get all variables if 'olderThan' param is not provided
        """
             
        version = Version.objects.get(pk=2)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='oldVar', value='oldValue1', application=version.application, version=version, environment=env, 
                 creationDate=datetime.datetime.now() - datetime.timedelta(2), 
                 timeToLive=5).save()
        Variable(name='oldVar2', value='oldValue2', application=version.application, version=version, environment=env, 
                 creationDate=datetime.datetime.now() - datetime.timedelta(1), 
                 timeToLive=5).save()
    
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1})
             
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
             
        all_variables = self._convertToDict(response.data)
             
        self.assertIn('oldVar', all_variables, "oldVar should be get as it's older than requested")
        self.assertIn('oldVar2', all_variables, "oldVar2 should not be get as it's younger than requested")
           
   
    def test_returnAllVariablesIfOlderThan0Days(self):
        """
        Check that we get all variables if 'olderThan' param is 0
        """
            
        version = Version.objects.get(pk=2)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='oldVar', value='oldValue1', application=version.application, version=version, environment=env, 
                 creationDate=timezone.now(), 
                 timeToLive=5).save()
        Variable(name='oldVar2', value='oldValue2', application=version.application, version=version, environment=env, 
                 creationDate=datetime.datetime.now() - datetime.timedelta(1), 
                 timeToLive=5).save()
   
        time.sleep(0.5) # wait so that comparing variable time is not a problem
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1, 'olderThan': 0})
            
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
            
        all_variables = self._convertToDict(response.data)
            
        self.assertIn('oldVar', all_variables, "oldVar should be get as it's older than requested")
        self.assertIn('oldVar2', all_variables, "oldVar2 should not be get as it's younger than requested")
           
   
    def test_returnAllVariablesIfOlderThanNegativeDays(self):
        """
        Check that we get all variables if 'olderThan' param is negative
        """
            
        version = Version.objects.get(pk=2)
        env = TestEnvironment.objects.get(pk=3)
        Variable(name='oldVar', value='oldValue1', application=version.application, version=version, environment=env, 
                 creationDate=timezone.now(), 
                 timeToLive=5).save()
        Variable(name='oldVar2', value='oldValue2', application=version.application, version=version, environment=env, 
                 creationDate=datetime.datetime.now() - datetime.timedelta(1), 
                 timeToLive=5).save()
   
        time.sleep(0.5) # wait so that comparing variable time is not a problem
        response = self.client.get(reverse('variableApi'), data={'version': 2, 'environment': 3, 'test': 1, 'olderThan': -1})
            
        self.assertEqual(response.status_code, 200, 'status code should be 200: ' + str(response.content))
            
        all_variables = self._convertToDict(response.data)
            
        self.assertIn('oldVar', all_variables, "oldVar should be get as it's older than requested")
        self.assertIn('oldVar2', all_variables, "oldVar2 should not be get as it's younger than requested")
           