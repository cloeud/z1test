from django.contrib import admin
from .models import User, FollowRequest, Idea, Profile


admin.site.register(User)
admin.site.register(FollowRequest)
admin.site.register(Idea)
admin.site.register(Profile)
