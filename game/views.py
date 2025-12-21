from typing import cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from game.services import monsters, inventory

from game.models import (
    ActivityLink,
    GlobalLocation,
    Item,
    ItemInstance,
    ItemStack,
    Monster,
    Shop,
    ShopItem,
    SubLocation,
)
from users.models import CustomUser

from . import utils
from .constants import FIGHT_COOLDOWN_SECONDS


@login_required
def hunting_zones(request):
    """Список глобальных локаций"""
    global_locations = GlobalLocation.objects.all().order_by('min_level')
    context = {
        'global_locations': global_locations,
    }
    return render(request, 'game/hunting_zones.html', context)


@login_required
def city(request, global_location_slug='gorod'):
    """Обзор городских локаций"""
    global_location = get_object_or_404(
        GlobalLocation,
        slug=global_location_slug
    )
    sublocation_list = SubLocation.objects.filter(global_location=global_location).order_by('name')
    context = {
        'global_location': global_location,
        'sublocations': sublocation_list
    }
    return render(request, 'game/city.html', context)


@login_required
def city_sublocation(request, sublocation_slug):
    user = cast(CustomUser, request.user)

    sublocation = get_object_or_404(
        SubLocation,
        slug=sublocation_slug
    )

    global_location = sublocation.global_location
    # ---- Запрашиваем ссылки на активности и получаем их список ----
    activity_links = sublocation.activity_links.all()
    activities = [link.activity for link in activity_links if link.activity]
    # ---------------------------------------------------------------
    if user.current_sublocation != sublocation:
        return redirect('game:travel_status')

    context = {
        'global_location': global_location,
        'sublocation': sublocation,
        'activities': activities,
    }
    return render(request, 'game/city_sublocation.html', context)


@login_required
def sublocations_list(request, global_location_slug):
    """Список саблокаций"""
    global_location = get_object_or_404(
        GlobalLocation,
        slug=global_location_slug
    )
    sublocation_list = SubLocation.objects.filter(global_location=global_location).order_by('min_level')
    context = {
        'global_location': global_location,
        'sublocations': sublocation_list
    }
    return render(request, 'game/sublocations_list.html', context)


@login_required
def sublocation(request, global_location_slug, sublocation_slug):
    """Страница локации"""
    user = cast(CustomUser, request.user)
    global_location = get_object_or_404(
        GlobalLocation,
        slug=global_location_slug
    )
    sublocation = get_object_or_404(
        SubLocation,
        slug=sublocation_slug,
        global_location=global_location
    )
    monsters = sublocation.monsters.all()

    if user.current_sublocation != sublocation:
        return redirect('game:travel_status')

    context = {
        'global_location': global_location,
        'sublocation': sublocation,
        'monsters': monsters,
    }
    return render(request, 'game/sublocation.html', context)


@login_required
def start_travel(request, global_location_slug, sublocation_slug):
    """Старт пешего перемещения между локациями"""
    target_global_location = get_object_or_404(
        GlobalLocation,
        slug=global_location_slug
    )
    target_sublocation = get_object_or_404(
        SubLocation,
        slug=sublocation_slug,
        global_location=target_global_location
    )
    user = cast(CustomUser, request.user)
    travel_time = utils.calculate_travel_time(request.user, target_global_location,   target_sublocation)

    user.travel_destination = target_sublocation
    user.travel_started_at = timezone.now()
    user.travel_time = travel_time
    user.save()

    return redirect('game:travel_status')


@login_required
def travel_status(request):
    """Статус ожидания перемещения"""
    user = cast(CustomUser, request.user)
    if not user.travel_destination or not user.travel_started_at:
        return redirect('game:hunting_zones')
    time_from_start = timezone.now() - user.travel_started_at
    time_remained = user.travel_time - time_from_start.total_seconds()

    if time_remained <= 0:
        user.set_location(sublocation=user.travel_destination)
        user.travel_destination = None
        user.travel_time = 0
        user.travel_started_at = None
        user.save()
        if user.current_sublocation.slug != 'gorodskaya-ploshad':
            return redirect(
                'game:sublocation',
                global_location_slug=user.current_sublocation.global_location.slug,
                sublocation_slug=user.current_sublocation.slug
            )
        else:
            return redirect(
                'game:city'
            )

    context = {
        'destination': user.travel_destination,
        'time_remained': int(time_remained)
    }
    return render(request, 'game/travel_status.html', context)


