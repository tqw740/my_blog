from django.db import models
from django.contrib.postgres.indexes import GinIndex  # 1. 引入 GIN 索引
from .topic import Topic

class Entry(models.Model):
    """主题下的具体内容笔记"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='entries')
    title = models.CharField(max_length=200, verbose_name="文章标题")
    text = models.TextField(verbose_name="笔记内容")
    date_added = models.DateTimeField(auto_now_add=True)
    word_count = models.IntegerField(default=0, verbose_name="字数统计")

    # 2. 增加 Meta 类与索引
    class Meta:
        verbose_name = "笔记"
        verbose_name_plural = "笔记列表"
        indexes = [
            # 为文章标题加速
            GinIndex(
                fields=['title'], 
                name='entry_title_trgm_idx', 
                opclasses=['gin_trgm_ops']
            ),
            # 为文章正文加速
            GinIndex(
                fields=['text'], 
                name='entry_text_trgm_idx', 
                opclasses=['gin_trgm_ops']
            ),
        ]

    def __str__(self):
        return self.title if self.title else f"{self.text[:50]}..."