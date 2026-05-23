from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='FontAwesome class e.g. fa-solid fa-building', max_length=100)),
                ('color', models.CharField(blank=True, default='#0284f0', help_text='Hex color for badge e.g. #f97316', max_length=20)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Service Category', 'verbose_name_plural': 'Service Categories', 'ordering': ['order', 'name']},
        ),
        migrations.AddField(
            model_name='service',
            name='category',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='services',
                to='services.servicecategory',
            ),
        ),
    ]
