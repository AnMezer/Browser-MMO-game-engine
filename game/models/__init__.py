
# Теперь модели импортируются, как раньше:
# from game.models import Model
from .economy import Currency, Wallet
from .items import Item, ItemInstance, ItemStack, item_logo_path
from .locations import GlobalLocation, SubLocation
from .monsters import Monster, MonsterDrop, monster_avatar_path
from .shops import ActivityLink, Shop, ShopItem
