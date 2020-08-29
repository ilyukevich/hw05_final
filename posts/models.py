from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
User = get_user_model()


class Group(models.Model):
    """creating a GROUP model"""
    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique=True, null=True)
    description = models.TextField('description', null=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    """creating a Post model"""
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    # group = models.ForeignKey(Group, on_delete=models.CASCADE,
    #                           blank=True, null=True, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="posts")
    # поле для картинки
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):

    post = models.ForeignKey(Post, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="comments")
    text = models.TextField()
    created = models.DateTimeField("created", auto_now_add=True)

    class Meta:
        ordering = ["-created"]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')


