from django.contrib import admin
from .models import Task, VectorDesign, VectorImage, Course, CourseVideo, CoursePurchase, Purchase

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


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'design',
        'amount',
        'purchased_at',
        'download_count',
        'paypal_order_id',
    )

    list_filter = (
        'purchased_at',
        'design',
    )

    search_fields = (
        'user__username',
        'user__email',
        'design__title',
        'paypal_order_id',
    )

    readonly_fields = (
        'purchased_at',
    )

    ordering = ('-purchased_at',)