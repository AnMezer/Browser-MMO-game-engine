
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.text import slugify

from game.models import Item, SubLocation


class ActivityLink(models.Model):
    """Класс для подключения игровых активностей
    (магазин и т.д.) в саблокацию
    """
    sublocation = models.ForeignKey(SubLocation, on_delete=models.CASCADE, related_name='activity_links')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    activity = GenericForeignKey('content_type', 'object_id')

    class Meta:
        default_related_name = 'activity_links'


class Shop(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название магазина',
    )
    description = models.TextField(
        verbose_name='Описание предмета',
        blank=True,
        default='Здесь еще нет описания, возможно когда-то появится'
    )
    allowed_items = models.ManyToManyField(Item,
        through='ShopItem',
        blank=True,
        verbose_name='Доступные предметы'
    )
    min_level_items = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Минимальный уровень продаваемых предметов',
    )
    max_level_items = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Максимальный уровень продаваемых предметов',
    )

    class Meta:
        verbose_name = 'магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return (f"Магазин: {self.name}")


class ShopItem(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Предмет')
    price_coef = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Коэффициент цены магазина'
    )
    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = ('shop', 'item')
        verbose_name = 'предмет в магазине'
        verbose_name_plural = 'Предметы в магазине'

    def __str__(self):
        return f"{self.item.name} в {self.shop.name}"
