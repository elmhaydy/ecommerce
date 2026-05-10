from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_supportconversation_client_visible_from"),
    ]

    operations = [
        migrations.AddField(
            model_name="supportmessage",
            name="delivered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="supportmessage",
            name="read_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
