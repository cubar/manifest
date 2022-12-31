# models.py
from django.db import models
from wagtail.images.models import Image, Rendition, AbstractImage, AbstractRendition


class CustomImage(AbstractImage):
    # Add any extra fields to image here
    source = models.CharField(max_length=255, blank=True, default='change-this-source')
    caption = models.CharField(max_length=255, blank=True, default='change-this-caption')

    admin_form_fields = Image.admin_form_fields + (
        #Then add the field names here to make them appear in the form:
        'source', 'caption'
    )


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )
