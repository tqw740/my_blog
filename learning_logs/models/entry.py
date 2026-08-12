from django.db import models
from .topic import Topic

class Entry(models.Model):
    """主题下的具体内容笔记"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='entries')
    text = models.TextField(verbose_name="笔记内容")
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text[:50]}..." if len(self.text) > 50 else self.text