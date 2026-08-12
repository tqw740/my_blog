from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from ..models import Topic
from ..utils import slugify_pinyin, validate_topic_text

def _get_topic_by_path(username, topic_path):
    """解析多级路径并找到对应的主题与用户实体"""
    slugs = [s for s in topic_path.split('/') if s]
    if not slugs:
        raise Http404("非法路径")

    user = get_object_or_404(User, username=username)

    # 查找根 Topic
    try:
        current_topic = Topic.objects.get(owner=user, parent=None, slug=slugs[0])
    except(Topic.DoesNotExist, Topic.MultipleObjectsReturned):
        raise Http404("未找到主题")

    for slug in slugs[1:]:
        try:
            current_topic = current_topic.children.get(slug=slug)
        except(Topic.DoesNotExist, Topic.MultipleObjectsReturned):
            raise Http404("未找到子主题")

    return user, current_topic

def slug_preview(request):
    """根据主题名称实时生成 URL 别名预览（供表单 AJAX 调用）"""
    text = request.GET.get('text', '')
    slug = slugify_pinyin(text) if validate_topic_text(text) else ''
    return JsonResponse({'slug': slug})

def user_root_topics(request, username):
    """显示用户的顶层主题"""
    # 获取用户实体
    user = get_object_or_404(User, username=username)
    # 获取用户根主题
    root_topics = Topic.objects.filter(owner=user, parent=None)
    # 将前端需要的数据列出
    context = {
        'target_user': user,
        'topics': root_topics,
    }
    # 指定模板渲染数据，并将刚刚打包的数据发送给前端对应的模板
    return render(request, 'learning_logs/user_root.html', context)

def topic_detail(request, username, topic_path):
    """显示 Topic 的详细信息"""
    user, topic = _get_topic_by_path(username, topic_path)
    subtopics = topic.get_children()
    entries = topic.entries.all().order_by('-date_added')
    ancestors = topic.get_ancestors(include_self=True)

    context = {
        'target_user': user,
        'topic': topic,
        'subtopics': subtopics,
        'entries':entries,
        'ancestors': ancestors,
    }

    return render(request, 'learning_logs/topic_detail.html', context)

@login_required
def add_topic(request, username, topic_path=None):
    """添加根主题或为主题添加子主题"""
    if request.user.username != username:
        raise Http404("您没有权限修改他人的主题")

    parent_topic = None
    # 有 topic_path，说明不是根主题，找到父主题
    if topic_path:
        _, parent_topic = _get_topic_by_path(username, topic_path)

    # 记录用户提交的数据，避免刷新表单时丢失
    submitted_text = ''
    error = None

    if request.method == 'POST':
        # 获取 text 来作为 topic 的名字，获取失败就留空
        text = request.POST.get('text', '').strip()
        submitted_text = text

        # 校验文本是否正常
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
                    owner=request.user,
                )
                # 重定向到新主题页面
                full_path = new_topic.get_full_path()
                return redirect('learning_logs:topic_detail', username=username, topic_path=full_path)

    context = {
        'parent_topic': parent_topic,
        'error': error,
        'submitted_text': submitted_text,
    }

    return render(request, 'learning_logs/add_topic.html', context)

@login_required
def edit_topic(request, username, topic_path):
    """修改用户的主题"""
    if request.user.username != username:
        raise Http404("您没有权限修改他人的主题")

    _, topic = _get_topic_by_path(username, topic_path)

    submitted_text = ''
    error = None

    if request.method == 'POST':
        # 获取 text 来作为 topic 的名字，获取失败就留空
        text = request.POST.get('text', '').strip()
        submitted_text = text

        # 校验文本是否正常
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
                full_path = topic.get_full_path()
                return redirect('learning_logs:topic_detail', username=username, topic_path=full_path)

    context = {
        'topic': topic,
        'error': error,
        'submitted_text': submitted_text,
    }

    return render(request, 'learning_logs/edit_topic.html', context)

@login_required
def delete_topic(request, username, topic_path):
    """删除用户的主题"""
    if request.user.username != username:
        raise Http404("您没有权限删除他人的主题")

    _, topic = _get_topic_by_path(username, topic_path)
    parent = topic.parent

    if request.method == 'POST':
        topic.delete()
        if parent:
            return redirect('learning_logs:topic_detail', username=username, topic_path=parent.get_full_path())
        return redirect('learning_logs:user_root', username=username)

    return render(request, 'learning_logs/delete_topic.html', {'topic': topic})
