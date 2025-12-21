import math
import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from game.constants import BASE_STATS, STATS_PER_LEVEL


def get_all_avatar_choices():
    """Сканирует папки avatars/male и avatars/female и возвращает все файлы."""
    choices = []
    for gender in ['male', 'female']:
        avatar_dir = os.path.join(settings.BASE_DIR, 'static', 'avatars', gender)
        if os.path.exists(avatar_dir):
            for file in os.listdir(avatar_dir):
                if file.endswith(('.svg', '.png', '.jpg', '.jpeg')):
                    full_path = f"{gender}/{file}"
                    label = f"{'Мужской' if gender == 'male' else 'Женский'} — {os.path.splitext(file)[0].replace('_', ' ').title()}"
                    choices.append((full_path, label))
    return choices


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя.
    Наследуемся от AbstractUser — получаем все поля (username, email, password и т.д.)
    и можем добавлять свои.
    """

    nickname = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Имя персонажа'
    )
    avatar = models.CharField(
        max_length=100,
        choices=get_all_avatar_choices(),  # ← динамически заполняется при запуске сервера
        default='male/elf_1.svg',
        verbose_name='Аватар'
    )
    experience = models.PositiveBigIntegerField(
        default=0,
        verbose_name='Опыт'
    )
    level = models.PositiveIntegerField(
        default=1,
        verbose_name='Уровень'
    )
    current_global_location = models.ForeignKey(
        'game.GlobalLocation',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Текущая глобальная локация'
    )
    current_sublocation = models.ForeignKey(
        'game.SubLocation',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Текущая саблокация'
    )
    last_fight_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время последнего нападения',
        
    )


    # Базовые характеристики
    strength = models.PositiveSmallIntegerField(
    default=BASE_STATS['strength'],
    verbose_name="Сила"
    )
    defense = models.PositiveSmallIntegerField(
        default=BASE_STATS['defense'],
        verbose_name="Защита"
    )
    dexterity = models.PositiveSmallIntegerField(
        default=BASE_STATS['dexterity'],
        verbose_name="Ловкость"
    )
    stamina = models.PositiveSmallIntegerField(
        default=BASE_STATS['stamina'],
        verbose_name="Выносливость"
    )
    intelligence = models.PositiveSmallIntegerField(
        default=BASE_STATS['intelligence'],
        verbose_name="Интеллект"
    )
    spirit = models.PositiveSmallIntegerField(
        default=BASE_STATS['spirit'],
        verbose_name="Дух"
    )
    willpower = models.PositiveSmallIntegerField(
        default=BASE_STATS['willpower'],
        verbose_name="Воля"
    )
    luck = models.PositiveSmallIntegerField(
        default=BASE_STATS['luck'],
        verbose_name="Удача"
    )
    item_slots = models.PositiveSmallIntegerField(
        default=BASE_STATS['item_slots'],
        verbose_name="Слоты инвентаря"
    )
    current_hp = models.PositiveIntegerField(
        default=0,
        verbose_name="Текущее здоровье"
    )
    # ---- Для перемещения пешком ----

    travel_destination = models.ForeignKey(
        'game.SubLocation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='travel_destination',
        verbose_name='Перемещение в'
    )
    travel_started_at = models.DateTimeField(null=True, blank=True)
    travel_time = models.PositiveIntegerField(default=0)

    # ---------------------------------
    
    banned_until = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Забанен до'
    )
    
    premium_until = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Премиум до'
    )

    class Meta:
        default_related_name = 'users'
        db_table = 'user'  # имя таблицы в БД
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.nickname
    
    @staticmethod
    def xp_required_for_level(level):
        """Возвращает общий опыт, необходимый для ДОСТИЖЕНИЯ уровня `level`."""
        # При изменении формулы изменить def current_level(self)
        if level <= 1:
            return 0
        return 100 * (level - 1) ** 2
    
    def calculate_current_level(self):
        """Вычисляет текущий уровень на основе опыта."""
        # Зависит от формулы вычисления уровня от опыта
        # def xp_required_for_level()
        current_level = math.floor(math.sqrt(self.experience / 100)) + 1
        return current_level
    
    def save(self, *args, **kwargs):
        # Обновляем уровень
        self.level = self.calculate_current_level()
        # Если current_hp не задан — устанавливаем в максимум
        if self.current_hp == 0:
            self.current_hp = self.max_hp
        
        # Если текущее HP превышает максимум — обрезаем
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        super().save(*args, **kwargs)

    def set_location(self, sublocation):
        """
        Установить текущее местоположение пользователя.
        
        Требуется обязательный аргумент `sublocation`.
        Глобальная локация берётся автоматически из подлокации.
        """
        if sublocation._meta.label != 'game.SubLocation':
            raise TypeError(f"Ожидался game.SubLocation")
        
        self.current_sublocation = sublocation
        self.current_global_location = sublocation.global_location
        self.save(update_fields=['current_sublocation', 'current_global_location'])
    
    @property
    def max_hp(self):
        """Максимальное здоровье зависит от выносливости и уровня."""
        return self.stamina * 10 + self.level * 10

    @property
    def xp_to_next_level(self):
        """Опыт, необходимый для перехода на следующий уровень."""
        exp = self.xp_required_for_level(self.level + 1) - self.experience
        return exp

    @property
    def xp_progress(self):
        """Сколько опыта НАБРАНО в текущем уровне (для прогресс-бара)."""
        exp = self. experience - self.xp_required_for_level(self.level)
        return exp
    
    def add_experience(self, amount):
        """Начислить опыт."""
        self.experience += amount
        self.level = self.calculate_current_level()
        self.save(update_fields=['experience', 'level'])

    @property
    def is_banned(self):
        if self.banned_until is None:
            return False
        return timezone.now() < self.banned_until
    
    @property
    def is_premium(self):
        if self.premium_until is None:
            return False
        return timezone.now() < self.premium_until


    def get_balance(self, currency_code):
            """Запрос баланса выбранной валюты"""
            try:
                wallet = self.wallets.get(currency__code=currency_code)
                return wallet.amount
            except Exception:
                return 0