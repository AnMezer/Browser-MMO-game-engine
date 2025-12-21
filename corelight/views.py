from typing import cast

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from game.models import GlobalLocation, ItemStack, SubLocation, Wallet
from users.forms import CustomUserCreationForm
from users.models import CustomUser


def handler404(request, exception):
    """Страница «Не найдена»."""
    return render(request, 'errors/404.html', status=404)

def handler403(request, exception=None):
    """Доступ запрещён."""
    return render(request, 'errors/403.html', status=403)

def handler500(request):
    """Внутренняя ошибка сервера."""
    return render(request, 'errors/500.html', status=500)

def index(request):
    """Главная страница сайта."""
    return render(request, 'game/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def player_character(request):
    """Страница с данными о своём персонаже"""
    context = {
        'hide_left_sidebar': True,
        'hide_right_sidebar': True,
    }
    user = cast(CustomUser, request.user)
    inventory_slots = user.item_slots
    stacks = ItemStack.objects.filter(owner=user).select_related('item').order_by('item__name')
    instances = []
    inventory_display = []

    for stack in stacks:
        item = stack.item
        inventory_display.append(
            {
                'type': 'stack',
                'item_id': item.id,
                'name': item.name,
                'description': item.description,
                'logo_url': item.logo.url if item.logo else None,
                'quantity': stack.quantity
            }
        )
    while len(inventory_display) <inventory_slots:
        inventory_display.append(
            {
                'type': 'empty',
            }
        )

    context['inventory_display'] = inventory_display
    return render(request, 'game/player_character.html', context)

