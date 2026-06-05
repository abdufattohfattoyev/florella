"""
python manage.py seed_data
Эски маълумотларни тозалаб, 6 та категория ва 58 та меню элементи яратади.
Расмлар media/menu/ дан олинади, категория thumbnail'лари media/categories/ га сақланади.
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from menu.models import Category, MenuItem

MEDIA    = Path(settings.MEDIA_ROOT)
MENU_DIR = MEDIA / 'menu'
CAT_DIR  = MEDIA / 'categories'


def fn(n):
    """Расм файл номини қайтаради."""
    suffix = '19-42-29' if n <= 3 else '19-42-30'
    return f'photo_{n}_2026-06-03_{suffix}.jpg'


# (slug, кирилл_ном, таvsif, thumbnail_photo_n_or_None, order)
CATEGORIES = [
    ('rolllar',     'Роллар',      'Куйдирилган, уро ва классик суши роллар',       1,    10),
    ('pizzalar',    'Пиццалар',    'Ўтин ўчоқда пиширилган авторлик пиццалар',      13,   20),
    ('setlar',      'Сетлар',      'Икки кишига мўлжалланган роллар ва пицца тўплами', 30, 30),
    ('zakuskalar',  'Закускалар',  'Енгил закуска ва иштаҳа очувчилар',             None, 40),
    ('ichimliklar', 'Ичимликлар',  'Иссиқ ва совуқ ичимликлар',                     None, 50),
    ('kokteyl',     'Коктейль',    'Алкогольсиз ва авторлик коктейллар',             None, 60),
]

# (cat_slug, ном, таvsif, photo_n_or_None, нарх, машҳурми)
MENU_ITEMS = [

    # ══════════ РОЛЛАР (photos 1-11, 32-48) ══════════
    ('rolllar', 'Яки Гункан',       'Куйдирилган гункан — унаги соус ва кунжут билан',     1,  49000, True),
    ('rolllar', 'Сусам Яки',        'Куйдирилган ролл — қора кунжут ва терияки соус',       2,  52000, True),
    ('rolllar', 'Сёмга Лимон Уро',  'Свежий сёмга уро — лимон ва укроп безакли',           3,  56000, True),
    ('rolllar', 'Тунец Уро',        'Тунец билан уро ролл — тоза денгиз таъми',            4,  58000, False),
    ('rolllar', 'Яки Спешл',        'Йирик куйдирилган ролл — унаги соус',                 5,  55000, True),
    ('rolllar', 'Сёмга Уро',        'Сёмга уро ролл — лимон билан нафис безатилган',       6,  54000, False),
    ('rolllar', 'Лока Яки',         'Куйдирилган ролл — терияки ва кунжут',                7,  50000, False),
    ('rolllar', 'Терияки Ролл',     'Классик терияки соусли куйдирилган ролл',             8,  48000, False),
    ('rolllar', 'Самурай Яки',      'Самурай услубида куйдирилган ролл',                   9,  50000, False),
    ('rolllar', 'Гункан Яки',       'Нори пипа ичидаги куйдирилган суши',                 10, 46000, False),
    ('rolllar', 'Флорелла Филадельфия', 'Свежий сёмга ва кремли пишлоқ',                 11, 62000, True),
    ('rolllar', 'Эби Мак',          'Классик креветкали мак ролл',                        32, 38000, False),
    ('rolllar', 'Тунец Мак',        'Тунец билан анъанавий мак ролл',                     33, 40000, False),
    ('rolllar', 'Сёмга Мак',        'Свежий сёмгали мак ролл',                            34, 42000, False),
    ('rolllar', 'Бейкед Ролл',      'Куйдирилган ролл — нафис таъм ва ароматли соус',     35, 47000, False),
    ('rolllar', 'Унаги Уро',        'Сёмга ва унаги соус билан уро ролл',                 36, 62000, True),
    ('rolllar', 'Флорелла Яки',     'Флорелла Sushi авторлик куйдирилган ролл',           37, 54000, True),
    ('rolllar', 'Дракон Яки',       'Куйдирилган ролл — дракон услубида безатилган',      38, 56000, False),
    ('rolllar', 'Спайс Яки',        'Аччиқли куйдирилган ролл',                           39, 49000, False),
    ('rolllar', 'Яки Меню',         'Куйдирилган ролл авторлик соус билан',               40, 53000, False),
    ('rolllar', 'Голд Яки',         'Олтин безакли куйдирилган ролл',                     41, 58000, True),
    ('rolllar', 'Нори Яки',         'Нори ичидаги куйдирилган суши',                      42, 50000, False),
    ('rolllar', 'Тошкент Яки',      'Маҳаллий спецлик билан куйдирилган ролл',            43, 47000, False),
    ('rolllar', 'Калифорния',       'Тобико, авокадо ва краб билан Калифорния',           44, 55000, True),
    ('rolllar', 'Унаги Яки',        'Мукаммал куйдирилган унаги яки суши',                45, 60000, True),
    ('rolllar', 'Сакура Яки',       'Гулдор безакли куйдирилган ролл',                   46, 52000, False),
    ('rolllar', 'Принц Яки',        'Нафис куйдирилган принц суши',                      47, 55000, False),
    ('rolllar', 'Қизил Яки',        'Қизил гуруч ва куйдирилган тепели ролл',            48, 60000, True),

    # ══════════ ПИЦЦАЛАР (photos 12-29) ══════════
    ('pizzalar', 'Флорелла Спайс',   'Халапеньо ва аччиқ соус — ўткир таъмли',           12, 62000, True),
    ('pizzalar', 'Пепперони',        'Пепперони колбаса ва мозарелла пишлоқ',             13, 65000, True),
    ('pizzalar', 'Песто Чикен',      'Товуқ, пармезан ва пишлоқ пиццаси',                14, 63000, False),
    ('pizzalar', 'Маргарита',        'Черри помидор, песто ва мозарелла',                 15, 55000, False),
    ('pizzalar', 'Картошкали',       'Қовурма картошка, корнишон ва пепперони',           16, 60000, True),
    ('pizzalar', 'Ветчина Қалампир', 'Ветчина, қизил қалампир ва майонез',               17, 58000, False),
    ('pizzalar', 'Ассорти',          'Ветчина, помидор ва рангли қалампир',               18, 60000, False),
    ('pizzalar', 'Бургер Пицца',     'Мол гўшти, корнишон ва горчица соус',              19, 65000, True),
    ('pizzalar', 'Диаволо',          'Аччиқли салями ва чили қалампир',                   20, 62000, False),
    ('pizzalar', 'Ҳавайи',           'Ананас ва ветчина — ширин-аччиқ уйғунлик',         21, 58000, False),
    ('pizzalar', 'Цезарь',           'Руккола, черри помидор ва пармезан',               22, 63000, False),
    ('pizzalar', 'Флорелла Мих',     'Шеф авторлик пиццаси — ноёб рецепт',               23, 75000, True),
    ('pizzalar', 'Тўрт Пишлоқ',     'Тўрт хил пишлоқ уйғунлиги',                        25, 68000, True),
    ('pizzalar', 'Замбуруғли',       'Шампиньон, фета пишлоқ ва сабзавот',               26, 57000, False),
    ('pizzalar', 'Том Ям',           'Том-ям соус ва денгиз мевалари',                    27, 72000, True),
    ('pizzalar', 'Горчица Чикен',    'Горчица соус, товуқ ва помидор',                   28, 60000, False),
    ('pizzalar', 'Гўштли',           'Мол гўшти ва горчица соус',                        29, 65000, False),
    ('pizzalar', 'Маргарита Классик','Классик помидор соус ва мозарелла',                24, 52000, False),

    # ══════════ СЕТЛАР ══════════
    ('setlar', 'Яки Сети 12 та',    '12 та куйдирилган ролл ассортиментда',              30, 145000, True),
    ('setlar', 'Флорелла Гранд Сет','16 та ролл + 1 пицца — иккига мўлжалланган',        31, 185000, True),
    ('setlar', 'Сёмга Сети 16 та',  '16 та сёмгали уро ролл ва унаги соус',              3,  135000, False),
    ('setlar', 'Пицца + Ролл Сети', '8 та ролл + битта пицца — хушбахт зиёфат',          12, 165000, True),
    ('setlar', 'Тунец Сети 16 та',  '16 та тунец уро ролл ва соус',                      4,  140000, False),

    # ══════════ ЗАКУСКАЛАР ══════════
    ('zakuskalar', 'Мисо шўрва',    'Анъанавий японча мисо шўрва — тофу ва вакаме',  None, 18000, False),
    ('zakuskalar', 'Эдамаме',       'Тузланган ёш соя дуккаклари — ширин-тузли',     None, 22000, True),
    ('zakuskalar', 'Нори Чипс',     'Денгиз сабзавоти чипси — хрусткий',             None, 15000, False),
    ('zakuskalar', 'Гёза',          'Қовурилган пельмен — товуқ ва зираворлар',      None, 35000, True),
    ('zakuskalar', 'Темпура',       'Қовурилган сабзавот ва креветка темпура',        None, 42000, False),

    # ══════════ ИЧИМЛИКЛАР ══════════
    ('ichimliklar', 'Матча Чой',        'Японча кўк чой — иссиқ ёки муздак',          None, 18000, True),
    ('ichimliklar', 'Апельсин Шарбати', 'Тоза сиқилган апельсин шарбати',             None, 22000, False),
    ('ichimliklar', 'Уй Лимонади',      'Нана ва лимон билан уй лимонади',            None, 20000, True),
    ('ichimliklar', 'Минерал Сув',      'Газли ёки газсиз минерал сув 0.5л',          None, 12000, False),
    ('ichimliklar', 'Кола / Фанта',     'Совутилган 0.33л банкали ичимлик',           None, 15000, False),
    ('ichimliklar', 'Саке Иссиқ',       'Анъанавий японча саке — иссиқ',              None, 45000, False),

    # ══════════ КОКТЕЙЛЬ ══════════
    ('kokteyl', 'Клубника Мохито',  'Клубника, нана ва лайм — алкогольсиз',           None, 35000, True),
    ('kokteyl', 'Кўк Лагуна',       'Экзотик мева шираси коктейли',                   None, 38000, True),
    ('kokteyl', 'Тропикал Микс',    'Манго, ананас ва кокос — тропик таъми',           None, 40000, False),
    ('kokteyl', 'Флорелла Спешл',   'Рестораннинг авторлик коктейли',                  None, 42000, True),
    ('kokteyl', 'Юзу Лимонад',      'Японча юзу лимон шарбати',                       None, 36000, False),
]


class Command(BaseCommand):
    help = 'Эски маълумотларни тозалаб, янги категориялар ва меню яратади'

    def handle(self, *args, **options):
        CAT_DIR.mkdir(parents=True, exist_ok=True)

        # ── Tozalash ──
        self.stdout.write('  Eski malumotlar tozalanmoqda...')
        MenuItem.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING('  Tozalandi.\n'))

        # ── Kategoriyalar ──
        self.stdout.write('  Kategoriyalar yaratilmoqda...')
        cats = {}
        for slug, name, desc, thumb_n, order in CATEGORIES:
            cat = Category.objects.create(
                slug=slug, name=name, description=desc, order=order
            )
            if thumb_n:
                src = MENU_DIR / fn(thumb_n)
                dst = CAT_DIR / f'{slug}.jpg'
                if src.exists():
                    if not dst.exists():
                        shutil.copy2(src, dst)
                    with dst.open('rb') as f:
                        cat.image.save(f'{slug}.jpg', File(f), save=True)
            cats[slug] = cat
            self.stdout.write(self.style.SUCCESS(f'  [OK] {slug}'))

        self.stdout.write('')

        # ── Menu elementlari ──
        self.stdout.write('  Menu elementlari yaratilmoqda...')
        created = 0
        for cat_slug, name, desc, photo_n, price, popular in MENU_ITEMS:
            cat = cats.get(cat_slug)
            if not cat:
                continue
            item = MenuItem.objects.create(
                category=cat,
                name=name,
                description=desc,
                price=price,
                is_available=True,
                is_popular=popular,
            )
            if photo_n:
                src = MENU_DIR / fn(photo_n)
                if src.exists():
                    with src.open('rb') as f:
                        item.image.save(fn(photo_n), File(f), save=True)
            created += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'  DONE! Categories: {len(CATEGORIES)}, Menu items: {created}'
        ))
