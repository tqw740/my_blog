from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from ..models import Entry
from .topic_views import _get_topic_by_path

@login_required
def add_entry(request, username, topic_path):
    """在指定 Topic 下增加 Entry"""
    if request.user.username != username:
        raise Http404("无权操作")

    _, topic = _get_topic_by_path(username, topic_path)

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Entry.objects.create(topic=topic, text=text)
            return redirect('learning_logs:topic_detail', username=username, topic_path=topic_path)

    return render(request, 'learning_logs/add_entry.html', {'topic': topic})


@login_required
def edit_entry(request, entry_id):
    """修改 Entry"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    
    if topic.owner != request.user:
        raise Http404("无权操作")

    if request.method == 'POST':
        entry.text = request.POST.get('text', entry.text)
        entry.save()
        return redirect('learning_logs:topic_detail', username=request.user.username, topic_path=topic.get_full_path())

    return render(request, 'learning_logs/edit_entry.html', {'entry': entry})


@login_required
def delete_entry(request, entry_id):
    """删除 Entry"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic

    if topic.owner != request.user:
        raise Http404("无权操作")

    if request.method == 'POST':
        entry.delete()
        return redirect('learning_logs:topic_detail', username=request.user.username, topic_path=topic.get_full_path())

    return render(request, 'learning_logs/delete_entry.html', {'entry': entry})