from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Gallery
from . import utility


def _detect_image_type(data: bytes) -> str:
    """Detect image MIME type from magic bytes. Replaces removed imghdr module."""
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if data[:3] == b'\xff\xd8\xff':
        return 'jpeg'
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'webp'
    if data[:4] in (b'MM\x00*', b'II*\x00'):
        return 'tiff'
    if data[:4] == b'BM':
        return 'bmp'
    return 'jpeg'  # safe fallback


def gallery_list(request):
    photos = Gallery.objects.all()
    gallery_data = []
    for photo in photos:
        gallery_data.append({
            "id":    photo.pk,       
            "uuid":  photo.uuid,      
            "title": photo.title or "Untitled",
            "about": photo.about or "",
        })
    return render(request, "gallery/gallery_list.html", {
        "photos": gallery_data,
        "total":  len(gallery_data),
    })


def gallery_detail(request, uuid):  
    photo = get_object_or_404(Gallery, uuid=uuid)
    data = {
        "id":          photo.pk,      
        "uuid":        photo.uuid,
        "title":       photo.title or "Untitled",
        "about":       photo.about or "",
        "description": photo.description or "",
        "created_at":  photo.created_at,
        "updated_at":  photo.updated_at,
    }
    return render(request, "gallery/gallery_detail.html", {"photo": data})


def image_proxy(request, pk):
    photo = get_object_or_404(Gallery, pk=pk)

    if not photo.file_id:
        raise Http404("No image stored for this photo.")

    raw_bytes = utility.fetch_and_decrypt(photo.file_id)

    if raw_bytes is None:
        raise Http404("Could not decrypt image.")

    image_type = _detect_image_type(raw_bytes)
    response = HttpResponse(raw_bytes, content_type=f"image/{image_type}")
    response["Cache-Control"] = "private, max-age=2700"
    return response
