from django.db import models


class Article(models.Model):
    """博客文章表"""
    title = models.CharField(max_length=255, verbose_name='标题', default='')
    body = models.TextField('内容')
    excerpt = models.CharField(max_length=255, verbose_name='摘要', default='')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, db_constraint=False)
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
    name = models.TextField('标签名称')
