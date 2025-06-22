from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def temp_view(request):
    return render(request, 'bar/temp.html', {'message': 'Sistema en mantenimiento'})