@login_required
def teleport(request, global_location_slug, sublocation_slug):
    print('TELEPORT')
    """Телепорт в другую локацию"""
    target_global_location = get_object_or_404(
        GlobalLocation,
        slug=global_location_slug
    )
    target_sublocation = get_object_or_404(
        SubLocation,
        slug=sublocation_slug,
        global_location=target_global_location
    )
    user = cast(CustomUser, request.user)

    travel_time = utils.calculate_travel_time(user, target_global_location, target_sublocation)

    teleports_stack = ItemStack.objects.filter(
        owner=user,
        item__slug='svitok-teleporta'
    ).first()

    if teleports_stack and teleports_stack.quantity >= 1:
        travel_time = 0
        if teleports_stack.quantity == 1:
            teleports_stack.delete()
        else:
            teleports_stack.quantity -= 1
            teleports_stack.save(update_fields=['quantity'])

    else:
        travel_time *= 3

    user.travel_destination = target_sublocation
    user.travel_started_at = timezone.now()
    user.travel_time = travel_time
    user.save(update_fields=['travel_destination', 'travel_started_at', 'travel_time'])

    return redirect('game:travel_status')


@login_required
def attack_monster(request,  global_location_slug, sublocation_slug, monster_slug):
    monster = get_object_or_404(
        Monster,
        slug=monster_slug
    )
    user = cast(CustomUser, request.user)
    # ---- Проверка, вышло ли время до следующего боя ----
    if user.last_fight_at:
        elapsed = (timezone.now() - user.last_fight_at).total_seconds()
        if elapsed < FIGHT_COOLDOWN_SECONDS:
            return redirect(
                'game:sublocation',
                global_location_slug=user.current_sublocation.global_location.slug,
                sublocation_slug=user.current_sublocation.slug
            )
    # ----------------------------------------------------

    if not utils.perform_attack(user, monster):
        print('Что-то пошло не так')
    drop_list = monsters.get_amount_of_loot(monster)
    if not drop_list:
        print('Вам ничего не выпало')
    else:
        utils.change_multiple_items_quantity(user, drop_list)
    user.add_experience(monster.xp_reward)
    user.last_fight_at = timezone.now()
    user.save(update_fields=['last_fight_at'])
    return redirect(
            'game:sublocation',
            global_location_slug=user.current_sublocation.global_location.slug,
            sublocation_slug=user.current_sublocation.slug
        )


@login_required
def trader_test(request):
    """
    Страница торговца.
    """
    player_inventory = []

    user = cast(CustomUser, request.user)
    inventiry_slots = user.item_slots
    stacks = ItemStack.objects.filter(owner=user).select_related('item').order_by('item__name')
    instances = ItemInstance.objects.filter(owner=user).select_related('item').order_by('item__name')
    for stack in stacks:
        item = stack.item
        player_inventory.append(
            {
                'type': 'stack',
                'item_id': item.id,
                'name': item.name,
                'description': item.description,
                'logo_url': item.logo.url if item.logo else None,
                'quantity': stack.quantity
            }
        )
    for instance in instances:
        item = instance.item
        player_inventory.append(
            {
                'type': 'instance',
                'item_id': item.id,
                'name': item.name,
                'description': item.description,
                'logo_url': item.logo.url if item.logo else None,
                'stats': utils.get_item_stats_fot_tooltip(instance),
                'world_id': instance.world_id
            }

        )
    # Добавим пустые слоты до максимальных возможных
    while len(player_inventory) < inventiry_slots:
        player_inventory.append({'type': 'empty', 'slot_number': len(player_inventory) + 1})

    trader_inventory = []
    shop = Shop.objects.get(name='Походник')
    stacks = ShopItem.objects.filter(
        shop=shop,
        is_active=True,
    ).select_related('item')
    print(stacks)
    for stack in stacks:
        item = stack.item
        if item.is_stacked:
            trader_inventory.append(
                {   'is_stacked': item.is_stacked,
                    'type': item.item_type,
                    'item_id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'logo_url': item.logo.url if item.logo else None,
                    'base_price': item.cost,
                    'max_quantity': 1000
                }
            )
        if not item.is_stacked:
            trader_inventory.append(
                {   
                    'is_stacked': item.is_stacked,
                    'type': item.item_type,
                    'item_id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'logo_url': item.logo.url if item.logo else None,
                    'stats': utils.get_item_stats_fot_tooltip(stack),
                    'base_price': item.cost,
                    'max_quantity': 1
                }
            )
    print(trader_inventory)

    context = {
        'player_inventory': player_inventory,
        'trader_items': trader_inventory,
    }
    return render(request, 'game/trader.html', context)


@login_required
def trade_view(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        source = request.POST.get('source')
        quantity = int(request.POST.get('quantity', 1))
        price_per_unit = int(request.POST.get('price_per_unit', 0))
        world_id = request.POST.get('world_id') or None
        print(world_id)

        try:
            if source == 'shop':
                success, error = utils.buy_item(request.user, item_id, quantity, price_per_unit, world_id)
                if success:
                    messages.success(request, f"Куплено: {quantity} шт.")
                else:
                    messages.error(request, f"Ошибка покупки: {error}")
            elif source == 'player':
                success, error = utils.sell_item(request.user, item_id, quantity, price_per_unit, world_id)
                if success:
                    messages.success(request, f"Продано: {quantity} шт.")
                else:
                    messages.error(request, f"Ошибка продажи: {error}")
            else:
                messages.error(request, "Неверный источник сделки")
        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")
    return redirect('game:trader_test')