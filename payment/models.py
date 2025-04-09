from django.db import models

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = "courses"


    def __str__(self):
        return self.name
    