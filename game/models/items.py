import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from users.models import CustomUser
from game.constants import SLOT_CHOICES, ITEM_TYPE_CHOICES
from typing import TYPE_CHECKING


def item_logo_path(instance, filename):
    """
    Возвращает путь: 'item/<slug>.<ext>'
    """
    ext = filename.split('.')[-1].lower()
    slug = instance.slug
    return f'item/{slug}.{ext}'


class Item(models.Model):
    if TYPE_CHECKING:
        id: int

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Наименование'
    )
    code = models.CharField(
        max_length=30,
        unique=True,
        blank=True,  # ← разрешаем оставлять пустым в форме
        help_text="Уникальный код (генерируется автоматически)",
        verbose_name='Код предмета'
    )
    slug = models.SlugField(unique=True, blank=True)
    min_level = models.PositiveIntegerField(
        default=1,
        verbose_name="Мин. уровень игрока"
    )
    is_sellable = models.BooleanField(default=False)

    cost = models.PositiveIntegerField(
        verbose_name='Базовая стоимость',
        help_text='Стоимость продажи в магазин'
    )
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        verbose_name="Тип предмета"
    )

    # --- Слот (только для экипировки) ---

    slot = models.CharField(
        max_length=20,
        choices=SLOT_CHOICES,
        blank=True,
        verbose_name="Слот экипировки",
        help_text="Заполняется только для брони, оружия, амулетов"
    )

    # --- Статы (для экипировки) ---
    strength = models.PositiveSmallIntegerField(default=0)
    defense = models.PositiveSmallIntegerField(default=0)
    dexterity = models.PositiveSmallIntegerField(default=0)
    stamina = models.PositiveSmallIntegerField(default=0)
    intelligence = models.PositiveSmallIntegerField(default=0)
    spirit = models.PositiveSmallIntegerField(default=0)
    willpower = models.PositiveSmallIntegerField(default=0)
    item_slots = models.PositiveSmallIntegerField(default=0)
    luck = models.PositiveSmallIntegerField(default=0)

    # --- Прочее ---
    is_stacked = models.BooleanField(
        default=True,
        help_text="Можно ли складывать в стак (хлам, ресурсы, зелья)"
    )
    is_active = models.BooleanField(default=True)

    logo = models.ImageField(
        upload_to=item_logo_path,
        blank=True,
        null=True,
        verbose_name='Иконка'
    )
    description = models.TextField(
        verbose_name='Описание предмета',
        blank=True,
        default='Здесь еще нет описания, возможно когда-то появится'
    )

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return self.name

    def clean(self):
        # Слот можно указывать только для определённых типов
        if self.item_type in ['ARMOR', 'WEAPON', 'AMULET']:
            if not self.slot:
                raise ValidationError(f"Для типа '{self.get_item_type_display()}' обязательно указать слот.")
        else:
            if self.slot:
                raise ValidationError(f"Слот нельзя указывать для типа '{self.get_item_type_display()}'.")

    def save(self, *args, **kwargs):
        if not self.code:
            # Генерируем код из имени
            self.code = slugify(self.name)
        self.full_clean()  # вызывает clean()
        super().save(*args, **kwargs)

    
    def is_unique_instance_needed(self):
        """
        Возвращает True, если при выдаче предмета нужно создавать ItemInstance.
        """
        return (
            not self.is_stacked and
            self.item_type not in ['QUEST']  # можно расширить список позже
        )


class ItemInstance(models.Model):
    if TYPE_CHECKING:
        item: Item

    world_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='Уникальный ID'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name='Шаблон предмета'
    )
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Владелец'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    strength_bonus = models.SmallIntegerField(default=0)
    defense_bonus = models.SmallIntegerField(default=0)
    dexterity_bonus = models.SmallIntegerField(default=0)
    stamina_bonus = models.SmallIntegerField(default=0)
    intelligence_bonus = models.SmallIntegerField(default=0)
    spirit_bonus = models.SmallIntegerField(default=0)
    willpower_bonus = models.SmallIntegerField(default=0)
    item_slots_bonus = models.SmallIntegerField(default=0)
    luck_bonus = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Уникальный экземпляр предмета'
        verbose_name_plural = 'Уникальные экземпляры предметов'

    def __str__(self):
        return f"{self.item.name} ({self.world_id}) → {self.owner.username}"
    
    def get_total_stat(self, stat_name):
        """Возвращает полный бонус по названию характеристики."""
        base = getattr(self.item, stat_name, 0)
        bonus = getattr(self, f"{stat_name}_bonus", 0)
        return base + bonus


class ItemStack(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name='Предмет'
    )
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Кол-во'
    )

    def clean(self):
        if not self.item.is_stacked:
            raise ValidationError('Нельзя добавить нестакаемый предмет в стек.')

    def save(self, *args, **kwargs):
        self.full_clean()  # вызывает clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('owner', 'item')
        verbose_name = "Стек предметов"
        verbose_name_plural = "Стеки предметов"
