from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Flight
from .forms import FlightForm


def index(request):
    return render(request, "index.html")


@login_required(login_url='admin:login')
def flights(request):
    if request.method == "POST":
        form_data = FlightForm(data=request.POST, files=request.FILES)
        if form_data.is_valid():
            flight = form_data.save(commit=False)
            flight.user = request.user
            flight.photo = form_data.cleaned_data['photo']
            flight.save()
            return redirect("flights")
    else:
        form_data = FlightForm()

    queryset = Flight.objects.filter(user=request.user, takeoff_airport="Skopje").all()
    context = {"flights": queryset, "form": form_data}
    return render(request, "flights.html", context)
