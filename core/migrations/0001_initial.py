from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportConversation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_closed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_message_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="support_conversation", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Conversation support",
                "verbose_name_plural": "Conversations support",
                "ordering": ["-last_message_at"],
            },
        ),
        migrations.CreateModel(
            name="SupportMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.TextField()),
                ("is_staff", models.BooleanField(default=False)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="core.supportconversation")),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="support_messages", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Message support",
                "verbose_name_plural": "Messages support",
                "ordering": ["created_at"],
            },
        ),
    ]
