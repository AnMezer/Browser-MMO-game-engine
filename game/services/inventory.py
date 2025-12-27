from typing import overload, cast
from uuid import UUID
from pprint import pprint

from game.exceptions import (
    AddDropListInInventoryError,
    InsufficientQuantity,
    NoItemInInventory,
    OperationError,
    WrongDeltaForInstance,
    ZeroDelta,
)
from game.models import Item, ItemInstance, ItemStack, ShopItem, Shop
from game.models.shops import Shop
from users.models import CustomUser
from game.utils import get_item_stats_fot_tooltip  # нужно перенести

from .items import create_item_instance


@overload
def get_item_from_inventory(
        user: CustomUser,
        item: Item,
        world_id: None = None) -> ItemStack:
    ...


@overload
def get_item_from_inventory(
        user: CustomUser,
        item: Item,
        world_id: str) -> ItemInstance:
    ...


@overload
def get_item_from_inventory(
        user: CustomUser,
        item: Item,
        world_id: UUID) -> ItemInstance:
    ...


def get_item_from_inventory(
        user: CustomUser,
        item: Item,
        world_id: str | UUID | None = None) -> ItemStack | ItemInstance:
    """Возвращает объект предмета из инвентаря.

    Args:
        user: Юзер, чей инвентарь проверяется.
        item: Какой предмет ищем.
        world_id: world_id, для уникальных предметов.

    Raises:
        NoItemInInventory: Если предмет отсутствует в инвентаре.

    Returns:
        ItemStack | ItemInstance: Объект предмета, если найден.
    """
    item_in_bag: ItemStack | ItemInstance
    try:
        if world_id is None:
            item_in_bag = ItemStack.objects.get(owner=user, item=item)
        else:
            item_in_bag = ItemInstance.objects.get(owner=user,
                                                   world_id=world_id)
        return item_in_bag
    except (ItemStack.DoesNotExist, ItemInstance.DoesNotExist) as e:
        raise NoItemInInventory(
            f'Предмет {item.name} (world_id={world_id}) '
            f'отсутствует в инвентаре') from e


def change_stack_quantity(user: CustomUser,
                          item: Item,
                          delta: int):
    """Изменяет кол-во обычных предметов в инвентаре.

    Args:
        user: Юзер с чьим инвентарем работаем.
        item: Предмет, кол-во которого нужно изменить.
        delta: На сколько нужно изменить кол-во.

    Raises:
        InsufficientQuantity: Если предметов недостатояно для удаления.
        ZeroDelta: Если была попытка изменить кол-во на 0
    """
    if delta < 0:
        item_in_inventory = get_item_from_inventory(user, item)
        if item_in_inventory.quantity >= abs(delta):
            item_in_inventory.quantity += delta
            if item_in_inventory.quantity == 0:
                item_in_inventory.delete()
            else:
                item_in_inventory.save(update_fields=['quantity'])
            return
        else:
            raise InsufficientQuantity(
                f'В инвентаре {user.nickname}: '
                f'{item.name} - {item_in_inventory.quantity}. '
                f'Попытка удалить {abs(delta)}')
    elif delta > 0:
        item_in_inventory, created = ItemStack.objects.get_or_create(
            owner=user, item=item, defaults={'quantity': 0})
        item_in_inventory.quantity += delta
        item_in_inventory.save(update_fields=['quantity'])
    else:
        raise ZeroDelta('Кол-во нельзя изменять на 0')


def add_or_remove_unique_item(user: CustomUser,
                              item: Item,
                              delta: int,
                              world_id: str | UUID):
    """Удаляет/добавляет предмет в ItemInstance

    Args:
        user: Юзер с чьим инвентарем работаем.
        item: Предмет, который нужно удалить/добавить.
        delta: Кол-во. Только 1 или -1 (уникальные предметы хранятся по 1)
        world_id: Уникальный id предмета.
                  По умолчанию None.
    """
    if delta == 1:
        item_instance = ItemInstance.objects.get(world_id=world_id)
        item_instance.owner = user
        item_instance.save(update_fields=['owner'])
        return
    elif delta == -1 and world_id is not None:
        item_in_inventory = get_item_from_inventory(user, item, world_id)
        item_in_inventory.delete()
        return
    else:
        raise WrongDeltaForInstance(
            'Для изменения кол-ва у ItemInstance delta должна быть 1 | -1')


