from django.db import models
from django.utils import timezone


class Article(models.Model):
    """博客文章表"""
    title = models.CharField(max_length=255, verbose_name='标题', default='')
    body = models.TextField('内容')
    excerpt = models.CharField(max_length=255, verbose_name='摘要', default='')
    category = models.ForeignKey('Category', null=True, on_delete=models.SET_NULL)
    # tags => [tag_id, tag_id, tag_id]
    tags = models.JSONField(default=list)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Category(models.Model):
    """分类"""
    name = models.TextField('分类名称')
    # create_time = models.DateTimeField(auto_now_add=True)
    # update_time = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    """标签"""
    name = models.TextField('标签名称')


class Mood(models.Model):
    """说说"""
    content = models.CharField(max_length=255, verbose_name='内容')
    create_time = models.DateTimeField(default=timezone.now)
    is_visible = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)


class Group(models.Model):
    """权限组"""
    name = models.CharField('组名', max_length=15, unique=True)


class Permission(models.Model):
    """权限"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, db_constraint=False)
    name = models.CharField('权限名', max_length=31)


class User(models.Model):
    """用户"""
    username = models.CharField('用户名', max_length=15, unique=True)
    password = models.CharField('密码', max_length=128)
    is_active = models.BooleanField('激活', default=True)
    is_admin = models.BooleanField('管理员', default=False)
    last_login = models.DateTimeField('上次登录时间', default=timezone.now)
    create_time = models.DateTimeField('创建时间', default=timezone.now)
    group = models.ManyToManyField(Group, db_constraint=False)
