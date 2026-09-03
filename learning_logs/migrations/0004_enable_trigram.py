# learning_logs/migrations/xxxx_enable_trigram.py
from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    dependencies = [
        ('learning_logs', '0003_entry_word_count'), # 保留自动生成的依赖
    ]

    operations = [
        TrigramExtension(),  # 激活 PostgreSQL 的 pg_trgm 扩展
    ]