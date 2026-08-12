from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from ..models import Topic
from ..utils import slugify_pinyin, validate_topic_text

def _get_topic_by_path(username, topic_path):
    """辅助函数：解析多级 path 并查找对应的 Topic"""
    slugs = [s for s in topic_path.split('/') if s]
    if not slugs:
        raise Http404("Invalid path")

    user = get_object_or_404(User, username=username)
    
    # 查找根 Topic
    try:
        current_topic = Topic.objects.get(owner=user, parent=None, slug=slugs[0])
    except (Topic.DoesNotExist, Topic.MultipleObjectsReturned):
        raise Http404("Topic not found")

    # 逐级往下查找子 Topic
    for slug in slugs[1:]:
        try:
            current_topic = current_topic.children.get(slug=slug)
        except (Topic.DoesNotExist, Topic.MultipleObjectsReturned):
            raise Http404("Subtopic not found")

    return user, current_topic


def slug_preview(request):
    """根据主题名称实时生成 URL 别名预览（供表单 AJAX 调用）"""
    text = request.GET.get('text', '')
    slug = slugify_pinyin(text) if validate_topic_text(text) else ''
    return JsonResponse({'slug': slug})


def user_root_topics(request, username):
    """显示用户的顶级 Topics"""
    user = get_object_or_404(User, username=username)
    root_topics = Topic.objects.filter(owner=user, parent=None)
    return render(request, 'learning_logs/user_root.html', {'target_user': user, 'topics': root_topics})


def topic_detail(request, username, topic_path):
    """显示 Topic 详情：同时展示子 Topic 列表和属于自己的 Entry 列表"""
    user, topic = _get_topic_by_path(username, topic_path)
    
    subtopics = topic.get_children()  # 获取直接子 Topic
    entries = topic.entries.all().order_by('-date_added')  # 获取当前 Topic 的条目

    context = {
        'target_user': user,
        'topic': topic,
        'subtopics': subtopics,
        'entries': entries,
        'ancestors': topic.get_ancestors(include_self=True),  # 用于面包屑导航
    }
    return render(request, 'learning_logs/topic_detail.html', context)


@login_required
def add_topic(request, username, topic_path=None):
    """添加 Topic（如果是根目录添加则 topic_path 为 None，否则作为子 Topic 添加）

    URL 别名由系统根据主题名称自动生成（汉字转拼音、空格转连词符），
    若生成的 URL 与已有主题重复则拒绝创建。
    """
    if request.user.username != username:
        raise Http404("无权操作")

    parent_topic = None
    if topic_path:
        _, parent_topic = _get_topic_by_path(username, topic_path)

    error = None
    submitted_text = ''

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        submitted_text = text

        if not validate_topic_text(text):
            error = "主题名称只能包含汉字、大小写字母、连词符、空格和数字。"
        else:
            slug = slugify_pinyin(text)
            if not slug:
                error = "无法根据主题名称生成 URL 别名，请更换主题名称。"
            elif Topic.objects.filter(owner=request.user, parent=parent_topic, slug=slug).exists():
                error = f"URL 别名「{slug}」已存在，请更换主题名称。"
            else:
                new_topic = Topic.objects.create(
                    text=text,
                    slug=slug,
                    parent=parent_topic,
                    owner=request.user
                )
                # 重定向到新创建的 Topic 页面
                full_path = new_topic.get_full_path()
                return redirect('learning_logs:topic_detail', username=username, topic_path=full_path)

    return render(request, 'learning_logs/add_topic.html', {
        'parent_topic': parent_topic,
        'error': error,
        'submitted_text': submitted_text,
    })


@login_required
def edit_topic(request, username, topic_path):
    """修改 Topic：URL 别名随主题名称自动重新生成，若与其它主题重复则拒绝保存。"""
    if request.user.username != username:
        raise Http404("无权操作")
        
    _, topic = _get_topic_by_path(username, topic_path)

    error = None
    submitted_text = ''

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        submitted_text = text

        if not validate_topic_text(text):
            error = "主题名称只能包含汉字、大小写字母、连词符、空格和数字。"
        else:
            slug = slugify_pinyin(text)
            slug_duplicated = Topic.objects.filter(
                owner=request.user, parent=topic.parent, slug=slug
            ).exclude(pk=topic.pk).exists()

            if not slug:
                error = "无法根据主题名称生成 URL 别名，请更换主题名称。"
            elif slug_duplicated:
                error = f"URL 别名「{slug}」已存在，请更换主题名称。"
            else:
                topic.text = text
                topic.slug = slug
                topic.save()
                return redirect('learning_logs:topic_detail', username=username, topic_path=topic.get_full_path())

    return render(request, 'learning_logs/edit_topic.html', {
        'topic': topic,
        'error': error,
        'submitted_text': submitted_text,
    })


@login_required
def delete_topic(request, username, topic_path):
    """删除 Topic 及其子项"""
    if request.user.username != username:
        raise Http404("无权操作")

    _, topic = _get_topic_by_path(username, topic_path)
    parent = topic.parent

    if request.method == 'POST':
        topic.delete()
        if parent:
            return redirect('learning_logs:topic_detail', username=username, topic_path=parent.get_full_path())
        return redirect('learning_logs:user_root', username=username)

    return render(request, 'learning_logs/delete_topic.html', {'topic': topic})