from django.db import migrations
from django.utils.text import slugify

def update_category_slugs(apps, schema_editor):
    Category = apps.get_model('ecommerce', 'Category')
    for category in Category.objects.all():
        if not category.slug:
            base_slug = slugify(category.name)
            category.slug = base_slug
            counter = 1
            while Category.objects.filter(slug=category.slug).exists():
                category.slug = f"{base_slug}-{counter}"
                counter += 1
            category.save()

class Migration(migrations.Migration):
    dependencies = [
        ('ecommerce', '0002_category_slug'),
    ]

    operations = [
        migrations.RunPython(update_category_slugs),
    ] 