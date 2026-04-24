import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator


def staff_required(fn):
    return user_passes_test(lambda u: u.is_active and u.is_staff, login_url='/dashboard/login/')(fn)


# ── AUTH ──────────────────────────────────────────────────────────────────────
def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username',''), password=request.POST.get('password',''))
        if user and user.is_staff:
            login(request, user)
            return redirect(request.GET.get('next', '/dashboard/'))
        messages.error(request, 'Invalid credentials or insufficient permissions.')
    return render(request, 'dashboard/login.html')


def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:login')


# ── HOME ──────────────────────────────────────────────────────────────────────
@staff_required
def dashboard_home(request):
    from blog.models import Post
    from contact.models import Enquiry, Career
    from portfolio.models import Item
    from pages.models import Page

    stats = {
        'total_posts':     Post.objects.count(),
        'published_posts': Post.objects.filter(status='published').count(),
        'draft_posts':     Post.objects.filter(status='draft').count(),
        'total_enquiries': Enquiry.objects.count(),
        'new_enquiries':   Enquiry.objects.filter(status='new').count(),
        'active_careers':  Career.objects.filter(is_active=True).count(),
        'portfolio_items': Item.objects.count(),
        'active_pages':    Page.objects.filter(is_active=True).count(),
    }
    recent_enquiries = Enquiry.objects.order_by('-created_at')[:5]
    recent_posts     = Post.objects.select_related('category').order_by('-created_at')[:5]

    from django.db.models.functions import TruncMonth
    monthly = (
        Enquiry.objects
        .filter(created_at__gte=timezone.now() - timezone.timedelta(days=180))
        .annotate(month=TruncMonth('created_at'))
        .values('month').annotate(count=Count('id')).order_by('month')
    )
    chart_labels = [m['month'].strftime('%b %Y') for m in monthly]
    chart_data   = [m['count'] for m in monthly]
    post_status  = {
        'published': Post.objects.filter(status='published').count(),
        'draft':     Post.objects.filter(status='draft').count(),
        'archived':  Post.objects.filter(status='archived').count(),
    }
    return render(request, 'dashboard/home.html', {
        'stats': stats, 'recent_enquiries': recent_enquiries, 'recent_posts': recent_posts,
        'chart_labels': json.dumps(chart_labels), 'chart_data': json.dumps(chart_data),
        'post_status': json.dumps(post_status), 'page_title': 'Dashboard',
    })


# ── PAGES ─────────────────────────────────────────────────────────────────────
@staff_required
def pages_list(request):
    from pages.models import Page
    search = request.GET.get('search', '')
    qs = Page.objects.all()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
    pages = Paginator(qs.order_by('order','title'), 10).get_page(request.GET.get('page'))
    return render(request, 'dashboard/pages/list.html', {'pages': pages, 'search': search, 'page_title': 'Pages'})


@staff_required
def pages_create(request):
    from pages.models import Page
    from django.utils.text import slugify
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        if not title:
            messages.error(request, 'Title is required.')
        else:
            Page.objects.create(
                title=title, slug=slugify(title),
                content=request.POST.get('content',''),
                meta_title=request.POST.get('meta_title',''),
                meta_description=request.POST.get('meta_description',''),
                is_active=request.POST.get('is_active') == 'on',
                order=int(request.POST.get('order',0) or 0),
                banner_image=request.FILES.get('banner_image'),
            )
            messages.success(request, 'Page created.')
            return redirect('dashboard:pages_list')
    return render(request, 'dashboard/pages/form.html', {'page_title': 'Create Page', 'obj': None})


