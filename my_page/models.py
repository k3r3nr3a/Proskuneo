from django.db import models
from django.contrib.auth.models import User 


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datacompleted = models.DateTimeField(null=True, blank=True) 
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        title = self.title if self.title else "Sin título"
        username = self.user.username if self.user else "Anónimo"
        return f"{title} - by {username}"


class VectorDesign(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    preview_image = models.ImageField(upload_to='previews/')
    vector_file = models.FileField(upload_to='vectors/')  # Puedes subir .zip, .rar
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



# ✅ Modelo para imágenes adicionales (galería tipo lightbox)
class VectorImage(models.Model):
    design = models.ForeignKey(VectorDesign, related_name='extra_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vectores/')

    def __str__(self):
        return f"Imagen de {self.design.title}"
    

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    design = models.ForeignKey(VectorDesign, on_delete=models.CASCADE)
    paypal_order_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'design')

    def __str__(self):
        return f"{self.user.username} compró {self.design.title}"


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    preview_image = models.ImageField(upload_to='cursos/')

    def __str__(self):
        return self.title


class CourseVideo(models.Model):
    course = models.ForeignKey(Course, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    youtube_url = models.URLField()
    order = models.IntegerField(default=0)  # Para ordenar los videos (1, 2, 3...)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CoursePurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    paypal_order_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} compró {self.course.title}"