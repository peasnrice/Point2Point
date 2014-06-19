from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext

# Returns Home Page from url /
def how_to_play(request):
    return render_to_response('howtoplay/howtoplay.html', locals(), context_instance=RequestContext(request)) 

