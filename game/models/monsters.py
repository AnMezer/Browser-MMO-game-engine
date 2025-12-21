from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from typing import TYPE_CHECKING


from game.models import Currency, Item



def monster_avatar_path(instance, filename):
    """
    Возвращает путь: 'monsters/<slug>.<ext>'
    """
    ext = filename.split('.')[-1].lower()
    slug = instance.slug
    return f'monsters/{slug}.{ext}'


class Monster(models.Model):
    name = models.CharField(max_length=30, unique=True)
    level = models.PositiveIntegerField(default=1)

    strength = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Сила"
    )
    defense = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Защита"
    )
    dexterity = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Ловкость"
    )
    stamina = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Выносливость"
    )
    intelligence = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Интеллект"
    )
    spirit = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Дух"
    )
    willpower = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Воля"
    )

    xp_reward = models.PositiveIntegerField(default=20)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)

    avatar = models.ImageField(
        upload_to=monster_avatar_path,
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание монстра'
    )

    class Meta:
        unique_together = ('name', 'level')
        verbose_name = 'Тип монстра'
        verbose_name_plural = 'Типы монстров'

    def __str__(self):
        return f"{self.name} [{self.level}]"

    if TYPE_CHECKING:
        drops: models.manager.Manager["MonsterDrop"]

    # --- Расчет статов ---
    @property
    def max_hp(self):
        return self.vitality * 8


class MonsterDrop(models.Model):

    monster = models.ForeignKey(
        Monster,
        on_delete=models.CASCADE,
        verbose_name='Монстр',
        related_name='drops'
    )
    item_type = models.CharField(
        max_length=10,
        choices=(
            ('CURRENCY', 'Валюта'),
            ('ITEM', 'Предмет')
        ),
        verbose_name='Тип предмета'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Валюта'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        null=False,
        blank=True
    )
    min_amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Минимальное кол-во'
    )
    max_amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Максимальное кол-во'
    )
    chance_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Вероятность выпадения в процентах (0.00–100.00)",
        verbose_name='Шанс выпадения'
    )

    class Meta:
        verbose_name = 'Дроп с монстра'
        verbose_name_plural = 'Дропы с монстров'

    def clean(self):
        if self.chance_percent is not None:
            if self.chance_percent < 0:
                raise ValidationError({'chance_percent': 'Шанс не может быть отрицательным.'})
            if self.chance_percent > 100:
                raise ValidationError({'chance_percent': 'Шанс не может быть больше 100%.'})

        if self.item_type == 'CURRENCY':
            if not self.currency:
                raise ValidationError(f"Для типа '{self.get_item_type_display()}' обязательно указать тип валюты")
            if self.item:
                raise ValidationError(f"Для типа '{self.get_item_type_display()}' не нужно указывть предмет")
        if self.item_type == 'ITEM':
            if not self.item:
                raise ValidationError(f"Для типа '{self.get_item_type_display()}' обязательно указать предмет")
            if self.currency:
                raise ValidationError(f"Для типа '{self.get_item_type_display()}' не нужно указывть валюту")


    
            
            
    def save(self, *args, **kwargs):
        self.full_clean()  # вызывает clean()
        super().save(*args, **kwargs)