from django.shortcuts import render
def index(request):
    template_data = {}
    template_data['title'] = 'Movies Store'
    return render(request, 'home/index.html', {
        'template_data': template_data
    })

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {
        'template_data': template_data
    })


def local_popularity_map(request):
    """Render the local popularity map page.

    Aggregates purchase counts per region from cart.Item and sends
    a small JSON-friendly structure to the template where JS will
    render pins and popups.
    """
    from cart.models import Item, REGION_CHOICES
    from django.db.models import Sum

    # Aggregate top movies per region (top 3)
    region_codes = [code for code, _ in REGION_CHOICES]
    data = {}
    for code, display in REGION_CHOICES:
        # Count purchases grouped by movie for this region
        qs = (
            Item.objects.filter(location=code)
            .values('movie__id', 'movie__name', 'movie__image')
            .annotate(bought=Sum('quantity'))
            .order_by('-bought')[:3]
        )

        # Build image URLs server-side so templates/JS don't need MEDIA_URL context
        top_list = []
        from django.conf import settings
        for entry in list(qs):
            img_path = entry.get('movie__image') or ''
            if img_path:
                # build absolute URL so the browser can load images reliably
                entry['movie__image_url'] = request.build_absolute_uri(settings.MEDIA_URL + img_path)
            else:
                entry['movie__image_url'] = ''
            top_list.append(entry)

        data[code] = {
            'region_name': display,
            'top': top_list
        }

    template_data = {'title': 'Local Popularity Map', 'popularity_data': data}
    return render(request, 'home/map.html', {'template_data': template_data})


def popularity_api(request):
    """Return the same aggregated popularity data as JSON."""
    from cart.models import Item, REGION_CHOICES
    from django.db.models import Sum
    from django.http import JsonResponse

    data = {}
    for code, display in REGION_CHOICES:
        qs = (
            Item.objects.filter(location=code)
            .values('movie__id', 'movie__name')
            .annotate(bought=Sum('quantity'))
            .order_by('-bought')[:3]
        )
        data[code] = {
            'region_name': display,
            'top': list(qs)
        }

    return JsonResponse({'popularity_data': data})


def user_purchases_api(request):
    """Return the current user's aggregated purchases as JSON.

    Requires authentication; returns mapping movie_id -> total_quantity.
    """
    from django.http import JsonResponse
    from django.db.models import Sum
    from cart.models import Item

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required'}, status=401)

    qs = (
        Item.objects.filter(order__user=request.user)
        .values('movie__id')
        .annotate(total=Sum('quantity'))
    )
    result = {entry['movie__id']: entry['total'] for entry in qs}
    return JsonResponse({'user_purchases': result})