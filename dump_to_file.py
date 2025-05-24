
import os
import django

# Укажи путь к своему settings.py — например: capybara.settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capybara.settings")

# Инициализируем Django
django.setup()

from django.core.management import call_command

# Делаем дамп в файл UTF-8
with open("datadump.json", "w", encoding="utf-8") as f:
    call_command(
        "dumpdata",
        exclude=["contenttypes", "auth.Permission"],
        use_natural_primary_keys=True,
        use_natural_foreign_keys=True,
        stdout=f
    )



# загружаем данные из файла
# python manage.py loaddata datadump.json --verbosity 3