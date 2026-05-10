from django.conf import settings
from django.db import models


class SupportConversation(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_conversation",
    )
    is_closed = models.BooleanField(default=False)
    client_visible_from = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_message_at"]
        verbose_name = "Conversation support"
        verbose_name_plural = "Conversations support"

    def __str__(self):
        return f"Support #{self.pk} - {self.user.username}"

    @property
    def unread_for_client(self):
        return self.messages.filter(is_staff=True, is_read=False).count()

    @property
    def unread_for_support(self):
        return self.messages.filter(is_staff=False, is_read=False).count()


class SupportMessage(models.Model):
    conversation = models.ForeignKey(
        SupportConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_messages",
    )
    body = models.TextField()
    is_staff = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Message support"
        verbose_name_plural = "Messages support"

    def __str__(self):
        role = "Support" if self.is_staff else "Client"
        return f"{role} message #{self.pk}"
