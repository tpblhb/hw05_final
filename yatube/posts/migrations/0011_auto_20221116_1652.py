# Generated by Django 2.2.16 on 2022-11-16 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20221114_2158'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'default_related_name': 'comments', 'ordering': ('-modified',), 'verbose_name': 'комментарий'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'default_related_name': 'posts', 'ordering': ('-modified',), 'verbose_name': 'пост', 'verbose_name_plural': 'посты'},
        ),
    ]