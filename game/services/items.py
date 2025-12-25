from game.models import Item, ItemInstance, ItemStack
from users.models import CustomUser
import logging
from game.exceptions import NoItemInInventory, ZeroDelta
from typing import Optional

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
