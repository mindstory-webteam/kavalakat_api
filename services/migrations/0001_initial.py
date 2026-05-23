from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [

        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name',        models.CharField(max_length=100, unique=True)),
                ('slug',        models.SlugField(blank=True, max_length=120, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon',        models.CharField(blank=True, max_length=100)),
                ('color',       models.CharField(blank=True, default='#0284f0', max_length=20)),
                ('order',       models.PositiveIntegerField(default=0)),
                ('is_active',   models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Service Category', 'verbose_name_plural': 'Service Categories', 'ordering': ['order', 'name']},
        ),

        migrations.CreateModel(
            name='Service',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category',    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services', to='services.servicecategory')),
                ('name',        models.CharField(max_length=255)),
                ('slug',        models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon',        models.CharField(blank=True, max_length=100)),
                ('image',       models.ImageField(blank=True, null=True, upload_to='services/list/')),
                ('is_active',   models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('order',       models.PositiveIntegerField(default=0)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Service', 'ordering': ['order', 'name']},
        ),

        migrations.CreateModel(
            name='ServiceAbout',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service',         models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='about', to='services.service')),
                ('main_title',      models.CharField(max_length=255)),
                ('sub_title',       models.CharField(blank=True, max_length=255)),
                ('description',     models.TextField(blank=True)),
                ('left_side_image', models.ImageField(blank=True, null=True, upload_to='services/about/')),
                ('gallery_image_1', models.ImageField(blank=True, null=True, upload_to='services/about/gallery/')),
                ('gallery_image_2', models.ImageField(blank=True, null=True, upload_to='services/about/gallery/')),
                ('gallery_image_3', models.ImageField(blank=True, null=True, upload_to='services/about/gallery/')),
                ('button_text',     models.CharField(blank=True, max_length=100)),
                ('button_link',     models.CharField(blank=True, max_length=500)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Service About Section'},
        ),

        migrations.CreateModel(
            name='ServiceCounter',
            fields=[
                ('id',                models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service',           models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='counters', to='services.service')),
                ('counter_title',     models.CharField(max_length=255)),
                ('counter_number',    models.CharField(max_length=50)),
                ('short_description', models.CharField(blank=True, max_length=255)),
                ('icon',              models.CharField(blank=True, max_length=100)),
                ('order',             models.PositiveIntegerField(default=0)),
                ('is_active',         models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Service Counter', 'ordering': ['order', 'counter_title']},
        ),

        migrations.CreateModel(
            name='ServiceOffer',
            fields=[
                ('id',                models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service',           models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='services.service')),
                ('offer_title',       models.CharField(max_length=255)),
                ('offer_icon',        models.CharField(blank=True, max_length=100)),
                ('short_description', models.CharField(blank=True, max_length=500)),
                ('order',             models.PositiveIntegerField(default=0)),
                ('is_active',         models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Service Offer', 'ordering': ['order', 'offer_title']},
        ),

        migrations.CreateModel(
            name='ServiceFeatureSection',
            fields=[
                ('id',               models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service',          models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feature_section', to='services.service')),
                ('section_title',    models.CharField(max_length=255)),
                ('left_main_image',  models.ImageField(blank=True, null=True, upload_to='services/features/')),
                ('main_description', models.TextField(blank=True)),
                ('updated_at',       models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Service Feature Section'},
        ),

        migrations.CreateModel(
            name='ServiceFeature',
            fields=[
                ('id',                  models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section',             models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='services.servicefeaturesection')),
                ('feature_title',       models.CharField(max_length=255)),
                ('feature_description', models.TextField(blank=True)),
                ('order',               models.PositiveIntegerField(default=0)),
            ],
            options={'verbose_name': 'Service Feature', 'ordering': ['order', 'feature_title']},
        ),

        migrations.CreateModel(
            name='ServiceHighlight',
            fields=[
                ('id',                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service',               models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='highlights', to='services.service')),
                ('section_title',         models.CharField(blank=True, max_length=255)),
                ('section_sub_title',     models.CharField(blank=True, max_length=255)),
                ('highlight_title',       models.CharField(max_length=255)),
                ('highlight_description', models.TextField(blank=True)),
                ('highlight_video',       models.FileField(blank=True, null=True, upload_to='services/videos/')),
                ('display_order',         models.PositiveIntegerField(default=0)),
                ('is_active',             models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Service Highlight', 'ordering': ['display_order', 'highlight_title']},
        ),

        migrations.CreateModel(
            name='ServiceLocation',
            fields=[
                ('id',                        models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service',                   models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='location', to='services.service')),
                ('location_main_title',       models.CharField(max_length=255)),
                ('location_main_sub_title',   models.CharField(blank=True, max_length=255)),
                ('location_main_description', models.TextField(blank=True)),
                ('left_main_image',           models.ImageField(blank=True, null=True, upload_to='services/location/')),
                ('updated_at',                models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Service Location Section'},
        ),

        migrations.CreateModel(
            name='ServiceNearbyPlace',
            fields=[
                ('id',                models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location',          models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nearby_places', to='services.servicelocation')),
                ('nearby_place_name', models.CharField(max_length=255)),
                ('distance',          models.CharField(blank=True, max_length=100)),
                ('map_link',          models.URLField(blank=True)),
                ('order',             models.PositiveIntegerField(default=0)),
            ],
            options={'verbose_name': 'Nearby Place', 'ordering': ['order', 'nearby_place_name']},
        ),
    ]
