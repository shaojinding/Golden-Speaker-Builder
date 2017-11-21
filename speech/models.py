from __future__ import unicode_literals
from django.template.defaultfilters import slugify
from django.db import models
import json


class User(models.Model):
    user_name = models.CharField(unique=True, max_length=128)

    def __unicode__(self):
        return self.user_name


class AnchorSet(models.Model):
    anchor_set_name = models.CharField(max_length=128)
    user = models.ForeignKey(User)
    timestamp = models.CharField(max_length=128)  # set up time
    active = models.BooleanField()  # whether the anchor set is active (in using)
    used = models.BooleanField()  # whether the anchor set has been used
    completed = models.BooleanField()  # whether all anchors are recorded
    built = models.CharField(max_length=128)  # whether sabr model has been built
    modified = models.BooleanField()
    aborted = models.BooleanField()
    slug = models.SlugField()
    saved_phonemes = models.CharField(max_length=1000)  # phonemes which are saved
    sabr_model_path = models.CharField(max_length=128)  # path to sabr model
    pitch_path = models.CharField(max_length=128)  # path to pitch recording file

    class Meta:
        unique_together = ('anchor_set_name', 'user')

    def save(self, *args, **kwargs):  # slugify before save
        self.slug = slugify(self.anchor_set_name)
        super(AnchorSet, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.anchor_set_name

    def set_saved_phonemes(self, x):  # set saved phonemes from front end
        self.saved_phonemes = json.dumps(x)

    def get_saved_phonemes(self):  # get saved phonemes to front end
        return json.loads(self.saved_phonemes)


class Anchor(models.Model):  # the anchor is determined by both recording and anchor set
    anchor_set = models.ForeignKey(AnchorSet)
    phoneme = models.CharField(max_length=128)
    L = models.FloatField(default=0.0)
    C = models.FloatField(default=0.0)
    R = models.FloatField(default=0.0)

    def __unicode__(self):
        return '{0}_{1}_{2}'.format(self.anchor_set.user.user_name, self.anchor_set.anchor_set_name, self.phoneme)


class Recording(models.Model):
    record_name = models.CharField(unique=True, max_length=128)
    phoneme = models.CharField(max_length=128)  # phoneme of the recording
    user = models.ForeignKey(User)
    anchor = models.ForeignKey(Anchor)

    def __unicode__(self):
        return self.record_name


class SourceModel(models.Model):
    model_name = models.CharField(unique=True, max_length=20)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):  # slugify before save
        self.slug = slugify(self.model_name)
        super(SourceModel, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.model_name


class Utterance(models.Model):  # the utterance belongs to a source model, and has transcription and name
    source_model = models.ForeignKey(SourceModel)
    transcription = models.CharField(max_length=512)
    name = models.CharField(max_length=128)
    week = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class GoldenSpeaker(models.Model):  # golden speaker is determined by source model and anchor set (target model)
    speaker_name = models.CharField(unique=True, max_length=128)
    anchor_set = models.ForeignKey(AnchorSet)
    source_model = models.ForeignKey(SourceModel)
    user = models.ForeignKey(User)
    slug = models.SlugField(unique=True)
    contained_utterance = models.ManyToManyField(Utterance)
    timestamp = models.CharField(max_length=128)
    status = models.CharField(max_length=128)
    aborted = models.BooleanField()
    tempo_scale = models.FloatField()

    def save(self, *args, **kwargs):  # slugify before save
        self.slug = slugify(self.speaker_name)
        super(GoldenSpeaker, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.speaker_name

