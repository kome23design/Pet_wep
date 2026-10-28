from django.contrib import admin
from .models import FAQ, GalleryItem, ContactInquiry, NewsletterSubscriber, BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'read_time', 'is_featured', 'is_published', 'published_at')
    list_filter = ('category', 'is_featured', 'is_published', 'published_at')
    search_fields = ('title', 'content', 'excerpt', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_published')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'display_order', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')
    list_editable = ('display_order', 'is_published')


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'breed_tag', 'display_order', 'is_featured', 'created_at')
    list_filter = ('breed_tag', 'is_featured')
    search_fields = ('title', 'caption')
    list_editable = ('display_order', 'is_featured')


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
