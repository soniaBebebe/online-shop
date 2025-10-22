from django.db import migrations

def create_group(apps, schema_editor):
    Group=apps.get_model('auth', 'Group')
    Permission=apps.get_model('auth', 'Permission')
    ContentType=apps.get_model('contenttypes', 'ContentType')
    Product = apps.get_model('shop', 'Product')
    Category = apps.get_model('shop', 'Category')

    group, _ =Group.objects.get_or_create(name='catalog_admin')

    product_ct=ContentType.objects.get_for_model(Product)
    category_ct=ContentType.objects.get_for_model(Category)

    perms=Permission.objects.filter(
        content_type__in=[product_ct, category_ct],
        codename__in=['add_product', 'change_product', 'add_category', 'change_category']
    )
    group.permissions.add(*perms)

def delete_group(apps, schema_editor):
    Group=apps.get_model('auth', 'Group')
    Group.objects.filter(name='catalog_admin').delete()

class Migration(migrations.Migration):
    dependencies=[
        ('shop', '0002_product_description'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]
    operations=[
        migrations.RunPython(create_group, delete_group),
    ]