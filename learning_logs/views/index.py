from django.shortcuts import render
from ..models import Entry

def index(request):
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')

def entries(request):
    """展示全站最新的帖子"""
    latest_entries = Entry.objects.select_related('topic__owner')\
        .defer('text')\
        .order_by('-date_added')[:10]

    context = {
        'latest_entries': latest_entries,
    }

    return render(request, 'learning_logs/entries.html', context)