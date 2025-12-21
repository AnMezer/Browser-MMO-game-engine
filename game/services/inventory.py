from game.models import ItemStack, ItemInstance, Item
from users.models import CustomUser
from .items import create_item_instance
from game.exceptions import InsufficientQuantity, NoItemInInventory, ZeroDelta, WrongDeltaForInstance, OperationError
from typing import overload


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


def get_item_from_inventory(
        user: CustomUser,
        item: Item,
        world_id: str | None = None) -> ItemStack | ItemInstance:
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
            item_in_bag = ItemInstance.objects.get(
                    owner=user, world_id=world_id)
        return item_in_bag
    except (ItemStack.DoesNotExist, ItemInstance.DoesNotExist) as e:
        raise NoItemInInventory(
            f'Предмет {item.name} (world_id={world_id}) '
            f'отсутствует в инвентаре') from e


def change_stack_quantity(
        user: CustomUser,
        item: Item, delta: int):
    """Изменяет кол-во обычных предметов в инвентаре.

    Args:
        user: Юзер с чьим инвентарем работаем.
        item: Предмет, кол-во которого нужно изменить.
        delta: На сколько нужно изменить кол-во.

    Raises:
        InsufficientQuantity: Если предметов недостатояно для удаления.
        ZeroDelta: Если была попатка изменить кол-во на 0
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


def add_or_remove_unique_item(
        user: CustomUser,
        item: Item,
        delta: int,
        world_id: str | None = None):
    """Удаляет/добавляет предмет в ItemInstance

    Args:
        user: Юзер с чьим инвентарем работаем.
        item: Предмет, который нужно удалить/добавить.
        delta: Кол-во. Только 1 или -1 (уникальные предметы хранятся по 1)
        world_id: Уникальный id предмета.
                  По умолчанию None.
    """
    if delta == 1:
        create_item_instance(item, user)
        return
    elif delta == -1 and world_id is not None:
        item_in_inventory = get_item_from_inventory(user, item, world_id)
        item_in_inventory.delete()
        return
    else:
        raise WrongDeltaForInstance(
            'Для изменения кол-ва у ItemInstance delta должна быть 1 | -1')


def change_item_quantity(
        user: CustomUser,
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
            raise OperationError(f'Ошибка при выполнении операции.') from e
    else:
        try:
            add_or_remove_unique_item(user, item, delta, world_id)
        except (WrongDeltaForInstance, TypeError) as e:
            raise OperationError(f'Ошибка при выполнении операции.') from e
