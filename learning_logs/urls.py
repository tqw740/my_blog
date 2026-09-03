from django.urls import path
from .views import topic_views, entry_views, index, search_views
from .views.R2_views import get_upload_presigned_url

app_name = 'learning_logs'

urlpatterns = [
    path('', index.index, name='index'),
    path('entries/', index.entries, name='entries'),
    # URL 别名实时预览接口（必须放在 <str:username> 路由之前）
    path('slug-preview/', topic_views.slug_preview, name='slug_preview'),

    # 3. 图床相关路由
    path('api/upload-presigned-url/', get_upload_presigned_url, name='get_upload_presigned_url'),

    path('search/', search_views.search_view, name='search'),

    # 2. Entry 相关路由（放在最前面，避免被 <str:username> 路由误匹配）
    path('entry/<int:entry_id>/edit/', entry_views.edit_entry, name='edit_entry'),
    path('entry/<int:entry_id>/delete/', entry_views.delete_entry, name='delete_entry'),
    path('entry/<int:entry_id>/', entry_views.entry_detail, name='entry_detail'),

    # 1. Topic 相关路由
    # 用户根目录列表：/username/
    path('<str:username>/', topic_views.user_root_topics, name='user_root'),
    
    # 创建顶级 Topic：/username/add_topic/
    path('<str:username>/add_topic/', topic_views.add_topic, name='add_topic'),
    
    # 给特定 Topic 添加子 Topic：/username/python/django/add_subtopic/
    path('<str:username>/<path:topic_path>/add_subtopic/', topic_views.add_topic, name='add_subtopic'),
    
    # 修改/删除 Topic
    path('<str:username>/<path:topic_path>/edit/', topic_views.edit_topic, name='edit_topic'),
    path('<str:username>/<path:topic_path>/delete/', topic_views.delete_topic, name='delete_topic'),
    path('<str:username>/<path:topic_path>/add_entry/', entry_views.add_entry, name='add_entry'),

    # 动态匹配多级 Topic 路径：/username/python/django/
    # 注意：必须放在所有具体动作路由之后，否则会吞掉上面的路由
    path('<str:username>/<path:topic_path>/', topic_views.topic_detail, name='topic_detail'),
]