import logging
from typing import Optional

from game.exceptions import NoItemInInventory, ZeroDelta
from game.models import Item, ItemInstance, ItemStack
from users.models import CustomUser

logger = logging.getLogger(__name__)


def create_item_instance(item: Item, owner: Optional[CustomUser] = None):
    """Создает новый уникальный предмет.

    Добавляет запись в ItemInstance.
    Args:
        item: Объект модели Item (шаблон).
        owner: Владелец предмета.
    Returns:
        instance: Созданный объект ItemInstance
    """
    instance = ItemInstance.objects.create(item=item, owner=owner)
    return instance
