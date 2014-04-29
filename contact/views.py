from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext

# Returns Home Page from url /contact
def contact(request):
    return render_to_response('contact/contact.html', locals(), context_instance=RequestContext(request)) 
