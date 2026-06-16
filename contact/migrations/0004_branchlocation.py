from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0003_alter_enquiry_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='BranchLocation',
            fields=[
                ('id',           models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name',         models.CharField(help_text='Branch name e.g. Head Office, Thrissur Branch', max_length=255)),
                ('address',      models.TextField()),
                ('phone',        models.CharField(max_length=20)),
                ('alt_phone',    models.CharField(blank=True, max_length=20)),
                ('email',        models.EmailField()),
                ('alt_email',    models.EmailField(blank=True)),
                ('map_link',     models.URLField(blank=True, help_text='Google Maps link')),
                ('map_embed_url',models.URLField(blank=True, help_text='Google Maps embed URL for iframe')),
                ('image',        models.ImageField(blank=True, help_text='Location image / photo of the branch', null=True, upload_to='contact/branches/')),
                ('city',         models.CharField(blank=True, max_length=100)),
                ('state',        models.CharField(blank=True, max_length=100)),
                ('pincode',      models.CharField(blank=True, max_length=10)),
                ('is_main',      models.BooleanField(default=False, help_text='Mark as main/head office')),
                ('is_active',    models.BooleanField(default=True)),
                ('order',        models.PositiveIntegerField(default=0)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
                ('updated_at',   models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name':        'Branch Location',
                'verbose_name_plural': 'Branch Locations',
                'ordering':            ['order', 'name'],
            },
        ),
    ]
