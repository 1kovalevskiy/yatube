from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        help_texts = {
            "text": "Здесь должен быть текст поста",
            "group": "А здесь можно выбрать группу для опубликования",
            "image": "Тут можно прикрепить картиночку"
        }
        labels = {
            "text": "Текст поста",
            "group": "Группа",
            "image": "Изображение"
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text",]
        help_texts = {
            "text": "Здесь должен быть текст поста",
        }
        labels = {
            "text": "Текст поста",
        }