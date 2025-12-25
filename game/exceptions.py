class GameError(Exception):
    """Базовое исключение"""


class NoItemInItemInventory(GameError):
    """Предмет отсутствует в инвентаре"""


class ZeroDelta(GameError):
    """Нельзя изменять кол-во на 0"""


class InsufficientQuantity(GameError):
    """Недостаточное кол-во предметов в инвентаре"""


class WrongDeltaForInstance(GameError):
    """Для изменения колва у ItemInstance delta должна быть 1 | -1"""


class OperationError(GameError):
    """Ошибка при выполнении операции"""


class AddDropListInInventoryError(GameError):
    """Не удалось добавить дроп-лист в инвентарь игрока"""


class TheBigDelta(Exception):
    pass



class NoWorldID(Exception):
    pass

class WorldIDItemFalseDelta(Exception):
    pass

class NoItemInInventory(Exception):
    pass

class NoItemForWorldId(Exception):
    pass