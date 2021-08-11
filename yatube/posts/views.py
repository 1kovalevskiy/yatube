from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def paginator(request, lst):
    paginator = Paginator(lst, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page = paginator(request, post_list)
    return render(request,
                  'posts/index.html',
                  {'page': page, }
                  )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page = paginator(request, post_list)
    return render(request, "posts/group.html", {"group": group, "page": page})


def group_list(request):
    groups = Group.objects.all()
    groups = paginator(request, groups)
    return render(request, "posts/groups_list.html", {"groups": groups})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    page = paginator(request, post_list)
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(
            user=request.user,
            author=user,
        ).exists():
            following = True
    content = {
        "user_post": user,
        "page": page,
        "following": following,
    }
    return render(request, 'posts/profile.html', content)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    user = post.author
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("post", username=username, post_id=post_id)

    comments = post.comments.all()
    content = {
        "user_post": user,
        "post": post,
        "form": form,
        "comments": comments,
    }
    return render(request, 'posts/post.html', content)


def user_list(request):
    users = User.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    return render(request, "posts/user_list.html", {"users": users})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        cache.clear()
        return redirect("/")
    return render(request, "posts/new_post.html", {"form": form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    if request.user != post.author:
        return redirect("/")
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return render(
        request, "posts/post_edit.html",
        {"form": form, "post": post}
    )


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
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
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "posts/add_comment.html", {"form": form})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page = paginator(request, post_list)
    return render(request,
                  'posts/follow.html',
                  {'page': page, })


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        return redirect("profile", username=username)
    Follow.objects.get_or_create(
        user=request.user,
        author=user,
    )
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        return redirect("profile", username=username)
    follow = Follow.objects.get(
        user=request.user,
        author=user,
    )
    follow.delete()
    return redirect("profile", username=username)
