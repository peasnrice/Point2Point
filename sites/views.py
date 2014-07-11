from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext
from quests.models import Competition, QuestType

def homepage(request):
	args = {}
    args['quest_types'] = quest_types
    return render_to_response('sites/index.html', args, context_instance=RequestContext(request)) 

def about(request):
	args = {}
    args['quest_types'] = quest_types
    return render_to_response('sites/about.html', args, context_instance=RequestContext(request)) 


