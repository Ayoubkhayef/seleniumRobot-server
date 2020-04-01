'''
Created on 11 mai 2017

@author: bhecquet
'''
from snapshotServer.models import Version, Application, TestCaseInSession,\
    TestStep, StepResult, Snapshot, TestSession, TestEnvironment, TestCase
import pickle
import datetime
import pytz
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import django.test


class TestTestSession(django.test.TestCase):

    fixtures = ['snapshotServer.yaml']

    def test_delete_old_sessions(self):
        """
        Delete sessions that have no reference snapshots, with a ttl > 0, which are older than the ttl
        """

        s1 = TestSession(sessionId="1234", 
                         date=timezone.now() - datetime.timedelta(days=4), 
                         browser="firefox", 
                         environment=TestEnvironment.objects.get(pk=1), 
                         version=Version.objects.get(pk=1), 
                         ttl=datetime.timedelta(days=0))
        s1.save()
        
        s1.ttl = datetime.timedelta(days=3)
        s1.save()
        
        # s1 should have been deleted
        self.assertRaises(TestSession.DoesNotExist, TestSession.objects.get, pk=s1.id)

    def test_delete_not_so_old_sessions(self):
        """
        Do not delete sessions that have no reference snapshots, with a ttl > 0, which are not older than the ttl
        """

        s1 = TestSession(sessionId="1234", 
                         date=timezone.now() - datetime.timedelta(days=4), 
                         browser="firefox", 
                         environment=TestEnvironment.objects.get(pk=1), 
                         version=Version.objects.get(pk=1), 
                         ttl=datetime.timedelta(days=0))
        s1.save()
        
        s1.ttl = datetime.timedelta(days=5)
        s1.save()
        
        TestSession.objects.get(pk=s1.id)
        

    def test_delete_old_sessions_with_reference(self):
        """
        Do not delete sessions that have reference snapshots, with a ttl > 0, which are older than the ttl
        """
        s1 = TestSession(sessionId="1234", 
                         date=timezone.now() - datetime.timedelta(days=4), 
                         browser="firefox", 
                         environment=TestEnvironment.objects.get(pk=1), 
                         version=Version.objects.get(pk=1), 
                         ttl=datetime.timedelta(days=0))
        s1.save()
        step = TestStep(name="step1")
        step.save()
        tc1 = TestCase(name="case1", application=Application.objects.get(pk=1))
        tc1.save()
        tcs1 = TestCaseInSession(testCase=tc1, session=s1)
        tcs1.save()
        tcs1.testSteps.set([step])
        tcs1.save()
        tsr1 = StepResult(step=step, testCase=tcs1, result=True)
        tsr1.save()
        
        # add a snapshot without reference => its a reference itself
        sn1 = Snapshot(stepResult=tsr1, image=None, refSnapshot=None, pixelsDiff=None)
        sn1.save()
        
        s1.ttl = datetime.timedelta(days=3)
        s1.save()
        
        # session should not be deleted
        TestSession.objects.get(pk=s1.id)

    def test_delete_old_sessions_with_no_reference(self):
        """
        Delete sessions that have snapshots (but no reference, with a ttl > 0, which are older than the ttl
        """
        s1 = TestSession(sessionId="1234", 
                         date=timezone.now() - datetime.timedelta(days=4), 
                         browser="firefox", 
                         environment=TestEnvironment.objects.get(pk=1), 
                         version=Version.objects.get(pk=1), 
                         ttl=datetime.timedelta(days=0))
        s1.save()
        step = TestStep(name="step1")
        step.save()
        tc1 = TestCase(name="case1", application=Application.objects.get(pk=1))
        tc1.save()
        tcs1 = TestCaseInSession(testCase=tc1, session=s1)
        tcs1.save()
        tcs1.testSteps.set([step])
        tcs1.save()
        tsr1 = StepResult(step=step, testCase=tcs1, result=True)
        tsr1.save()
        
        # add a snapshot without reference => its a reference itself
        sn0 = Snapshot(stepResult=StepResult.objects.get(pk=1), image=None, refSnapshot=None, pixelsDiff=None)
        sn0.save()
        sn1 = Snapshot(stepResult=tsr1, image=None, refSnapshot=sn0, pixelsDiff=None)
        sn1.save()
        
        s1.ttl = datetime.timedelta(days=3)
        s1.save()
        
        # s1 should have been deleted
        self.assertRaises(TestSession.DoesNotExist, TestSession.objects.get, pk=s1.id)
