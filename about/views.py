from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext

# Returns Home Page from url /about
def about(request):
    args = {}
    return render_to_response('about/about.html', args, context_instance=RequestContext(request)) 
