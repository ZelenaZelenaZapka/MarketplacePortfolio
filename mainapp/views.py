from django.shortcuts import render, redirect
from .forms import RegisterUserForm

def index(request):
    return render(request, "page_of_store/startpage.html")

def reg_page(request):
    return render(request, "auth_page/auth.html")

def auth_view(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            return redirect('index')
    else:
        form = RegisterUserForm()

    return render(request, 'auth.html', {'form': form})


