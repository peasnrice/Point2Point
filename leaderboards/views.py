from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext

# Returns Home Page from url /
def leaderboards(request):
    return render_to_response('leaderboards/leaderboards.html', locals(), context_instance=RequestContext(request)) 
