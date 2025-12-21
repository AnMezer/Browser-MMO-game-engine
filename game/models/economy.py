from django.db import models

from users.models import CustomUser


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)  # 'GOLD', 'CRYSTAL', 'FUEL'
    name = models.CharField(max_length=30)               # 'Золото', 'Кристаллы', 'Топливо'
    is_active = models.BooleanField(default=True)


    class Meta:
        default_related_name = 'currencies'
        verbose_name = 'валюта'
        verbose_name_plural = 'Валюты'

    def __str__(self):
        return self.name


class Wallet(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='wallets',
        verbose_name='Персонаж'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        verbose_name='Валюта'
    )
    amount = models.PositiveBigIntegerField(default=0, verbose_name='Кол-во')

    class Meta:
        unique_together = ('user', 'currency')
        default_related_name = 'wallets'
        verbose_name = 'кошелек'
        verbose_name_plural = 'Кошельки'

    def add_currency(self, currency_code, amount):
        """Добавление нужного кол-ва указанной валюты"""
        try:
            currency = Currency.objects.get(code=currency_code)
        except Currency.DoesNotExist:
            raise ValueError(f"Валюта с кодом '{currency_code}' не существует.")
        
        wallet, created = self.wallets.get_or_create(
            currency=Currency.objects.get(code=currency_code),
            defaults={'amount': 0}
        )
        wallet.amount += amount
        wallet.save(update_fields=['amount'])