from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from ..models import Entry
from .topic_views import _get_topic_by_path

def entry_detail(request, entry_id):
    """显示条目的详细内容"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic

    context = {
        'entry': entry,
        'topic': topic,
    }
    return render(request, 'learning_logs/entry_detail.html', context)

@login_required
def add_entry(request, username, topic_path):
    """在用户主题下新增条目"""
    if request.user.username != username:
        raise Http404("您没有权限在该主题中新增条目")

    _, topic = _get_topic_by_path(username, topic_path)

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        text = (request.POST.get('text') or '').strip()
        if title and text:
            Entry.objects.create(title=title, text=text, topic=topic)
            return redirect('learning_logs:topic_detail', username=username, topic_path=topic_path)

    context = {
        'topic': topic,
    }

    return render(request, 'learning_logs/add_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """修改主题下的条目"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic

    if request.user != topic.owner:
        raise Http404("您没有权限在该主题中修改条目")

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        text = (request.POST.get('text') or '').strip()

        if title:
            entry.title = title
        if text:
            entry.text = text

        entry.save()
        username = request.user.username
        topic_path = topic.get_full_path()
        return redirect('learning_logs:topic_detail', username=username, topic_path = topic_path)

    context = {
        'entry': entry,
    }

    return render(request, 'learning_logs/edit_entry.html', context)

@login_required
def delete_entry(request, entry_id):
    """删除用户主题下的条目"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic

    if request.user != topic.owner:
        raise Http404("您没有权限在该主题中删除条目")

    if request.method == 'POST':
        entry.delete()
        return redirect('learning_logs:topic_detail', username=request.user.username, topic_path=topic.get_full_path())

    return render(request, 'learning_logs/delete_entry.html', {'entry': entry})