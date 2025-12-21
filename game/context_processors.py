from typing import cast

from django.utils import timezone

from users.models import CustomUser

from .constants import FIGHT_COOLDOWN_SECONDS


def current_user_data(request):
    """
    Добавляет данные о текущем пользователе (если авторизован)
    для использования в шаблонах.
    """
    STATS_DESCRIPTIONS = {
        'Сила': 'Определяет физическую атаку. Чем выше — тем больший урон наносит оружие.',
        'Защита': 'Снижает получаемый физический урон.',
        'Ловкость': 'Повышает шанс критического удара и уклонения от атак.',
        'Выносливость': 'Увеличивает максимальное здоровье (HP).',
        'Интеллект': 'Определяет магическую атаку и регенерацию маны.',
        'Дух': 'Увеличивает максимальную ману (MP).',
        'Воля': 'Снижает получаемый магический урон.',
        'Удача': 'Увеличивает вероятность приятных событий'
    }
    if request.user.is_authenticated:
        user = cast(CustomUser, request.user)
        # ---- Считаем кулдаун между атаками ----
        cooldown = 0
        on_cooldown = False
        if user.last_fight_at:
            elapsed = (timezone.now() - user.last_fight_at).total_seconds()
            if elapsed < FIGHT_COOLDOWN_SECONDS:
                cooldown = int(FIGHT_COOLDOWN_SECONDS - elapsed)
                on_cooldown = True

        # ---------------------------------------

        # ---- Готовим списки статов для отображения ----
        stats = {
                'Сила': user.strength,
                'Защита': user.defense,
                'Ловкость': user.dexterity,
                'Выносливость': user.stamina,
                'Интеллект': user.intelligence,
                'Дух': user.spirit,
                'Воля': user.willpower,
                'Удача': user.luck,
        }

        stats_with_desc = [
            {'name': k, 'value': v, 'desc': STATS_DESCRIPTIONS.get(k, '')}
            for k, v in stats.items()
        ]
        mid = len(stats_with_desc) // 2
        left_stats = stats_with_desc[:mid]
        right_stats = stats_with_desc[mid:]
        # -----------------------------------------------

        # ---- Расчет значений опыта для отображения ----
        xp_for_current_level_abs = user.xp_required_for_level(user.level) # Сколько нужно опаты для текущего уровня всего, от 0
        xp_for_next_level_abs = user.xp_required_for_level(user.level + 1) # Сколько нужно опаты для следующего уровня всего, от 0
        xp_on_this_level = user.experience - user.xp_required_for_level(user.level) # Сколько опыта набрано после перехода на текущий уровень
        delta_xp_for_levels = xp_for_next_level_abs - xp_for_current_level_abs # Сколько опыта между границей текущего уровня и следующего
        xp_for_next_level = user.xp_required_for_level(user.level + 1) - user.experience # Сколько опыта осталось набрать для перехода на новый уровень

        return {
                'current_user_data': {
                    'nickname': user.nickname,
                    'level': user.level,
                    'avatar_path': user.avatar,
                    'current_global_location': user.current_global_location,
                    'current_sublocation': user.current_sublocation,
                    'left_stats': left_stats,
                    'right_stats': right_stats,
                    'max_hp': user.max_hp,
                    'current_hp': user.current_hp,
                    'on_cooldown': on_cooldown,
                    'cooldown': cooldown,
                    'xp_for_next_level': xp_for_next_level,
                    'delta_xp_for_levels': delta_xp_for_levels,
                    'xp_on_this_level': xp_on_this_level,

            }
        }
        
    else:
        return {
            'current_user_data': None
        }
