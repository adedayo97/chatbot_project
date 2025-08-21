from django.db import models

class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)   # e.g. greeting
    message = models.TextField()                           # Bot response text
    is_start = models.BooleanField(default=False)          # Mark as starting node

    def __str__(self):
        return self.name

class Option(models.Model):
    keyword = models.CharField(max_length=100)             # e.g. "yes"
    from_node = models.ForeignKey(Node, related_name="options", on_delete=models.CASCADE)
    to_node = models.ForeignKey(Node, related_name="next_nodes", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.keyword} → {self.to_node.name}"