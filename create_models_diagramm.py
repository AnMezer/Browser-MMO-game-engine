# Скрипт создания визуализации моделей
# Сохраняет файл docs/models_[дата]_[время].pdf
import os
import subprocess
import sys
from datetime import datetime

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_path = f'docs/models_{timestamp}.pdf'

os.makedirs('docs', exist_ok=True)

try:
    subprocess.run(
        [sys.executable, "manage.py", "graph_models", "-a", "-o", output_path],
        check=True)
    print(f'Диаграмма успешно сохранена: {output_path}')
except subprocess.CalledProcessError as e:
    print(f'Ошибка при генерации диаграммы: {e}')
except FileNotFoundError:
    print('pУбедитесь, что находитесь в корне проекта (где manage.py)')