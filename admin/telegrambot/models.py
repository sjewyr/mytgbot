# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Buildings(models.Model):
    cost = models.BigIntegerField(unique=True)
    income = models.BigIntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "buildings"
        verbose_name = "Здание"
        verbose_name_plural = "Здания"


class UserTasks(models.Model):
    name = models.CharField(max_length=255)
    reward = models.BigIntegerField()
    exp_reward = models.BigIntegerField()
    lvl_required = models.BigIntegerField()
    cost = models.BigIntegerField()
    length = models.IntegerField()

    class Meta:
        managed = False
        db_table = "user_tasks"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class UserUserTasks(models.Model):
    user = models.OneToOneField(
        "Users", models.DO_NOTHING, primary_key=True
    )  # The composite primary key (user_id, task_id) found, that is not supported. The first column is selected.
    task = models.ForeignKey(UserTasks, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "user_user_tasks"
        unique_together = (("user", "task"),)


class Users(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    currency = models.BigIntegerField()
    prestige = models.IntegerField(blank=True, null=True)
    lvl = models.BigIntegerField()
    xp = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class UsersBuildings(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING)
    building = models.ForeignKey(Buildings, models.DO_NOTHING)
    count = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = "users_buildings"
        unique_together = (("user", "building"),)
        verbose_name = "Здание пользователя"
        verbose_name_plural = "Здания пользователей"
