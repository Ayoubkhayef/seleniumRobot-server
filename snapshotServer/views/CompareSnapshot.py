'''
Created on 4 mai 2017

@author: bhecquet
'''

import json
import pickle

from django.http.response import HttpResponse
from django.views.generic import ListView
from django.views.generic.base import TemplateView, View

from snapshotServer.controllers.DiffComputer import DiffComputer
from snapshotServer.models import TestSession, TestCase, Snapshot, ExcludeZone, TestStep


class SessionList(ListView):
    model = TestSession
    template_name = "snapshotServer/compare.html"
    
class TestList(ListView):
    template_name = "snapshotServer/testList.html"
    
    def get_queryset(self):
        testCases = TestCase.objects.filter(testsession=self.args[0])
        return dict([(t, t.isOk(self.args[0])) for t in testCases])
    
    def get_context_data(self, **kwargs):
        context = super(TestList, self).get_context_data(**kwargs)
        context['sessionId'] = self.args[0]
        
        return context
    
        
    
class StepList(ListView):
    template_name = "snapshotServer/stepList.html"
    
    def get_queryset(self):
        try:
            testSteps = TestCase.objects.get(id=self.args[1]).testSteps.all()
            return dict([(s, s.isOk(self.args[0], self.args[1])) for s in testSteps])
        except:
            return []
        
    def get_context_data(self, **kwargs):
        context = super(StepList, self).get_context_data(**kwargs)
        context['testCaseId'] = self.args[1]
        context['sessionId'] = self.args[0]
        return context
    
class PictureView(TemplateView):
    template_name = "snapshotServer/displayPanel.html"

    def get_context_data(self, **kwargs):
        """
        Look for the snapshot of our session
        """
        context = super(PictureView, self).get_context_data(**kwargs)
        
        stepSnapshot = Snapshot.objects.filter(session=self.args[0]).filter(testCase=self.args[1]).filter(step=self.args[2]).last()
        
        
        if stepSnapshot:

            if 'makeRef' in self.request.GET: 
                if self.request.GET['makeRef'] == 'True' and stepSnapshot.refSnapshot is not None:
                    previousSnapshot = stepSnapshot.refSnapshot
                    stepSnapshot.refSnapshot = None
                    stepSnapshot.pixelsDiff = None
                    stepSnapshot.save()
                    
                    # Compute differences for the following snapshots as they will depend on this new ref
                    for snap in stepSnapshot.snapshotsUntilNextRef(previousSnapshot):
                        DiffComputer.addJobs(stepSnapshot, snap)
                    
                elif self.request.GET['makeRef'] == 'False' and stepSnapshot.refSnapshot is None:
                    # search a reference with a lower id, meaning that it has been recorded before our step
                    refSnapshots = Snapshot.objects.filter(testCase=self.args[1]) \
                                                .filter(step=self.args[2]) \
                                                .filter(refSnapshot=None) \
                                                .filter(id__lt=stepSnapshot.id)
                    
                    # do not remove reference flag if our snapshot is the very first one
                    if len(refSnapshots) > 0:
                        stepSnapshot.refSnapshot = refSnapshots.last()
                        stepSnapshot.save()
                        
                        # recompute diff pixels
                        DiffComputer.computeNow(stepSnapshot.refSnapshot, stepSnapshot)
                        
                        # recompute all following snapshot as they will depend on a previous ref
                        for snap in stepSnapshot.snapshotsUntilNextRef(stepSnapshot):
                            DiffComputer.addJobs(stepSnapshot.refSnapshot, snap)
    
            refSnapshot = stepSnapshot.refSnapshot
            
            # extract difference pixel. Recompute in case this step is no more a reference
            diffPixelsBin = stepSnapshot.pixelsDiff
                
            if diffPixelsBin:
                diffPixels = pickle.loads(diffPixelsBin)
            else:
                diffPixels = []
                
        # not snapshot has been recorded for this session
        else:
            refSnapshot = None
            diffPixels = []
         
        context['reference'] = refSnapshot
        context['stepSnapshot'] = stepSnapshot
        context['diff'] = str([[p.x, p.y] for p in diffPixels])
        context['testCaseId'] = self.args[1]
        context['sessionId'] = self.args[0]
        context['testStepId'] = self.args[2]
        return context
    
class ExclusionZoneList(ListView):
    template_name = "snapshotServer/excludeList.html"
    
    def get_queryset(self):
        return ExcludeZone.objects.filter(snapshot=self.args[0])

class RecomputeDiff(View):
    """
    API to compute diff from a REST request
    """
    
    def post(self, request, *args, **kwargs):
        try:
            stepSnapshot = Snapshot.objects.get(pk=args[0])
            
            # compute has sense when a reference exists
            if stepSnapshot.refSnapshot:
                DiffComputer.computeNow(stepSnapshot.refSnapshot, stepSnapshot)
                
                # start computing differences for other snapshots sharing the same reference
                for snap in stepSnapshot.snapshotWithSameRef():
                    DiffComputer.addJobs(stepSnapshot.refSnapshot, snap)
                
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=304)
                
        except:
            return HttpResponse(status=404)
        
        
class TestStatus(View):
    """
    API to get the test session status according to comparison results
    If only session and test are passed, the test is marked as KO when at least one step has a difference
    If moreover, test step is given, returns the comparison result of the step only
    """
        
    def get(self, request, sessionId, testCaseId, testStepId=None):
        try:
            session = TestSession.objects.get(pk=sessionId)
            testCase = TestCase.objects.get(pk=testCaseId)
            
            if testStepId:
                snapshots = Snapshot.objects.filter(session=session, testCase=testCase, step=testStepId)
            else:
                snapshots = Snapshot.objects.filter(session=session, testCase=testCase)
            
            results = {} 
            for snapshot in snapshots:
                if snapshot.refSnapshot is None:
                    results[snapshot.id] = True
                    continue
                if snapshot.pixelsDiff is None:
                    continue
                pixels = pickle.loads(snapshot.pixelsDiff)
                results[snapshot.id] = not bool(pixels)
                
            return HttpResponse(json.dumps(results), content_type='application/json')
            
        except:
            return HttpResponse(status=404, reason="Could not find one or more objects")
        
        