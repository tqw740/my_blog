from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.postgres.indexes import GinIndex  # 1. 引入 GIN 索引

class Topic(MPTTModel):
    """支持无限极分类的 Topic 模型"""
    text = models.CharField(max_length=200, verbose_name="主题名称")
    slug = models.SlugField(max_length=50, verbose_name="URL别名")

    # 树形父级关联
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="父级主题",
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")
    date_added = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ['text']

    class Meta:
        verbose_name = "主题"
        verbose_name_plural = "主题列表"
        # 原有的唯一性约束保留
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'parent', 'slug'],
                condition=models.Q(parent__isnull=False),
                name='unique_owner_parent_slug',
            ),
            models.UniqueConstraint(
                fields=['owner', 'slug'],
                condition=models.Q(parent__isnull=True),
                name='unique_owner_root_slug',
            )
        ]
        # 2. 追加 Trigram GIN 索引加速主题名称的搜索
        indexes = [
            GinIndex(
                fields=['text'], 
                name='topic_text_trgm_idx', 
                opclasses=['gin_trgm_ops']
            ),
        ]

    def get_full_path(self):
        """获取主题的完整路径"""
        ancestors = self.get_ancestors(include_self=True)
        return '/'.join([ancestor.slug for ancestor in ancestors])

    def __str__(self):
        return self.text