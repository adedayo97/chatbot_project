from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"

# Create user profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Save user profile when user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        # Create profile if it doesn't exist
        UserProfile.objects.create(user=instance)

# Your existing models
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