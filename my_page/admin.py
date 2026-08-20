from django.contrib import admin
from .models import Task, VectorDesign, VectorImage, Course, CourseVideo, CoursePurchase


class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )
admin.site.register(Task, TaskAdmin)    

class VectorImageInline(admin.TabularInline):
    model = VectorImage
    extra = 1
    max_num = 10

@admin.register(VectorDesign)
class VectorDesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')
    inlines = [VectorImageInline]


class CourseVideoInline(admin.TabularInline):
    model = CourseVideo
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseVideoInline]

admin.site.register(Course, CourseAdmin)
admin.site.register(CoursePurchase)
admin.site.register(CourseVideo)