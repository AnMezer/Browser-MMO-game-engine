from django.db import models
from django.utils.text import slugify


class GlobalLocation(models.Model):
    name = models.CharField(
        max_length=40,
        unique=True,
        verbose_name='Название локации'
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    is_city = models.BooleanField(
        default=False,
        blank=True,
        verbose_name='Это город?'
    )
    distance_to_the_city = models.PositiveSmallIntegerField(
        default=0,
        blank=True,
        verbose_name='Расстояние до города'
    )
    min_level = models.PositiveSmallIntegerField(
        blank=True,
        default=1,
        verbose_name='Минимальный уровень локации'
    )
    max_level = models.PositiveSmallIntegerField(
        blank=True,
        default=10,
        verbose_name='Максимальный уровень локации'
    )
    description = models.TextField(
        verbose_name='Описание глобальной локации',
        blank=True,
        default='Здесь еще нет описания, возможно когда-то появится'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        default_related_name = 'globallocations'
        verbose_name = 'глобальная локация',
        verbose_name_plural = 'Глобальные локации'

    def __str__(self):
        return f'{self.name} [{self.min_level} - {self.max_level}]'


class SubLocation(models.Model):
    name = models.CharField(
        max_length=40,
        verbose_name='Название внутренней локации',
    )
    global_location = models.ForeignKey(
            GlobalLocation,
            on_delete=models.PROTECT,
            related_name='sublocations',
            verbose_name='Глобальная локация'
    )
    slug = models.SlugField(blank=True, unique=True)
    distance_to_location_start = models.PositiveSmallIntegerField(
        default=0,
        blank=True,
        verbose_name='Расстояние до входа в локацию'
    )
    description = models.TextField(
        verbose_name='Описание саблокации',
        blank=True,
        default='Здесь еще нет описания, возможно когда-то появится'
    )
    min_level = models.PositiveSmallIntegerField(
        blank=True,
        default=1,
        verbose_name='Минимальный уровень локации'
    )
    max_level = models.PositiveSmallIntegerField(
        blank=True,
        default=10,
        verbose_name='Максимальный уровень локации'
    )

    monsters = models.ManyToManyField(
        'Monster',
        blank=True,
        related_name='locations',
        verbose_name='Монстры на локации'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('global_location', 'name')
        default_related_name = 'sublocations'
        verbose_name = 'внутренняя локация',
        verbose_name_plural = 'Внутренние локации'

    def __str__(self):
        return f'{self.name} [{self.min_level} - {self.max_level}]'