from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey

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

    # 标题按照文本进行排序
    class MPTTMeta:
        order_insertion_by = ['text']

    class Meta:
        constraints = [
            # 1. 有父节点时：owner + parent + slug 唯一
            models.UniqueConstraint(
                fields=['owner', 'parent', 'slug'],
                condition=models.Q(parent__isnull=False),
                name='unique_owner_parent_slug',
            ),
            # 2. 没有父节点时：owner + slug 唯一
            models.UniqueConstraint(
                fields=['owner', 'slug'],
                condition=models.Q(parent__isnull=True),
                name='unique_owner_root_slug',
            )
        ]
    def get_full_path(self):
        """获取主题的完整路径"""
        ancestors = self.get_ancestors(include_self=True)
        return '/'.join([ancestor.slug for ancestor in ancestors])

    def __str__(self):
        return self.text
