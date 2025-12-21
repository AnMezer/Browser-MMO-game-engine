
# Теперь модели импортируются, как раньше:
# from game.models import Model
from .locations import GlobalLocation, SubLocation
from .economy import Currency, Wallet
from .items import Item, ItemInstance, ItemStack
from .monsters import Monster, MonsterDrop
from .shops import Shop, ShopItem, ActivityLink

from .items import item_logo_path
from .monsters import monster_avatar_path
