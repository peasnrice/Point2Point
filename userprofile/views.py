from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from forms import UserProfileForm
from django.contrib.auth.decorators import login_required

@login_required
def user_profile(request):

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/users/profile')
    else:
        user = request.user
        profile = user.profile
        form = UserProfileForm(instance=profile)

    return render_to_response('userprofile/profile.html', locals(), context_instance=RequestContext(request))