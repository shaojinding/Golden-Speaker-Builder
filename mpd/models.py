from __future__ import unicode_literals

from django.db import models
import os

# Create your models here.


class User(models.Model):
    username = models.CharField(unique=True, max_length=128)
    num_saved_recordings = models.IntegerField(default=0)
    wav_file_dir = models.CharField(max_length=128, default='')  # wav file parent directory
    transcription_dir = models.CharField(max_length=128, default='')  # wav file parent directory
    textgrid_dir = models.CharField(max_length=128, default='')  # wav file parent directory

    def __unicode__(self):
        return self.username

    def set_wav_file_dir(self, x):
        self.wav_file_dir = x
        if not os.path.exists(self.wav_file_dir):
            os.makedirs(self.wav_file_dir)

    def set_textgrid_dir(self, x):
        self.textgrid_dir = x
        if not os.path.exists(self.textgrid_dir):
            os.makedirs(self.textgrid_dir)

    def set_transcription_dir(self, x):
        self.transcription_dir = x
        if not os.path.exists(self.transcription_dir):
            os.makedirs(self.transcription_dir)
