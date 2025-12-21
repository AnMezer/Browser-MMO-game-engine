from game.models import Monster, MonsterDrop, Item, ItemInstance
from typing import cast
from random import randint
from pprint import pprint
from .items import create_item_instance
from django.db.models import QuerySet


def get_amount_of_loot(monster: Monster) -> list[tuple[int, int, str | None]]:
    """Генерирует дроп с монстра.

    Для каждого применяется шанс выпадения.
    Уникальные предметы (is_stacked=False), создаются в ItemInstance,
    и их world_id включается в резельтат.
    Args:
        monster (Monster): Монстр с которого генерируется дроп.

    Returns:
        Список кортежей:
        [(item_id, amount, world_id), ...]
        Для не уникаотных предметов world_id = None. 
    """
    drops: QuerySet[MonsterDrop] = monster.drops.filter(
        item_type='ITEM'
        ).select_related('item')
    drop_list: list[tuple[int, int, str | None]] = []
    for drop in drops:
        if drop.item is None:
            continue

        item: Item = drop.item
        chance = drop.chance_percent
        min_amount = drop.min_amount
        max_amount = drop.max_amount
        threshold = int(chance * 100)

        if randint(1, 10000) > threshold:
            continue

        if item.is_stacked:
            amount = randint(min_amount, max_amount)
            drop_list.append((item.id, amount, None))
        else:
            instance = create_item_instance(item)
            drop_list.append(
                (instance.item.id, 1, str(instance.world_id))
            )
    return drop_list
