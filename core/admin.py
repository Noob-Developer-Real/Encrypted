from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.urls import reverse
from .models import Gallery


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "title",
        "short_about",
        "file_id",
        "created_display",
        "updated_display",
    )
    list_display_links = ("image_preview", "title")
    search_fields = ("title", "about", "description", "file_id")
    list_per_page = 20
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Media",
            {
                "fields": ("image", "image_preview_large", "file_id"),
                "description": "Upload an image — it will be encrypted and sent to Telegram automatically.",
            },
        ),
        (
            "Content",
            {
                "fields": ("title", "about", "description"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
                "description": "These fields are set automatically.",
            },
        ),
    )

    readonly_fields = ("image_preview_large", "file_id", "created_at", "updated_at")

    def _proxy_url(self, obj):
        """
        Returns the image_proxy URL for this object if it has a file_id.
        Falls back to the local image URL if the file hasn't been sent yet.
        """
        if obj.pk and obj.file_id:
            return reverse("image-proxy", args=[obj.pk])
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                pass
        return None

    @admin.display(description="Preview")
    def image_preview(self, obj):
        url = self._proxy_url(obj)
        if url:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;'
                'object-fit:cover;border-radius:8px;'
                'box-shadow:0 1px 4px rgba(0,0,0,.25);" />',
                url,
            )
        return format_html('<span style="color:#aaa;font-size:11px;">No image</span>')

    @admin.display(description="Image Preview")
    def image_preview_large(self, obj):
        """Shown inside the detail/edit form."""
        url = self._proxy_url(obj)
        if url:
            return format_html(
                '<img src="{}" style="max-width:320px;max-height:240px;'
                'object-fit:cover;border-radius:10px;'
                'box-shadow:0 2px 8px rgba(0,0,0,.3);margin-top:6px;" />'
                '<p style="color:#888;font-size:11px;margin-top:6px;">'
                '🔒 Decrypted on the fly from Telegram</p>',
                url,
            )
        return format_html('<span style="color:#aaa;">No image yet — save first.</span>')

    @admin.display(description="About")
    def short_about(self, obj):
        if obj.about:
            return obj.about[:60] + ("…" if len(obj.about) > 60 else "")
        return format_html('<span style="color:#aaa;">—</span>')

    @admin.display(description="Created")
    def created_display(self, obj):
        return localtime(obj.created_at).strftime("%d %b %Y, %H:%M")

    @admin.display(description="Updated")
    def updated_display(self, obj):
        return localtime(obj.updated_at).strftime("%d %b %Y, %H:%M")

    class Media:
        css = {
            "all": (
                "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap",
            )
        }   