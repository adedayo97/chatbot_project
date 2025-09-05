from django.db import models
from django.utils import timezone
import uuid

class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)
    message = models.TextField()
    is_start = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Option(models.Model):
    keyword = models.CharField(max_length=100)
    from_node = models.ForeignKey(Node, related_name="options", on_delete=models.CASCADE)
    to_node = models.ForeignKey(Node, related_name="next_nodes", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.keyword} → {self.to_node.name}"

class UserInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    service = models.CharField(max_length=100)
    session_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    email_confirmed = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.email} - {self.service} - {'Verified' if self.is_verified else 'Pending'}"