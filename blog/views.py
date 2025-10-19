from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic import CreateView
from .models import Post, Category, Comment, Subscription
from .forms import PostForm, CommentForm, SubscriptionForm


from .models import Post, Category
from .forms import PostForm


def get_categories():
    all = Category.objects.all()
    half = all.count() // 2
    first_half = all[:half]
    second_half = all[half:]
    return {'cats1': first_half,
            'cats2': second_half}


def index(request):
    posts = Post.objects.all().order_by("-published_date")
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'posts': posts, 'page_obj': page_obj}
    context.update(get_categories())
    return render(request, "blog/index.html", context=context)


def about(request):
    context = {}
    return render(request, "blog/about.html", context=context)


def contact(request):
    context = {}
    return render(request, "blog/contact.html", context=context)


def post(request, slug=None):
    post = get_object_or_404(Post, slug=slug)

    # Получаем комментарии из базы
    comments = Comment.objects.filter(post=post).order_by('-created_at')

    subscription_success = False
    comment_success = False

    if request.method == 'POST':
        # Обработка подписки
        if 'subscribe_submit' in request.POST:
            email = request.POST.get('email')
            if email and '@' in email:
                subscription_success = True

        # Обработка комментария
        elif 'comment_submit' in request.POST:
            if request.user.is_authenticated:
                text = request.POST.get('text')
                if text and text.strip():
                    # Создаем комментарий
                    Comment.objects.create(
                        post=post,
                        author=request.user,
                        text=text.strip()
                    )
                    comment_success = True
                    # Обновляем список комментариев
                    comments = Comment.objects.filter(post=post).order_by('-created_at')
            else:
                # Если пользователь не авторизован
                from django.contrib import messages
                messages.error(request, 'Для комментирования необходимо войти в систему.')
                return redirect('blog_login')

    context = {
        'post': post,
        'comments': comments,
        'subscription_success': subscription_success,
        'comment_success': comment_success,
    }
    context.update(get_categories())
    return render(request, "blog/post.html", context=context)

def category(request, slug=None):
    c = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=c).order_by("-published_date")
    context = {'posts': posts}
    context.update(get_categories())
    return render(request, "blog/index.html", context=context)


def search(request):
    query = request.GET.get('query')
    posts = Post.objects.filter(Q(content__icontains=query) | Q(title__icontains=query)).order_by("-published_date")
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'posts': posts, 'page_obj': page_obj}
    context.update(get_categories())
    return render(request, "blog/index.html", context=context)

# @login_required
# def create(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.published_date = now()
#             post.auther = request.user
#             post.save()
#     formCreate = PostForm()
#     context = {'formCreate': formCreate}
#     context.update(get_categories())
#     return render(request, "blog/create.html", context=context)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.published_date = now()
        post.auther = self.request.user
        post.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_categories())
        return context

def custom_logout_view(request):
    logout(request)
    return redirect('home')


class PostCreateView_as_view:
    pass


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by('-created_at')

    # Инициализируем формы
    comment_form = CommentForm()
    subscription_form = SubscriptionForm()
    subscription_success = False

    if request.method == 'POST':
        # Обработка комментария
        if 'comment_submit' in request.POST:
            if request.user.is_authenticated:
                comment_form = CommentForm(request.POST)
                if comment_form.is_valid():
                    comment = comment_form.save(commit=False)
                    comment.post = post
                    comment.author = request.user
                    comment.save()
                    return redirect('post_detail', pk=post.pk)
            else:
                return redirect('blog_login')

        # Обработка подписки
        elif 'subscribe_submit' in request.POST:
            subscription_form = SubscriptionForm(request.POST)
            if subscription_form.is_valid():
                email = subscription_form.cleaned_data['email']
                # Проверяем, нет ли уже такой подписки
                if not Subscription.objects.filter(email=email).exists():
                    subscription = subscription_form.save(commit=False)
                    if request.user.is_authenticated:
                        subscription.user = request.user
                    subscription.save()
                    subscription_success = True
                else:
                    subscription_success = True  # Все равно показываем успех

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'subscription_form': subscription_form,
        'subscription_success': subscription_success,
    }
    context.update(get_categories())
    return render(request, 'blog/post_detail.html', context)