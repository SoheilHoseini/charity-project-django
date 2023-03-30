from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import User


def about_us(request):
    allUsers = User.objects.all().values()
    context = {"users": allUsers}
    #return HttpResponse(str(allUsers.get_full_name()))
    return render(request, 'about_us.html', context=context)

