from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.views.decorators.cache import cache_page
from django.core.cache import cache

#@cache_page(20, key_prefix='index_page')
def index(request):
    latest = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(latest, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'posts': latest, 'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    """view function for community page"""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group, "page": page, "paginator": paginator}
    )


# close pages from unauthorized users
@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('/')
    return render(request, 'new_post.html', {'form': form})


# close pages from unauthorized users
@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    if profile != request.user:
        return redirect("post", username=post.author, post_id=post_id)

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        edit_post = form.save(commit=False)
        edit_post.author = post.author
        edit_post.id = post.id
        edit_post.pub_date = post.pub_date
        edit_post.save()
        return redirect("post", username=post.author, post_id=post_id)


    context = {
        "form": form,
        "post": post,
        "username": username,
        "post_id": post_id,
        }
    return render(request, "new_post.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = Post.objects.filter(author=author).count()
    author_posts = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(author_posts, 10)
    page = paginator.get_page(request.GET.get('page'))
    following = False
    if request.user.is_authenticated:
        author_value = User.objects.get(username=username)
        user_value = User.objects.get(username=request.user)
        following = Follow.objects.filter(author=author_value, user=user_value)

    return render(request, 'profile.html', {
        'page': page,
        'paginator': paginator,
        'posts_count': posts_count,
        'author': author,
        'author_posts': author_posts,
        'following': following,
    })

#edit for comments
def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author.id, id=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    items = post.comments.order_by('-created').all()
    return render(request, 'post.html', {
        'posts_count': posts_count,
        'post': post,
        'author': author,
        # for comment
        'items': items,
        'form': CommentForm(),
    })


def page_not_found(request, exception):
    # The exception variable contains debug information,
    # we will not display it in the custom 404 page template
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'comments.html', {'form': form, 'post': post})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    unfollow_profile = Follow.objects.get(author__username=username, user=request.user)
    # if Follow.objects.filter(pk=unfollow_profile.pk).exists():
    #     unfollow_profile.delete()
    unfollow_profile.delete()
    return redirect('profile', username=username)
