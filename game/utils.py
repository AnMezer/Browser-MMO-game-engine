from decimal import Decimal
from random import randint
from typing import cast

from users.models import CustomUser

from . import exceptions
from .constants import BASE_STATS, SECONDS_PER_UNIT_DISTANCE
from .models import (
    Currency,
    GlobalLocation,
    Item,
    ItemInstance,
    ItemStack,
    Monster,
    MonsterDrop,
    SubLocation,
    Wallet,
)


def change_item_quantity(user: CustomUser, item: Item, delta: int, world_id: str | None = None) -> bool:
    """Функция для изменения кол-ва предметов в инвентаре"""    
    if delta == 0:
        raise exceptions.ZeroDelta('Не нужно менять кол-во на 0 шт')

    if item.is_stacked:
        # Стакаемые предметы
        if delta < 0:
            # Продажа: проверяем, что хватает количества
            current = ItemStack.objects.filter(owner=user, item=item).first()
            if not current or current.quantity < abs(delta):
                raise exceptions.TheBigDelta('Недостаточно предметов для продажи')
        
        stack, created = ItemStack.objects.get_or_create(
            owner=user,
            item=item,
            defaults={'quantity': 0}
        )
        stack.quantity += delta
        if stack.quantity <= 0:
            stack.delete()
        else:
            stack.save(update_fields=['quantity'])

    else:
        # Уникальные предметы
        if delta == 1:
            # Покупка или получение: создаём НОВЫЙ экземпляр
            ItemInstance.objects.create(
                item=item,
                owner=user
                # world_id сгенерируется автоматически
            )
        elif delta == -1:
            # Продажа: удаляем по world_id
            if not world_id:
                raise exceptions.NoWorldID('Для продажи уникального предмета нужен world_id')
            deleted, _ = ItemInstance.objects.filter(
                world_id=world_id,
                owner=user,
                item=item
            ).delete()
            if deleted == 0:
                raise exceptions.NoItemInInventory('Предмет не найден в инвентаре')
        else:
            raise exceptions.WorldIDItemFalseDelta('Уникальный предмет можно изменить только на ±1')

    return True 



def change_multiple_items_quantity(user: CustomUser, item_list: list) -> bool:
    item_ids = [tpl[0] for tpl in item_list]
    items = {item.id: item for item in Item.objects.filter(id__in=item_ids)}
    for item_id, quantity, world_id in item_list:
        item = items[item_id]
        change_item_quantity(user, item, quantity, world_id)
    return True


def calculate_travel_time(user: CustomUser, target_global_location: GlobalLocation, target_sublocation: SubLocation) -> int:
    if user.current_global_location == target_global_location:
        travel_time = abs(user.current_sublocation.distance_to_location_start - target_sublocation.distance_to_location_start)
    else:
        travel_time = user.current_sublocation.distance_to_location_start + abs(user.current_global_location.distance_to_the_city - target_global_location.distance_to_the_city) + target_sublocation.distance_to_location_start
    return travel_time * SECONDS_PER_UNIT_DISTANCE

def perform_attack(user: CustomUser, monster:Monster) -> bool:
        # ---- Пока так для теста ----
        print(f'{user.nickname} напал на {monster}')
        winner = user
        if winner == user:
            print(f'В бою победил {winner}')
        return True

def get_item_stats_fot_tooltip(instance: ItemInstance):
    """Готовит словарь со статами предмета для отображения в тултипе"""
    stats = {}
    for stat_name, value in BASE_STATS.items():
        stats[stat_name] = {
            'base': getattr(instance.item, stat_name, 0),
            'bonus': getattr(instance, f'{stat_name}_bonus', 0)
        }
    return stats

def sell_item(user: CustomUser, item_id: int, delta: int, price_per_unit: int, world_id: str | None = None):
    delta = delta * -1
    try:
        item = Item.objects.get(id=item_id)
    except:
        raise exceptions.NoItemInInventory('Предмет не существует')
    
    if not world_id:
        if not ItemStack.objects.filter(
            item=item,
            owner = user
        ).exists():
            raise exceptions.NoItemInInventory('Предмета нет в инвентаре')
    else:
        if not ItemInstance.objects.filter(
            item=item,
            owner=user,
            world_id=world_id
        ).exists():
            raise exceptions.NoItemInInventory('Предмета нет в инвентаре')
    change_item_quantity(user, item, delta, world_id)

    gold_currency = Currency.objects.get(code='GOLD')
    gold = abs(item.cost * delta)
    wallet, created = Wallet.objects.get_or_create(user=user, currency=gold_currency, defaults={
            'amount': 0
        }
    )
    wallet.amount += gold
    wallet.save(update_fields=['amount',])
    return True, None

def buy_item(user: CustomUser, item_id: int, delta: int, price_per_unit: int, world_id: str | None = None):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return False, 'Предмет не существует'
    try:
        gold_currency = Currency.objects.get(code='GOLD')
        wallet = Wallet.objects.get(user=user, currency=gold_currency)
    except Wallet.DoesNotExist:
        return False, "Кошелёк не найден"
    
    total_cost = price_per_unit * delta

    if wallet.amount < total_cost:
        return False, "Недостаточно золота"
    
    try:
        change_item_quantity(user, item, delta, world_id)
        wallet.amount -= total_cost
        wallet.save(update_fields=['amount'])
        return True, None
    except Exception as e:
        return False, str(e)

