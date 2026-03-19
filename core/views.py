import imghdr
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Gallery
from . import utility


def gallery_list(request):
    photos = Gallery.objects.all()
    gallery_data = []
    for photo in photos:
        gallery_data.append({
            "id":    photo.pk,        # ← needed for image-proxy URL
            "uuid":  photo.uuid,      # ← needed for gallery-detail URL
            "title": photo.title or "Untitled",
            "about": photo.about or "",
        })
    return render(request, "gallery/gallery_list.html", {
        "photos": gallery_data,
        "total":  len(gallery_data),
    })


def gallery_detail(request, uuid):   # ← was 'pk', now matches URL <uuid:uuid>
    photo = get_object_or_404(Gallery, uuid=uuid)
    data = {
        "id":          photo.pk,      # ← needed for image-proxy URL
        "uuid":        photo.uuid,
        "title":       photo.title or "Untitled",
        "about":       photo.about or "",
        "description": photo.description or "",
        "created_at":  photo.created_at,
        "updated_at":  photo.updated_at,
    }
    return render(request, "gallery/gallery_detail.html", {"photo": data})


def image_proxy(request, pk):        # ← stays as pk (int), used internally
    photo = get_object_or_404(Gallery, pk=pk)

    if not photo.file_id:
        raise Http404("No image stored for this photo.")

    raw_bytes = utility.fetch_and_decrypt(photo.file_id)

    if raw_bytes is None:
        raise Http404("Could not decrypt image.")

    image_type = imghdr.what(None, h=raw_bytes) or "jpeg"
    response = HttpResponse(raw_bytes, content_type=f"image/{image_type}")
    response["Cache-Control"] = "private, max-age=2700"
    return response
