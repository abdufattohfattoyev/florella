"""
Usage:
  python manage.py import_categories

Scans media/categories/ for image files, sends each to Claude Vision,
gets an Uzbek category name back, then saves it to the DB.
Skips images already imported (matched by filename).
Requires ANTHROPIC_API_KEY in .env or environment.
"""

import base64
import os
import re
from pathlib import Path

import anthropic
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from menu.models import Category

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

SYSTEM_PROMPT = """Siz cafe menu kategoriyalarini tahlil qiluvchi yordamchisiz.
Berilgan rasm asosida:
1. Kategoriya nomi (o'zbek tilida, 1-3 so'z)
2. Qisqa tavsif (o'zbek tilida, 1 jumla)

Javobni FAQAT quyidagi formatda bering:
NOMI: [kategoriya nomi]
TAVSIF: [qisqa tavsif]"""


class Command(BaseCommand):
    help = 'Rasmlarni tahlil qilib kategoriyalar yaratadi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            default='categories',
            help='media/ ichidagi papka nomi (default: categories)',
        )

    def handle(self, *args, **options):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            self.stderr.write(self.style.ERROR(
                'ANTHROPIC_API_KEY topilmadi! .env faylga qo\'shing.'
            ))
            return

        folder = Path(settings.MEDIA_ROOT) / options['folder']
        if not folder.exists():
            self.stderr.write(self.style.ERROR(f'Papka topilmadi: {folder}'))
            return

        images = [f for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTS]
        if not images:
            self.stdout.write(self.style.WARNING('Rasmlar topilmadi.'))
            return

        client = anthropic.Anthropic(api_key=api_key)
        created = 0
        skipped = 0

        for idx, img_path in enumerate(sorted(images), 1):
            rel_path = f"{options['folder']}/{img_path.name}"

            if Category.objects.filter(image=rel_path).exists():
                self.stdout.write(f'  ⏭  {img_path.name} — allaqachon mavjud')
                skipped += 1
                continue

            self.stdout.write(f'  🔍 {img_path.name} tahlil qilinmoqda...')

            try:
                name, description = self._analyze_image(client, img_path)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'     Xato: {e}'))
                continue

            slug = self._unique_slug(slugify(name, allow_unicode=True) or f'category-{idx}')

            category = Category(name=name, slug=slug, description=description, order=idx * 10)
            with img_path.open('rb') as f:
                category.image.save(img_path.name, File(f), save=False)
            category.save()

            self.stdout.write(self.style.SUCCESS(f'  ✅ Yaratildi: "{name}"  [{slug}]'))
            created += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Tugadi — yaratildi: {created}, o\'tkazib yuborildi: {skipped}'
        ))

    def _analyze_image(self, client, img_path: Path):
        ext = img_path.suffix.lower().lstrip('.')
        media_type = 'image/jpeg' if ext in ('jpg', 'jpeg') else f'image/{ext}'

        with img_path.open('rb') as f:
            data = base64.standard_b64encode(f.read()).decode()

        response = client.messages.create(
            model='claude-opus-4-8',
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{
                'role': 'user',
                'content': [
                    {'type': 'image', 'source': {'type': 'base64', 'media_type': media_type, 'data': data}},
                    {'type': 'text', 'text': 'Bu rasmda nima ko\'ryapsiz? Kategoriya nomini aniqlang.'},
                ],
            }],
        )

        text = response.content[0].text
        name = self._extract(text, 'NOMI') or img_path.stem.replace('_', ' ').title()
        description = self._extract(text, 'TAVSIF') or ''
        return name, description

    @staticmethod
    def _extract(text: str, key: str) -> str:
        match = re.search(rf'{key}:\s*(.+)', text)
        return match.group(1).strip() if match else ''

    @staticmethod
    def _unique_slug(base: str) -> str:
        slug, counter = base, 1
        while Category.objects.filter(slug=slug).exists():
            slug = f'{base}-{counter}'
            counter += 1
        return slug
