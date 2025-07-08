from django.shortcuts import render
from django.core.paginator import Paginator

from myclickhouse_client.clickhouse import get_clickhouse_client

import math

def laion_list(request):
    try:
        client = get_clickhouse_client()
        page = int(request.GET.get('page', 1))
        per_page = 20
        offset = (page - 1) * per_page
        
        result = client.query(f"SELECT id, url, caption FROM laion LIMIT {per_page} OFFSET {offset}")
        rows = result.result_rows
        
        count_result = client.query("SELECT COUNT(*) FROM laion")
        total_count = count_result.result_rows[0][0]
        
        total_pages = math.ceil(total_count / per_page)
        has_previous = page > 1
        has_next = page < total_pages
        
        context = {
            "images": rows,
            "page": page,
            "total_pages": total_pages,
            "has_previous": has_previous,
            "has_next": has_next,
            "previous_page": page - 1 if has_previous else None,
            "next_page": page + 1 if has_next else None,
            "total_count": total_count,
            "per_page": per_page
        }
        return render(request, 'hw04/laion_list.html', context)
    
    except Exception as e:
        context = {
            "images": [],
            "error": str(e)
        }
        return render(request, 'hw04/laion_list.html', context)