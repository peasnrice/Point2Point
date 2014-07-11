from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext
from quests.models import QuestType

# Returns Home Page from url /contact
def contact(request):
    quest_types = QuestType.objects.filter(front_page=True).order_by('priority')
    args = {}
    args['quest_types'] = quest_types
    return render_to_response('contact/contact.html', args, context_instance=RequestContext(request)) 
