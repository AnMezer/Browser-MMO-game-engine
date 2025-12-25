from decimal import Decimal
from typing import Optional
from random import randint


def roll_loot_amout(base_chance: Decimal,
                    min_amount: int,
                    max_amount: int) -> int | None:
    """Возвращает кол-во предметов, которые удалось добыть.

    1. Вычисляет нужно ли вообще возвращать кол-во.
    2. Если нужно, вычисляет кол-во.

    Args:
        base_chance: Базовый шанс дропа (0.00-100.00).
        min_amount: Минимальное возможное кол-во.
        max_amount: Максимальное возможное кол-ва

    Returns:
        None: Если ничего не выпало.
        amount: Если добыча есть.
    """
    trashold = int(base_chance*100)
    if randint(1, 10000) > trashold:
        return None

    amount = randint(min_amount, max_amount)
    return amount