def change_item_quantity(user: CustomUser,
                         item: Item,
                         delta: int,
                         world_id: str | None = None):
    """Универсальная функция для изменения кол-ва предметов в инвентаре.

    Args:
        user:  Юзер с чьим инвентарем работаем.
        item: Предмет, кол-во которого нужно изменить.
        delta: Кол-во на которое нужно изменить.
        world_id: Уникальный id предмета,
                  Только для ItemInstance.
                  По умолчанию None.

    Raises:
        OperationError: Ошибка выполнения операции.
    """
    if world_id is None:
        try:
            change_stack_quantity(user, item, delta)
        except (InsufficientQuantity, ZeroDelta) as e:
            raise OperationError('Ошибка при выполнении операции.') from e
    else:
        try:
            add_or_remove_unique_item(user, item, delta, world_id)
        except (WrongDeltaForInstance, TypeError) as e:
            raise OperationError('Ошибка при выполнении операции.') from e


def add_drop_list_in_inventory(user: CustomUser, drop_list: list[tuple]):
    """Добавляет списко дропа указанному игроку.

    Args:
        user: Игрок, которому добавляем предметы.
        drop_list: Список кортежей:[(item_id, amount, world_id | None), ...]

    Raises:
        AddDropListInInventoryError: В случае ошибки при добавлении.
    """
    try:
        for drop in drop_list:
            item_id, delta, world_id = drop
            item = Item.objects.get(id=item_id)
            change_item_quantity(user, item, delta, world_id)
    except OperationError as e:
        raise AddDropListInInventoryError(
            f'Ошибка при добавлении {drop} игроку {user}') from e


def get_user_inventory_data(user: CustomUser) -> list[dict]:
    """Возвращает список с предметами в инвентаре.

    Список предназначен для дальнейшей отпрвки в шаблон.
    Args:
        user: Юзер, чей инвентарь нужно получить.

    Returns:
        player_inventory: Список с предметами в инвентаре.
    """
    player_inventory = []
    inventiry_slots = user.item_slots
    stacks = ItemStack.objects.filter(
        owner=user).select_related('item').order_by('item__name')
    instances = ItemInstance.objects.filter(
        owner=user).select_related('item').order_by('item__name')
    for stack in stacks:
        item: Item = stack.item
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
        inst_item: Item = instance.item
        print(type(item))
        player_inventory.append(
            {
                'type': 'instance',
                'item_id': inst_item.id,
                'name': inst_item.name,
                'description': inst_item.description,
                'logo_url': inst_item.logo.url if inst_item.logo else None,
                'stats': get_item_stats_fot_tooltip(instance),
                'world_id': instance.world_id
            }

        )
    # Добавим пустые слоты до максимальных возможных
    while len(player_inventory) < inventiry_slots:
        player_inventory.append({'type': 'empty',
                                 'slot_number': len(player_inventory) + 1})
    return player_inventory


def get_shop_inventory_data(shop_name: str):
    """Возвращает список с инвентарем магазина.

    Список предназначен для дальнейшей отпрвки в шаблон.
    Args:
        shop_name: Название магазина

    Returns:
        trader_inventory: Список с предметами, продающимися в магазине.
    """
    trader_inventory = []
    shop = Shop.objects.get(name=shop_name)
    stacks = ShopItem.objects.filter(shop=shop,
                                     is_active=True).select_related('item')
    for stack in stacks:
        item: Item = stack.item
        if item.is_stacked:
            max_quantity = 1000
        max_quantity = 1
        trader_inventory.append(
            {
                'is_stacked': item.is_stacked,
                'type': item.item_type,
                'item_id': item.id,
                'name': item.name,
                'description': item.description,
                'logo_url': item.logo.url if item.logo else None,
                'stats': get_item_stats_fot_tooltip(stack),
                'base_price': item.cost,
                'max_quantity': max_quantity
            }
        )
    return trader_inventory
