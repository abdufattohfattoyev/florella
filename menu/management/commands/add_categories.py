from django.core.management.base import BaseCommand
from menu.models import Category

CATEGORIES = [
    ('sushi',              'Суши',              'Классик ва авторлик суши турлари',    1),
    ('roll-holodny',       'Ролл холодный',     'Совуқ роллар — тоза ва нафис',        2),
    ('roll-zapechyonnye',  'Ролл запечённые',   'Куйдирилган роллар — иссиқ ва хушбўй', 3),
    ('zakuski',            'Закуски',           'Енгил закускалар',                     4),
    ('ichimliklar',        'Ичимликлар',        'Иссиқ ва совуқ ичимликлар',           5),
    ('souslar',            'Соуслар',           'Авторлик ва классик соуслар',          6),
    ('setlar',             'Сетлар',            'Иккига мўлжалланган роллар тўплами',   7),
    ('pizzalar',           'Пиццалар',          'Ўтин ўчоқда пиширилган пиццалар',     8),
    ('desertlar',          'Десертлар',         'Ширин таомлар ва десертлар',           9),
]


class Command(BaseCommand):
    help = 'Kategoriyalarni qoshish (mavjud bolsa skip qiladi)'

    def handle(self, *args, **options):
        for slug, name, desc, order in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'order': order}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'[YARATILDI] {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'[MAVJUD]   {name}'))
        self.stdout.write(self.style.SUCCESS('\nBarcha kategoriyalar tayyor!'))
