from django.db.models.fields.files import ImageField, ImageFieldFile

class SafeImageFieldFile(ImageFieldFile):
    def _get_url(self):
        try:
            return super().url
        except ValueError:
            return None
    
    url = property(_get_url)

class SafeImageField(ImageField):
    attr_class = SafeImageFieldFile
