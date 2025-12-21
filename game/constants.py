FIGHT_COOLDOWN_SECONDS = 0

SECONDS_PER_UNIT_DISTANCE = 5

ITEM_TYPE_CHOICES = [
    ('JUNK', 'Хлам'),
    ('RESOURCE', 'Ресурс'),
    ('ORE', 'Руда'),
    ('ARMOR', 'Броня'),
    ('WEAPON', 'Оружие'),
    ('AMULET', 'Амулет'),
    ('POTION', 'Зелье'),
    ('CONSUMABLE', 'Используемый предмет'),
    ('QUEST', 'Квестовый'),
]

SLOT_CHOICES = [
        ('HEAD', 'Голова'),
        ('CHEST', 'Тело'),
        ('HANDS', 'Руки'),
        ('LEGS', 'Ноги'),
        ('FEET', 'Обувь'),
        ('MAIN_HAND', 'Основная рука'),
        ('OFF_HAND', 'Вторая рука'),
        ('NECK', 'Шея (амулет)'),
        ('FINGER', 'Палец (кольцо)'),
        ('WAIST', 'Пояс (амулет)'),
        ('EAR', 'Ухо (серьга)')
    ]

BASE_STATS = {
    'strength': 5, # Физическая атака
    'defense': 5, # Физическая защита
    'dexterity': 5, # Шанс критического удара и шанс уворота
    'stamina': 5, # Максимальное здоровье (HP)
    'intelligence': 5, # Магическая атака
    'spirit': 5, # Максимальная мана (MP)
    'willpower': 5, # Магическая защита
    'item_slots': 24,
    'luck': 5,
}
STATS_PER_LEVEL = {
    'strength': 1, 
    'defense': 1,
    'dexterity': 1,
    'stamina': 1,
    'intelligence': 1,
    'spirit': 1,
    'willpower': 1,
    'item_slots': 0,
    'luck': 0,
}