@staff_required
def pages_edit(request, pk):
    from pages.models import Page
    obj = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        obj.title = request.POST.get('title', obj.title).strip()
        obj.content = request.POST.get('content', '')
        obj.meta_title = request.POST.get('meta_title', '')
        obj.meta_description = request.POST.get('meta_description', '')
        obj.is_active = request.POST.get('is_active') == 'on'
        obj.order = int(request.POST.get('order', 0) or 0)
        if request.FILES.get('banner_image'):
            obj.banner_image = request.FILES['banner_image']
        obj.save()
        messages.success(request, 'Page updated.')
        return redirect('dashboard:pages_list')
    return render(request, 'dashboard/pages/form.html', {'page_title': 'Edit Page', 'obj': obj})


@staff_required
def pages_delete(request, pk):
    from pages.models import Page
    obj = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, 'Page deleted.')
        return redirect('dashboard:pages_list')
    return render(request, 'dashboard/confirm_delete.html', {'obj': obj, 'page_title': 'Delete Page'})


# ── BLOG ──────────────────────────────────────────────────────────────────────
@staff_required
def blog_list(request):
    from blog.models import Post, Category
    search = request.GET.get('search',''); status = request.GET.get('status',''); cat = request.GET.get('category','')
    qs = Post.objects.select_related('category','author').all()
    if search: qs = qs.filter(Q(title__icontains=search)|Q(content__icontains=search))
    if status: qs = qs.filter(status=status)
    if cat:    qs = qs.filter(category_id=cat)
    posts = Paginator(qs.order_by('-created_at'), 10).get_page(request.GET.get('page'))
    return render(request, 'dashboard/blog/list.html', {
        'posts': posts, 'search': search, 'status': status,
        'categories': Category.objects.all(), 'page_title': 'Blog Posts',
    })


@staff_required
def blog_create(request):
    from blog.models import Post, Category
    from django.utils.text import slugify
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        if not title:
            messages.error(request, 'Title is required.')
        else:
            base = slugify(title); slug = base; n = 1
            while Post.objects.filter(slug=slug).exists(): slug = f'{base}-{n}'; n += 1
            post = Post.objects.create(
                title=title, slug=slug,
                content=request.POST.get('content',''),
                excerpt=request.POST.get('excerpt',''),
                status=request.POST.get('status','draft'),
                tags=request.POST.get('tags',''),
                meta_title=request.POST.get('meta_title',''),
                meta_description=request.POST.get('meta_description',''),
                is_featured=request.POST.get('is_featured') == 'on',
                author=request.user,
                category_id=request.POST.get('category') or None,
                image=request.FILES.get('image'),
            )
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
                post.save(update_fields=['published_at'])
            messages.success(request, 'Post created.')
            return redirect('dashboard:blog_list')
    return render(request, 'dashboard/blog/form.html', {
        'categories': Category.objects.all(), 'page_title': 'Create Post', 'obj': None,
    })


@staff_required
def blog_edit(request, pk):
    from blog.models import Post, Category
    obj = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        obj.title = request.POST.get('title', obj.title).strip()
        obj.content = request.POST.get('content', '')
        obj.excerpt = request.POST.get('excerpt', '')
        obj.status  = request.POST.get('status', obj.status)
        obj.tags    = request.POST.get('tags', '')
        obj.meta_title = request.POST.get('meta_title', '')
        obj.meta_description = request.POST.get('meta_description', '')
        obj.is_featured = request.POST.get('is_featured') == 'on'
        obj.category_id = request.POST.get('category') or None
        if request.FILES.get('image'): obj.image = request.FILES['image']
        if obj.status == 'published' and not obj.published_at: obj.published_at = timezone.now()
        obj.save()
        messages.success(request, 'Post updated.')
        return redirect('dashboard:blog_list')
    return render(request, 'dashboard/blog/form.html', {
        'categories': Category.objects.all(), 'page_title': 'Edit Post', 'obj': obj,
    })


@staff_required
def blog_delete(request, pk):
    from blog.models import Post
    obj = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, 'Post deleted.')
        return redirect('dashboard:blog_list')
    return render(request, 'dashboard/confirm_delete.html', {'obj': obj, 'page_title': 'Delete Post'})


