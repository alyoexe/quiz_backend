from django.contrib import admin
from .models import UploadedPDF, Quiz, Question, Option 
# Register your models here.


admin.site.register(UploadedPDF)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)