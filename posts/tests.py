from django.test import TestCase, Client
from .models import Group, Post, User, Follow, Comment
from django.urls import reverse

from django.core.cache import cache



class ProfileTest(TestCase):
    def setUp(self):
        self.auth_client = Client()
        self.unauth_client = Client()
        self.user_auth = User.objects.create_user(username="sarah")
        self.user_unauth = User.objects.create_user(username="anonimus")
        self.group = Group.objects.create(title="titlejust", slug="just", description="description1")
        self.auth_client.force_login(self.user_auth)
        cache.clear()


    def search_text_page(self, text):
        """checking the presence of a post on all the necessary pages
        (new entry appeared on all linked pages)"""

        search_text = text
        for url in (
            reverse("index"),
            reverse("profile", kwargs={"username": self.user_auth}),
            reverse("post", kwargs={"username": self.user_auth, "post_id": self.post.id}),
            reverse("group", kwargs={"slug": self.group.slug})
        ):
            response = self.auth_client.get(url)
            self.assertContains(response, search_text)



    def check_fields(self, post_text):
        """checking all fields from context"""

        post_get = Post.objects.get(author=self.user_auth, id=self.post.id)
        value = post_text
        self.assertEqual(post_get.text, value)
        self.assertEqual(post_get.author, self.user_auth)
        self.assertEqual(post_get.group, self.group)


    def test_personal_page(self):
        """After registering a user, his personal page (profile) is created"""

        response = self.auth_client.get(reverse("profile", args=[self.user_auth]))
        self.assertEqual(response.status_code, 200)


    def test_create_post_auth(self):
        """test_create_post
        An authorized user can publish a post (new),
        check the author's group, text and number of posts in the database"""

        self.text_new = "just test text"
        posts_count_now = Post.objects.filter(author=self.user_auth).count()
        self.post = Post.objects.create(
            text=self.text_new,
            author=self.user_auth, group=self.group)
        posts_count_last = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(posts_count_last, posts_count_now + 1)
        response = self.auth_client.get(reverse("profile", args=[self.user_auth]))
        self.assertEqual(len(response.context["author_posts"]), 1)
        self.assertContains(response, self.post.text)
        self.assertContains(response, self.post.group)

        # check if a post is present on all required pages
        self.search_text_page(self.text_new)

        # checking all fields from context
        self.check_fields(self.text_new)


    def test_create_post_unauth(self):
        """test_create_post
        An unauthorized user can publish a post (new)"""
        test_text = "Python"
        posts_count_now = Post.objects.filter(author=self.user_unauth).count()
        response = self.unauth_client.post(reverse('new_post'),
                                    {'text': test_text, 'author': self.user_unauth,
                                     'group': self.group.id}, follow=True)
        posts_count_last = Post.objects.filter(author=self.user_unauth).count()
        self.assertEqual(posts_count_last, posts_count_now)
        self.assertRedirects(response, f"{reverse('login')}?next=/new/")


    def test_edit(self):
        """test_edit_post
                An authorized user can edit a post"""
        self.text_create = "Old just test text11111"
        self.text_edit = "New text11111"
        self.post = Post.objects.create(
             text=self.text_create,
             author=self.user_auth, group=self.group)
        post_now = Post.objects.filter(author=self.user_auth).count()
        response = self.auth_client.post(
            reverse("post_edit",
                    kwargs={"username": self.user_auth,
                            "post_id": self.post.id, }),
                    {'text': self.text_edit, 'group': self.group.id})
        self.assertEqual(response.status_code, 302)
        post_update = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(post_now, post_update)
        self.search_text_page(self.text_edit)
        self.check_fields(self.text_edit)

    def test_404(self):
        #response = self.auth_client.get(reverse("profile", args=[self.user_auth]))
        response = self.auth_client.get('/go/', follow=True)
        self.assertEqual(response.status_code, 404)


    # проверяют страницу конкретной записи с картинкой: на странице есть тег < img >
    # проверяют, что на главной странице, на странице профайла и на странице группы пост с картинкой
    # отображается корректно, с тегом < img >
    def test_img_correct_in_post(self):
        """Тест на создание поста, изменение его с добавлением изображения
        и проверкой на содержание на нужных страницах тега <img"""
        self.text_create = "Old just test 4444text11111"
        self.text_edit = "New text111144441"
        self.post = Post.objects.create(
            text=self.text_create,
            author=self.user_auth, group=self.group)
        with open('media/posts/Снимок_экрана_от_2020-02-16_13-46-29.png', 'rb') as self.img:
            response = self.auth_client.post(
                reverse("post_edit",
                    kwargs={"username": self.user_auth,
                            "post_id": self.post.id, }),
                    {'text': self.text_edit, 'group': self.group.id, 'image': self.img})
        self.assertEqual(response.status_code, 302)
        post_update = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(post_update, 1)

        for url in (
                    reverse("index"),
                    reverse("profile", kwargs={"username": self.user_auth}),
                    reverse("post", kwargs={"username": self.user_auth, "post_id": self.post.id}),
                    reverse("group", kwargs={"slug": self.group.slug})
            ):
                response = self.auth_client.get(url)
                self.assertContains(response, '<img')
                self.assertIn('img', response.content.decode())


    # check that protection against downloading non-graphic files is triggered
    def test_shield_not_img(self):
        with open('media/posts/test.txt', 'rb') as img:
            self.auth_client.post(
                reverse(
                    'new_post'
                ),
                {
                    'author': self.user_auth,
                    'text': 'post with image test',
                    'group': self.group.id,
                    'image': img
                }
            )
        upd = Post.objects.count()
        # post is not created
        self.assertEqual(upd, 0)


    def test_cache_index(self):
        """Cache test"""
        post_now = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(post_now, 0)
        self.text_create_1 = "Old just test 11111111"
        self.text_create_2 = "Old just test 22222222"
        self.post_1 = Post.objects.create(
            text=self.text_create_1,
            author=self.user_auth, group=self.group)
        response = self.auth_client.get(reverse("index"))
        self.assertContains(response, self.text_create_1)
        post_update = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(post_update, 1)
        self.post_2 = Post.objects.create(
            text=self.text_create_2,
            author=self.user_auth, group=self.group)
        response_next = self.auth_client.get(reverse("index"))
        self.assertNotContains(response_next, self.text_create_2)
        post_update_2 = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(post_update_2, 2)
        cache.clear()
        response_next_2 = self.auth_client.get(reverse("index"))
        self.assertContains(response_next_2, self.text_create_1)
        self.assertContains(response_next_2, self.text_create_2)
        post_update_3 = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(post_update_3, 2)


    def test_auth_follow_unfollow(self):
        """An authorized user can subscribe
        to other users and remove them from subscriptions"""
        #follow
        response = self.auth_client.post(
            reverse("profile_follow",
                    kwargs={"username": self.user_unauth}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile", kwargs={"username": self.user_unauth}))
        follow_count_next = Follow.objects.count()
        self.assertEqual(follow_count_next, 1)

        # unfollow
        response_next = self.auth_client.post(
            reverse("profile_unfollow",
                    kwargs={"username": self.user_unauth}))
        self.assertEqual(response_next.status_code, 302)
        self.assertRedirects(response_next, reverse("profile", kwargs={"username": self.user_unauth}))
        follow_count_next_2 = Follow.objects.count()
        self.assertEqual(follow_count_next_2, 0)


    def test_new_follow_index(self):
        """A new user record appears in the feed of those who are subscribed
        to it and does not appear in the feed of those who is not following it"""
        #follow
        response = self.auth_client.post(
            reverse("profile_follow",
                    kwargs={"username": self.user_unauth}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile", kwargs={"username": self.user_unauth}))
        follow_count_next = Follow.objects.count()
        self.assertEqual(follow_count_next, 1)
        #create new post
        self.text_new = "new text create"
        posts_count_now = Post.objects.filter(author=self.user_auth).count()
        self.post = Post.objects.create(
            text=self.text_new,
            author=self.user_unauth, group=self.group)
        posts_count_last = Post.objects.filter(author=self.user_unauth).count()
        self.assertEqual(posts_count_last, posts_count_now + 1)
        #checking in the feed of those who are subscribed
        response = self.auth_client.post(
            reverse("follow_index"), follow=True)
        self.assertContains(response, self.text_new)
        #checking in the feed of those who are not subscribed
        response = self.unauth_client.post(
            reverse("follow_index"), follow=True)
        self.assertNotContains(response, self.text_new)


    def test_auth_add_comment(self):
        """Only an authorized user can comment on posts."""
        # create new post
        self.text_new = "new text create"
        self.comment_text = "new comment"
        self.post = Post.objects.create(
            text=self.text_new,
            author=self.user_auth, group=self.group)
        posts_count_last = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(posts_count_last, 1)
        # create new comment
        self.comment = Comment.objects.create(
            text=self.comment_text,
            author=self.user_auth)
        comment_count = Comment.objects.count()
        self.assertEqual(comment_count, 1)