@staff_required
def blog_categories(request):
    from blog.models import Category
    cats = Category.objects.annotate(post_count=Count('posts')).order_by('order','name')
    return render(request, 'dashboard/blog/categories.html', {'categories': cats, 'page_title': 'Blog Categories'})


@staff_required
def blog_cat_create(request):
    from blog.models import Category
    from django.utils.text import slugify
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        if name:
            Category.objects.create(name=name, slug=slugify(name),
                description=request.POST.get('description',''),
                order=int(request.POST.get('order',0) or 0))
            messages.success(request, 'Category created.')
        return redirect('dashboard:blog_categories')
    return render(request, 'dashboard/blog/category_form.html', {'page_title': 'Create Category', 'obj': None})


@staff_required
def blog_cat_edit(request, pk):
    from blog.models import Category
    obj = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        obj.name = request.POST.get('name', obj.name).strip()
        obj.description = request.POST.get('description','')
        obj.order = int(request.POST.get('order',0) or 0)
        obj.save(); messages.success(request, 'Category updated.')
        return redirect('dashboard:blog_categories')
    return render(request, 'dashboard/blog/category_form.html', {'page_title': 'Edit Category', 'obj': obj})


@staff_required
def blog_cat_delete(request, pk):
    from blog.models import Category
    obj = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, 'Category deleted.')
        return redirect('dashboard:blog_categories')
    return render(request, 'dashboard/confirm_delete.html', {'obj': obj, 'page_title': 'Delete Category'})


# ── ENQUIRIES ─────────────────────────────────────────────────────────────────
@staff_required
def enquiry_list(request):
    from contact.models import Enquiry
    status = request.GET.get('status',''); search = request.GET.get('search','')
    qs = Enquiry.objects.all()
    if status: qs = qs.filter(status=status)
    if search: qs = qs.filter(Q(name__icontains=search)|Q(email__icontains=search)|Q(message__icontains=search))
    enquiries = Paginator(qs.order_by('-created_at'), 15).get_page(request.GET.get('page'))
    counts = {s: Enquiry.objects.filter(status=s).count() for s in ['new','read','replied','closed']}
    counts['all'] = Enquiry.objects.count()
    return render(request, 'dashboard/enquiries/list.html', {
        'enquiries': enquiries, 'status': status, 'search': search,
        'counts': counts, 'page_title': 'Enquiries',
    })


@staff_required
def enquiry_detail(request, pk):
    from contact.models import Enquiry
    obj = get_object_or_404(Enquiry, pk=pk)
    if obj.status == 'new': obj.status = 'read'; obj.save(update_fields=['status'])
    if request.method == 'POST':
        obj.status = request.POST.get('status', obj.status)
        obj.admin_note = request.POST.get('admin_note','')
        obj.save(); messages.success(request, 'Enquiry updated.')
        return redirect('dashboard:enquiry_detail', pk=pk)
    return render(request, 'dashboard/enquiries/detail.html', {'obj': obj, 'page_title': 'Enquiry Detail'})


@staff_required
def enquiry_delete(request, pk):
    from contact.models import Enquiry
    obj = get_object_or_404(Enquiry, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, 'Enquiry deleted.')
        return redirect('dashboard:enquiry_list')
    return render(request, 'dashboard/confirm_delete.html', {'obj': obj, 'page_title': 'Delete Enquiry'})


