from django.contrib import admin
from speech.models import User, Recording, AnchorSet, Anchor, SourceModel, GoldenSpeaker, Utterance


class AnchorsetAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('anchor_set_name',)}
admin.site.register(User)
admin.site.register(Recording)
admin.site.register(AnchorSet, AnchorsetAdmin)
admin.site.register(Anchor)
admin.site.register(SourceModel)
admin.site.register(GoldenSpeaker)
admin.site.register(Utterance)

