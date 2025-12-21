from django import template
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def avatar_url(avatar_path):
    """
    Возвращает URL статического файла аватара.
    Пример: avatar_url 'male/elf_1.svg' → /static/avatars/male/elf_1.svg
    """
    return static(f'avatars/{avatar_path}')