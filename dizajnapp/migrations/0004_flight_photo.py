# Generated by Django 4.2.1 on 2023-06-04 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dizajnapp', '0003_remove_flight_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='photo',
            field=models.ImageField(default='https://previews.123rf.com/images/koufax73/koufax731506/koufax73150600053/41047910-small-beach-in-the-woods-hdr-horizontal-imaga.jpg', upload_to='flights/'),
            preserve_default=False,
        ),
    ]
