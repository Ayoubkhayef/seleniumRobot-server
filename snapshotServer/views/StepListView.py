'''
Created on 26 juil. 2017

@author: worm
'''
from django.views.generic.list import ListView

from snapshotServer.models import TestCaseInSession


class StepListView(ListView):
    """
    @param testCaseInSessionId
    """
    
    template_name = "snapshotServer/stepList.html"
    
    def get_queryset(self):
        try:
            testSteps = TestCaseInSession.objects.get(id=self.kwargs['testCaseInSessionId']).testSteps.all()
            return dict([(s, s.isOkWithSnapshots(self.kwargs['testCaseInSessionId'])) for s in testSteps])
        except:
            return []
        
    def get_context_data(self, **kwargs):
        context = super(StepListView, self).get_context_data(**kwargs)
        context['testCaseId'] = self.kwargs['testCaseInSessionId']
        return context