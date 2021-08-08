from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_post, name="new_post"),
    path("group/", views.group_list, name="group_list"),
    path("user/", views.user_list, name="user_list"),
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit,
         name='post_edit'),
    path("<username>/<int:post_id>/comment", views.add_comment, name="add_comment"), 

]
