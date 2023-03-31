from django.db import models
from django.db.models import Q
from accounts.models import User


class Benefactor(models.Model):
    EXPERIENCE_CHOICES = (
        (0, "beginner"),
        (1, "midlevel"),
        (2, "expert"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    experience = models.SmallIntegerField(choices=EXPERIENCE_CHOICES, default=0)
    free_time_per_week = models.PositiveSmallIntegerField(default=0)


class Charity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    reg_number = models.CharField(max_length=10)


class TaskManager(models.Manager):

    def related_tasks_to_charity(self, user):
        return Task.objects.filter(charity__user_id=user.id)

    def related_tasks_to_benefactor(self, user):
        return Task.objects.filter(assigned_benefactor__user_id=user.id)

    def all_related_tasks_to_user(self, user):

        #condition = ~Q(charity__user_id=user.id) & ~Q(assigned_benefactor__user_id=user.id)
        charityTasks = self.related_tasks_to_charity(user)
        benefactorTasks = self.related_tasks_to_benefactor(user)
        charityTasks.union(benefactorTasks)
        return Task.objects.difference(charityTasks)


class Task(models.Model):
    GENDER_CHOICES = (
        ("M", "male"),
        ("F", "female"),
    )
    STATE_CHOICES = (
        ("P", "Pending"),
        ("W", "Waiting"),
        ("A", "Assigned"),
        ("D", "Done"),
    )
    assigned_benefactor = models.ForeignKey(Benefactor, null=True, on_delete=models.SET_NULL)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    age_limit_from = models.IntegerField(blank=True, null=True)
    age_limit_to = models.IntegerField(blank=True, null=True)
    data = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    gender_limit = models.CharField(max_length=1, blank=True, null=True, choices=GENDER_CHOICES)
    state = models.CharField(choices=STATE_CHOICES, default="P", max_length=1)
    title = models.CharField(max_length=60)
    objects = TaskManager()


