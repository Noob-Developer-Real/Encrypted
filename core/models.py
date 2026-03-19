from django.db import models
import uuid
from . import utility

class Gallery(models.Model):
    id    = models.AutoField(primary_key=True)
    uuid  = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=80, blank=True, null=True)
    about = models.TextField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file_id = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='gallery/images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Gallery"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_image = None
        if not is_new:
            old = Gallery.objects.filter(pk=self.pk).first()
            if old:
                old_image = old.image
        super().save(*args, **kwargs)

        if self.image and (is_new or old_image != self.image):
            with open(self.image.path, "rb") as f:
                data = utility.send_document(f)

            if data.get("ok"):
                self.file_id = data["result"]["document"]["file_id"]
                super().save(update_fields=["file_id"])
                utility.delete_local_file(self.image)
                
    @property
    def telegram_image_url(self) -> str | None:
        if self.file_id:
            return utility.get_file_url(self.file_id)
        return None