# ── PORTFOLIO ─────────────────────────────────────────────────────────────────
@staff_required
def portfolio_list(request):
    from portfolio.models import Category, Item
    search        = request.GET.get('search', '').strip()
    selected_cat  = request.GET.get('cat', '')
    active_filter = request.GET.get('active', '')

    qs = Item.objects.select_related('category').all()
    if search:
        qs = qs.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__icontains=search) |
            Q(category__name__icontains=search)
        )
    if selected_cat:
        qs = qs.filter(category_id=selected_cat)
    if active_filter == '1':
        qs = qs.filter(is_active=True)
    elif active_filter == '0':
        qs = qs.filter(is_active=False)

    qs    = qs.order_by('category__order', 'order', 'name')
    items = Paginator(qs, 20).get_page(request.GET.get('page'))

    categories = (
        Category.objects
        .prefetch_related('items')
        .annotate(item_count=Count('items'))
        .order_by('order', 'name')
    )

    return render(request, 'dashboard/portfolio/list.html', {
        'categories':    categories,
        'items':         items,
        'search':        search,
        'selected_cat':  selected_cat,
        'active_filter': active_filter,
        'page_title':    'Portfolio',
    })


@staff_required
def portfolio_create(request):
    from portfolio.models import Category, Item

    # Support both ?cat= (from column + button) and ?category= (legacy)
    preselected_cat = request.GET.get('cat', '') or request.GET.get('category', '')

    categories = (
        Category.objects
        .annotate(item_count=Count('items'))
        .prefetch_related('items')
        .order_by('order', 'name')
    )

    if request.method == 'POST':
        name   = request.POST.get('name', '').strip().upper()
        cat_id = request.POST.get('category', '').strip()

        if not name:
            messages.error(request, 'Item name is required.')
        elif not cat_id:
            messages.error(request, 'Please select a category (Trading, Distribution or Services).')
        else:
            try:
                Item.objects.create(
                    name=name,
                    description=request.POST.get('description', ''),
                    tags=request.POST.get('tags', ''),
                    category_id=int(cat_id),
                    is_featured=request.POST.get('is_featured') == 'on',
                    is_active=request.POST.get('is_active') == 'on',
                    order=int(request.POST.get('order', 0) or 0),
                    image=request.FILES.get('image'),
                )
                messages.success(request, f'Item "{name}" created successfully.')
                return redirect('dashboard:portfolio_list')
            except Exception as e:
                messages.error(request, f'Error creating item: {e}')

    return render(request, 'dashboard/portfolio/form.html', {
        'categories':     categories,
        'page_title':     'Add Portfolio Item',
        'obj':            None,
        'preselected_cat': preselected_cat,
    })


@staff_required
def portfolio_edit(request, pk):
    from portfolio.models import Category, Item
    obj = get_object_or_404(Item, pk=pk)

    categories = (
        Category.objects
        .annotate(item_count=Count('items'))
        .prefetch_related('items')
        .order_by('order', 'name')
    )

    if request.method == 'POST':
        name   = request.POST.get('name', obj.name).strip().upper()
        cat_id = request.POST.get('category', '').strip()

        if not name:
            messages.error(request, 'Item name is required.')
        elif not cat_id:
            messages.error(request, 'Please select a category.')
        else:
            obj.name        = name
            obj.description = request.POST.get('description', '')
            obj.tags        = request.POST.get('tags', '')
            obj.category_id = int(cat_id)
            obj.is_featured = request.POST.get('is_featured') == 'on'
            obj.is_active   = request.POST.get('is_active') == 'on'
            obj.order       = int(request.POST.get('order', 0) or 0)
            if request.FILES.get('image'):
                obj.image = request.FILES['image']
            obj.save()
            messages.success(request, f'Item "{obj.name}" updated.')
            return redirect('dashboard:portfolio_list')

    return render(request, 'dashboard/portfolio/form.html', {
        'categories':     categories,
        'page_title':     f'Edit — {obj.name}',
        'obj':            obj,
        'preselected_cat': str(obj.category_id),
    })


@staff_required
def portfolio_delete(request, pk):
    from portfolio.models import Item
    obj = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f'Item "{name}" deleted.')
        return redirect('dashboard:portfolio_list')
    return render(request, 'dashboard/confirm_delete.html', {
        'obj': obj, 'page_title': f'Delete — {obj.name}'
    })


