from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
from ..models.entry import Entry

def search_view(request):
    query = request.GET.get('q', '').strip()
    
    entries = Entry.objects.select_related('topic', 'topic__owner')

    if query:
        entries = entries.annotate(
            similarity=Greatest(
                TrigramSimilarity('title', query) * 2.5,                  # 1. 命中笔记标题，权重最高
                TrigramSimilarity('topic__text', query) * 1.8,            # 2. 命中所属主题
                TrigramSimilarity('topic__owner__username', query) * 1.5,  # 3. 命中创建者名字
                TrigramSimilarity('text', query) * 1.0,                   # 4. 命中正文
            )
        ).filter(
            Q(similarity__gt=0.05) |
            Q(title__icontains=query) |
            Q(topic__text__icontains=query) |
            Q(topic__owner__username__icontains=query) |
            Q(text__icontains=query)
        ).order_by('-similarity', '-date_added').distinct()
    else:
        entries = Entry.objects.none()

    paginator = Paginator(entries, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'learning_logs/search_results.html', {
        'query': query,
        'page_obj': page_obj,
        'total_count': entries.count() if query else 0
    })