from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="supportconversation",
            name="client_visible_from",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
