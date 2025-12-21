from game.models import Item, ItemInstance, ItemStack
from users.models import CustomUser
import logging
from game.exceptions import NoItemInInventory, ZeroDelta

logger = logging.getLogger(__name__)


def create_item_instance(item: Item, owner: CustomUser | None):
    """Создает новый уникальный предмет.

    Добавляет запись в ItemInstance.
    Args:
        item (Item): Объект модели Item (шаблон).

    Returns:
        instance: Созданный объект ItemInstance
    """
    instance = ItemInstance.objects.create(item=item, owner=owner)
    return instance
