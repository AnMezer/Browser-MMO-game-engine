from django.contrib import admin
from django.db import models
from django.utils import timezone

from .models import CustomUser


# -- Я не понимаю, как работают фильтры, нужно разобраться --
class BannedStatusFilter(admin.SimpleListFilter):
    title = 'Статус бана'          # Заголовок в сайдбаре админки
    parameter_name = 'banned'      # URL-параметр: ?banned=yes

    def lookups(self, request, model_admin):
        # Варианты в фильтре
        return (
            ('yes', 'Забанен'),
            ('no', 'Не забанен'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'yes':
            # Забанен: banned_until в будущем
            return queryset.filter(banned_until__gt=now)
        if self.value() == 'no':
            # Не забанен: banned_until в прошлом ИЛИ NULL
            return queryset.filter(
                models.Q(banned_until__lte=now) | models.Q(banned_until__isnull=True)
            )
        return queryset  # если фильтр не выбран


class PremiumStatusFilter(admin.SimpleListFilter):
    title = 'Статус премиума'          # Заголовок в сайдбаре админки
    parameter_name = 'premium'      # URL-параметр: ?banned=yes

    def lookups(self, request, model_admin):
        return (
            ('yes', 'С премиумом'),
            ('no', 'Без премиума'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'yes':
            return queryset.filter(premium_until__gt=now)
        if self.value() == 'no':
            return queryset.filter(
                models.Q(premium_until__lte=now) | models.Q(premium_until__isnull=True)
            )
        return queryset


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'nickname',
        'experience',
        'level',
        'is_banned',
        'is_premium',
        'banned_until',
        'premium_until',
    )
    list_editable = (
        'experience',
        'banned_until',
        'premium_until'
    )
    search_fields = ('nickname', 'username', 'email')
    list_filter = (BannedStatusFilter, PremiumStatusFilter, 'current_sublocation')


