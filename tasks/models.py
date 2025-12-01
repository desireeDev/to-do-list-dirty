from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    priority = models.BooleanField(default=False, verbose_name="Prioritaire")

    def __str__(self):
        return self.title
    
class Meta:
        ordering = ['-priority', '-created']  # Tri par priorité puis date