# ── CAREERS ───────────────────────────────────────────────────────────────────
@staff_required
def careers_list(request):
    from contact.models import Career
    careers = Paginator(Career.objects.all().order_by('-created_at'), 10).get_page(request.GET.get('page'))
    return render(request, 'dashboard/careers/list.html', {'careers': careers, 'page_title': 'Careers'})


@staff_required
def careers_create(request):
    from contact.models import Career
    if request.method == 'POST':
        Career.objects.create(
            title=request.POST.get('title','').strip(), department=request.POST.get('department',''),
            description=request.POST.get('description',''), requirements=request.POST.get('requirements',''),
            location=request.POST.get('location',''), job_type=request.POST.get('job_type','Full-Time'),
            experience=request.POST.get('experience',''), salary_range=request.POST.get('salary_range',''),
            is_active=request.POST.get('is_active')=='on', deadline=request.POST.get('deadline') or None,
        )
        messages.success(request, 'Career posted.'); return redirect('dashboard:careers_list')
    return render(request, 'dashboard/careers/form.html', {'page_title': 'Post a Job', 'obj': None})


@staff_required
def careers_edit(request, pk):
    from contact.models import Career
    obj = get_object_or_404(Career, pk=pk)
    if request.method == 'POST':
        obj.title=request.POST.get('title',obj.title).strip(); obj.department=request.POST.get('department','')
        obj.description=request.POST.get('description',''); obj.requirements=request.POST.get('requirements','')
        obj.location=request.POST.get('location',''); obj.job_type=request.POST.get('job_type',obj.job_type)
        obj.experience=request.POST.get('experience',''); obj.salary_range=request.POST.get('salary_range','')
        obj.is_active=request.POST.get('is_active')=='on'; obj.deadline=request.POST.get('deadline') or None
        obj.save(); messages.success(request, 'Career updated.'); return redirect('dashboard:careers_list')
    return render(request, 'dashboard/careers/form.html', {'page_title': 'Edit Career', 'obj': obj})


@staff_required
def careers_delete(request, pk):
    from contact.models import Career
    obj = get_object_or_404(Career, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, 'Career deleted.'); return redirect('dashboard:careers_list')
    return render(request, 'dashboard/confirm_delete.html', {'obj': obj, 'page_title': 'Delete Career'})


# ── CONTACT INFO ──────────────────────────────────────────────────────────────
@staff_required
def contact_info(request):
    from contact.models import Contact
    obj = Contact.objects.first()
    fields = ['phone','alt_phone','email','alt_email','address','city','state','pincode',
              'map_embed_url','whatsapp','facebook','instagram','linkedin','youtube','business_hours']
    if request.method == 'POST':
        data = {f: request.POST.get(f,'') for f in fields}
        if obj:
            for k,v in data.items(): setattr(obj, k, v)
            obj.save()
        else:
            Contact.objects.create(**data)
        messages.success(request, 'Contact info saved.')
        return redirect('dashboard:contact_info')
    return render(request, 'dashboard/contact/form.html', {'obj': obj, 'page_title': 'Contact Info'})


# ── ABOUT ─────────────────────────────────────────────────────────────────────
@staff_required
def about_info(request):
    from about.models import About
    obj = About.objects.first()
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title','').strip(),
            'description': request.POST.get('description',''),
            'vision': request.POST.get('vision',''),
            'mission': request.POST.get('mission',''),
            'founded_year': request.POST.get('founded_year') or None,
            'employee_count': request.POST.get('employee_count') or None,
        }
        if obj:
            for k,v in data.items(): setattr(obj,k,v)
            obj.save()
        else:
            About.objects.create(**data)
        messages.success(request, 'About info saved.')
        return redirect('dashboard:about_info')
    return render(request, 'dashboard/about/form.html', {'obj': obj, 'page_title': 'About Info'})


@staff_required
def gallery_list(request):
    from about.models import Gallery
    return render(request, 'dashboard/about/gallery.html', {
        'items': Gallery.objects.all().order_by('order'), 'page_title': 'Gallery'
    })


