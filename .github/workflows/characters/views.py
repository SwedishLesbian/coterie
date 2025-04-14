# characters/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CharacterSheet
from .forms import CharacterSheetForm

def home(request):
    """Front page view."""
    return render(request, 'home.html')

@login_required
def dashboard(request):
    """Dashboard view listing the logged-in user's character sheets."""
    sheets = CharacterSheet.objects.filter(owner=request.user)
    return render(request, 'dashboard.html', {'sheets': sheets})

@login_required
def character_detail(request, pk):
    """View to display an individual character sheet."""
    sheet = get_object_or_404(CharacterSheet, pk=pk, owner=request.user)
    return render(request, 'character_detail.html', {'sheet': sheet})

@login_required
def character_create(request):
    """View to create a new character sheet."""
    if request.method == "POST":
        form = CharacterSheetForm(request.POST)
        if form.is_valid():
            sheet = form.save(commit=False)
            sheet.owner = request.user
            sheet.save()
            return redirect('dashboard')
    else:
        form = CharacterSheetForm()
    return render(request, 'character_form.html', {'form': form})

@login_required
def character_update(request, pk):
    """View to edit an existing character sheet."""
    sheet = get_object_or_404(CharacterSheet, pk=pk, owner=request.user)
    if request.method == "POST":
        form = CharacterSheetForm(request.POST, instance=sheet)
        if form.is_valid():
            form.save()
            return redirect('character_detail', pk=sheet.pk)
    else:
        form = CharacterSheetForm(instance=sheet)
    return render(request, 'character_form.html', {'form': form})
