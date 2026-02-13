from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0011_contract_tenant_contracttype_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateFile',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('tenant_id', models.UUIDField(null=True, blank=True, db_index=True)),
                ('filename', models.CharField(max_length=255, unique=True, db_index=True)),
                ('name', models.CharField(max_length=255)),
                ('contract_type', models.CharField(max_length=100, blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(max_length=20, choices=[('active', 'Active'), ('archived', 'Archived')], default='active')),
                ('content', models.TextField()),
                ('created_by_id', models.UUIDField(null=True, blank=True)),
                ('created_by_email', models.EmailField(null=True, blank=True, max_length=254)),
                ('signature_fields_config', models.JSONField(default=dict, blank=True)),
                ('signature_fields_updated_at', models.DateTimeField(null=True, blank=True)),
                ('signature_fields_updated_by_id', models.UUIDField(null=True, blank=True)),
                ('signature_fields_updated_by_email', models.EmailField(null=True, blank=True, max_length=254)),
                ('meta', models.JSONField(default=dict, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'template_files',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='templatefile',
            index=models.Index(fields=['tenant_id', 'updated_at'], name='tmpl_tenant_updated_idx'),
        ),
    ]