@staff_required
def gallery_upload(request):
    from about.models import Gallery
    if request.method == 'POST' and request.FILES.get('image'):
        Gallery.objects.create(
            title=request.POST.get('title',''),
            caption=request.POST.get('caption',''),
            order=int(request.POST.get('order',0) or 0),
            is_active=request.POST.get('is_active') == 'on',
            image=request.FILES['image'],
        )
        messages.success(request, 'Image uploaded.')
    return redirect('dashboard:gallery_list')


@staff_required
def gallery_delete(request, pk):
    from about.models import Gallery
    obj = get_object_or_404(Gallery, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, 'Image deleted.')
        return redirect('dashboard:gallery_list')
    return render(request, 'dashboard/confirm_delete.html', {'obj': obj, 'page_title': 'Delete Image'})


# ── AJAX ──────────────────────────────────────────────────────────────────────
@staff_required
@require_http_methods(['POST'])
def ajax_toggle(request):
    model_map = {
        'page': ('pages','Page'), 'post': ('blog','Post'),
        'item': ('portfolio','Item'), 'career': ('contact','Career'),
        'gallery': ('about','Gallery'), 'strength': ('about','Strength'),
    }
    model_name = request.POST.get('model'); pk = request.POST.get('pk'); field = request.POST.get('field')
    if model_name not in model_map:
        return JsonResponse({'ok': False, 'error': 'Unknown model'})
    app, cls = model_map[model_name]
    from django.apps import apps
    Model = apps.get_model(app, cls)
    obj = get_object_or_404(Model, pk=pk)
    current = getattr(obj, field)
    setattr(obj, field, not current)
    obj.save(update_fields=[field])
    return JsonResponse({'ok': True, 'value': not current})


# ── PORTFOLIO CATEGORIES ──────────────────────────────────────────────────────
@staff_required
def portfolio_categories(request):
    from portfolio.models import Category
    cats = Category.objects.annotate(item_count=Count('items')).order_by('order', 'name')
    return render(request, 'dashboard/portfolio/categories.html', {
        'categories': cats, 'page_title': 'Portfolio Categories'
    })


@staff_required
def portfolio_cat_create(request):
    from portfolio.models import Category
    from django.utils.text import slugify
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Category name is required.')
        else:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug':        slugify(name),
                    'description': request.POST.get('description', ''),
                    'icon':        request.POST.get('icon', ''),
                    'order':       int(request.POST.get('order', 0) or 0),
                    'is_active':   request.POST.get('is_active') == 'on',
                }
            )
            if created:
                messages.success(request, f'Category "{name}" created successfully.')
            else:
                messages.warning(request, f'Category "{name}" already exists.')
            return redirect('dashboard:portfolio_categories')
    return render(request, 'dashboard/portfolio/category_form.html', {
        'page_title': 'Add Category', 'obj': None
    })


@staff_required
def portfolio_cat_edit(request, pk):
    from portfolio.models import Category
    obj = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        obj.name        = request.POST.get('name', obj.name).strip()
        obj.description = request.POST.get('description', '')
        obj.icon        = request.POST.get('icon', '')
        obj.order       = int(request.POST.get('order', 0) or 0)
        obj.is_active   = request.POST.get('is_active') == 'on'
        obj.save()
        messages.success(request, f'Category "{obj.name}" updated.')
        return redirect('dashboard:portfolio_categories')
    return render(request, 'dashboard/portfolio/category_form.html', {
        'page_title': f'Edit — {obj.name}', 'obj': obj
    })


@staff_required
def portfolio_cat_delete(request, pk):
    from portfolio.models import Category
    obj = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('dashboard:portfolio_categories')
    return render(request, 'dashboard/confirm_delete.html', {
        'obj': obj, 'page_title': f'Delete Category — {obj.name}'
    })
