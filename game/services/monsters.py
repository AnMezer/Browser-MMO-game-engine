from game.models import Monster, MonsterDrop, Item, ItemInstance
from typing import cast
from random import randint
from pprint import pprint
from . import items, utils
from django.db.models import QuerySet


def get_amount_of_loot(monster: Monster) -> list[tuple[int, int, str | None]]:
    """Генерирует дроп с монстра.

    Для каждого применяется шанс выпадения.
    Уникальные предметы (is_stacked=False), создаются в ItemInstance,
    и их world_id включается в результат.
    Args:
        monster (Monster): Монстр с которого генерируется дроп.

    Returns:
        Список кортежей:
        [(item_id, amount, world_id), ...]
        Для не уникальных предметов world_id = None.
    """
    drops: QuerySet[MonsterDrop] = monster.drops.filter(
        item_type='ITEM'
        ).select_related('item')
    drop_list: list[tuple[int, int, str | None]] = []
    for drop in drops:
        if drop.item is None:
            continue

        item: Item = drop.item
        if item.is_stacked:
            amount = utils.roll_loot_amout(drop.chance_percent,
                                           drop.min_amount,
                                           drop.max_amount)
            if amount is not None:
                drop_list.append((item.id, amount, None))
        else:
            instance = items.create_item_instance(item)
            drop_list.append(
                (instance.item.id, 1, str(instance.world_id))
            )
    return drop_list
