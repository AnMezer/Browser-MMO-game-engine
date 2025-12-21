from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .models import (
    ActivityLink,
    Currency,
    GlobalLocation,
    Item,
    ItemInstance,
    ItemStack,
    Monster,
    MonsterDrop,
    Shop,
    ShopItem,
    SubLocation,
    Wallet,
)

# Список моделей, которые могут быть активностями
ACTIVITY_MODELS = [Shop]

class ShopItemInline(admin.TabularInline):
    model = ShopItem
    extra = 1  # сколько пустых строк показывать по умолчанию
    autocomplete_fields = ['item']  # улучшает UX при большом количестве предметов

class ActivityLinkForm(forms.ModelForm):
    activity_obj = forms.ChoiceField(
        choices=[],
        required=False,
        label="Активность"
    )

    class Meta:
        model = ActivityLink
        fields = ['activity_obj', 'content_type', 'object_id']
        widgets = {
            'content_type': forms.HiddenInput(),
            'object_id': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Собираем все доступные объекты
        choices = [('', '— Выберите активность —')]
        for model in ACTIVITY_MODELS:
            ct = ContentType.objects.get_for_model(model)
            for obj in model.objects.all():
                choices.append((
                    f"{ct.id}:{obj.pk}",
                    f"{obj}"  # или f"{model._meta.verbose_name}: {obj}"
                ))
        self.fields['activity_obj'].choices = choices

        # Если объект уже сохранён — подставляем текущее значение
        if self.instance and self.instance.pk and self.instance.activity:
            ct = ContentType.objects.get_for_model(self.instance.activity)
            self.fields['activity_obj'].initial = f"{ct.id}:{self.instance.activity.pk}"

    def clean_activity_obj(self):
        data = self.cleaned_data['activity_obj']
        if data:
            try:
                ct_id, obj_id = data.split(':')
                ct_id = int(ct_id)
                obj_id = int(obj_id)
                # Проверяем, что такая комбинация существует
                ct = ContentType.objects.get(id=ct_id)
                model_class = ct.model_class()
                if not model_class:
                    raise forms.ValidationError("Недопустимый тип активности")
                if not model_class.objects.filter(pk=obj_id).exists():
                    raise forms.ValidationError("Объект не найден")
            except (ValueError, ContentType.DoesNotExist):
                raise forms.ValidationError("Некорректный формат выбора")
        return data

    def save(self, commit=True):
        activity_choice = self.cleaned_data.get('activity_obj')
        if activity_choice:
            ct_id, obj_id = activity_choice.split(':')
            self.instance.content_type_id = int(ct_id)
            self.instance.object_id = int(obj_id)
        else:
            # Если ничего не выбрано — обнуляем связь
            self.instance.content_type = None
            self.instance.object_id = None
        return super().save(commit=commit)
   
    def clean(self):
        cleaned_data = super().clean()
        print("Ошибки формы:", self.errors)
        return cleaned_data
        


class ActivityLinkInline(admin.TabularInline):
    model = ActivityLink
    form = ActivityLinkForm
    extra = 1

@admin.register(GlobalLocation)
class GlobalLocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'levels',
        'slug',
    )
    search_fields = ('name',)
    #  Заполняет slug в реальном времени.
    prepopulated_fields = {'slug': ('name',)}

    def levels(self, obj):
        return f'{obj.min_level} - {obj.max_level}'
    levels.short_description = 'Уровни локации'  # Подпись в админке
    levels.admin_order_field = 'levels'  # Чтобы можно было сортировать по этому полю

@admin.register(SubLocation)
class SubLocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'levels',
        'global_location',
        'slug',
    )
    list_filter = (
        'global_location',
    )
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_vertical = ('monsters',)
    autocomplete_fields = ('monsters',)
    inlines = [ActivityLinkInline]

    def levels(self, obj):
        return f'{obj.min_level} - {obj.max_level}'
    levels.short_description = 'Уровни локации'  # Подпись в админке
    levels.admin_order_field = 'levels'  # Чтобы можно было сортировать по этому полю

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'is_active'
    )


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'currency',
        'amount'
    )
    list_filter = (
        'currency',
    )
    search_fields = ('user',)


@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'level',
        'xp_reward',
        'avatar',
    )
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'item_type', 'slot', 'is_stacked', 'is_active')
    list_filter = ('item_type', 'slot', 'is_active')
    search_fields = ('name', 'code')
    list_editable = ('is_active',)
    prepopulated_fields = {
        'code': ('name',),
        'slug': ('name',)
        }

   
@admin.register(MonsterDrop)
class MonsterDropAdmin(admin.ModelAdmin):

    list_display = (
        'monster',
        'item_type',
        'currency',
        'item',
        'amount',
        'chance_percent'
    )

    def amount(self, obj):
        return f'{obj.min_amount} - {obj.max_amount}'


@admin.register(ItemStack)
class ItemStackAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'item',
        'quantity',
    )
    search_fields = (
        'owner',
    )

@admin.register(ItemInstance)
class ItemInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'item',
        'world_id'
    )

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'min_level_items',
        'max_level_items',
    )
    inlines = [ShopItemInline]