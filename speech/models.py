from __future__ import unicode_literals
from django.template.defaultfilters import slugify
from django.db import models
import json
import os


class User(models.Model):
    user_name = models.CharField(unique=True, max_length=128)

    def __unicode__(self):
        return self.user_name


class AnchorSet(models.Model):
    anchor_set_name = models.CharField(max_length=128)
    user = models.ForeignKey(User)
    timestamp = models.CharField(max_length=128)  # set up time
    active = models.BooleanField(default=False)  # whether the anchor set is active (in using)
    completed = models.BooleanField(default=False)  # whether all anchors are recorded
    built = models.CharField(max_length=128, default='False')  # whether sabr model has been built
    modified = models.BooleanField(default=False)
    aborted = models.BooleanField(default=False)
    display = models.CharField(max_length=128, default='Phoneme')
    slug = models.SlugField()
    saved_phonemes = models.CharField(max_length=1000, default='[""]')  # phonemes which are saved
    wav_file_dir = models.CharField(max_length=128, default='')  # wav file parent directory
    cached_file_dir = models.CharField(max_length=128, default='')  # cached file parent directory
    cached_file_paths = models.CharField(max_length=4000, default='[""]')
    pitch_model_dir = models.CharField(max_length=128, default='')

    class Meta:
        unique_together = ('anchor_set_name', 'user')

    def save(self, *args, **kwargs):  # slugify before save
        self.slug = slugify(self.anchor_set_name)
        super(AnchorSet, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.anchor_set_name

    def set_wav_file_dir(self, x):
        self.wav_file_dir = x
        if not os.path.exists(self.wav_file_dir):
            os.makedirs(self.wav_file_dir)

    def set_cached_file_dir(self, x):
        self.cached_file_dir = x
        if not os.path.exists(self.cached_file_dir):
            os.makedirs(self.cached_file_dir)

    def set_pitch_model_dir(self, x):
        self.pitch_model_dir = x
        if not os.path.exists(os.path.dirname(self.pitch_model_dir)):
            os.makedirs(os.path.dirname(self.pitch_model_dir))

    def set_saved_phonemes(self, x):  # set saved phonemes from front end
        self.saved_phonemes = json.dumps(x)

    def get_saved_phonemes(self):  # get saved phonemes to front end
        return json.loads(self.saved_phonemes)

    def set_cached_file_paths(self, x):  # set cached file path
        self.cached_file_paths = json.dumps(x)

    def get_cached_file_paths(self):  # get cached file path
        return json.loads(self.cached_file_paths)


class Anchor(models.Model):  # the anchor is determined by both recording and anchor set
    anchor_set = models.ForeignKey(AnchorSet)
    record_name = models.CharField(max_length=128, default='')
    L = models.FloatField(default=0.0)
    C = models.FloatField(default=0.0)
    R = models.FloatField(default=0.0)

    def __unicode__(self):
        return self.record_name


# class Recording(models.Model):
#     record_name = models.CharField(unique=True, max_length=128)
#     phoneme = models.CharField(max_length=128)  # phoneme of the recording
#     user = models.ForeignKey(User)
#     anchor = models.ForeignKey(Anchor)
#
#     def __unicode__(self):
#         return self.record_name


class SourceModel(models.Model):
    model_name = models.CharField(unique=True, max_length=20)
    slug = models.SlugField(unique=True)
    cached_file_paths = models.CharField(max_length=4000, default='[""]')
    pitch_model_dir = models.CharField(max_length=128, default='')

    def save(self, *args, **kwargs):  # slugify before save
        self.slug = slugify(self.model_name)
        super(SourceModel, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.model_name

    def set_cached_file_paths(self, x):  # set cached file path
        self.cached_file_paths = json.dumps(x)

    def get_cached_file_paths(self):  # get cached file path
        return json.loads(self.cached_file_paths)


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
    aborted = models.BooleanField(default=False)
    gmm_model_path = models.CharField(max_length=128, default='')

    def save(self, *args, **kwargs):  # slugify before save
        self.slug = slugify(self.speaker_name)
        super(GoldenSpeaker, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.speaker_name

