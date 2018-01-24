from django.test import TestCase
from speech.models import User, AnchorSet, Recording, Anchor, SourceModel, GoldenSpeaker, Utterance
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from .forms import AnchorSetForm
import base64
import json
import os


class UserMethodTest(TestCase):
    def test_user_creating(self):
        a = User.objects.create(user_name='a')
        self.assertTrue(isinstance(a, User))
        self.assertEqual(a.__unicode__(), a.user_name)

    def test_ensure_username_is_unique(self):
        User.objects.create(user_name='a')
        with self.assertRaises(IntegrityError):
            User.objects.create(user_name='a')

class AnchorSetMethodTest(TestCase):
    def test_anchorset_creating(self):
        u = User.objects.create(user_name='a')
        a = AnchorSet.objects.create(anchor_set_name='b', user=u, active=False, used=False, completed=False)
        self.assertTrue(isinstance(a, AnchorSet))
        self.assertEqual(a.__unicode__(), a.anchor_set_name)

    # def test_ensure_anchor_set_name_is_unique(self):
    #     u = User.objects.create(user_name='a')
    #     AnchorSet.objects.create(anchor_set_name='b', user=u, active=False, used=False, completed=False)
    #     with self.assertRaises(IntegrityError):
    #         AnchorSet.objects.create(anchor_set_name='b', user=u)

    def test_slug_line_creation(self):
        u = User.objects.create(user_name='a')
        a = AnchorSet.objects.create(anchor_set_name='a b c', user=u, active=False, used=False, completed=False)
        a.save()
        self.assertEqual(a.slug, 'a-b-c')

    def test_active_is_bool(self):
        u = User.objects.create(user_name='a')
        with self.assertRaises(ValidationError):
            a = AnchorSet.objects.create(anchor_set_name='a b c', user=u, active=123, used=False, completed=False)

    def test_used_is_bool(self):
        u = User.objects.create(user_name='a')
        with self.assertRaises(ValidationError):
            a = AnchorSet.objects.create(anchor_set_name='a b c', user=u, active=False, used=123, completed=False)

    def test_completed_is_bool(self):
        u = User.objects.create(user_name='a')
        with self.assertRaises(ValidationError):
            a = AnchorSet.objects.create(anchor_set_name='a b c', user=u, active=False, used=False, completed=123)

    def test_set_phonemes(self):
        u = User.objects.create(user_name='a')
        a = AnchorSet.objects.create(anchor_set_name='a b c', user=u, active=False, used=False, completed=False)
        a.set_saved_phonemes('a b c')
        self.assertEqual(a.saved_phonemes, '"a b c"')

    def test_get_phonemes(self):
        u = User.objects.create(user_name='a')
        a = AnchorSet.objects.create(anchor_set_name='a b c', user=u, active=False, used=False, completed=False, saved_phonemes='"a b c"')
        x = a.get_saved_phonemes()
        self.assertEqual(x, 'a b c')


class RecordingMethodTest(TestCase):
    def test_recording_creating(self):
        u = User.objects.create(user_name='a')
        a = AnchorSet.objects.create(anchor_set_name='b', user=u, active=False, used=False, completed=False)
        aa = Anchor.objects.create(phoneme='a', anchor_set=a)
        r = Recording.objects.create(record_name='1', phoneme='a', user=u, anchor=aa)
        self.assertTrue(isinstance(r, Recording))
        self.assertEqual(r.__unicode__(), r.record_name)

    def test_ensure_anchor_set_name_is_unique(self):
        u = User.objects.create(user_name='a')
        a = AnchorSet.objects.create(anchor_set_name='b', user=u, active=False, used=False, completed=False)
        aa = Anchor.objects.create(phoneme='a', anchor_set=a)
        Recording.objects.create(record_name='1', phoneme='a', user=u, anchor=aa)
        with self.assertRaises(IntegrityError):
            Recording.objects.create(record_name='1', phoneme='a', user=u, anchor=aa)


class AnchorMethodTest(TestCase):
    def test_anchor_creating(self):
        u = User.objects.create(user_name='a')
        # r = Recording.objects.create(record_name='1', phoneme='a', user=u)
        a = AnchorSet.objects.create(anchor_set_name='b', user=u, active=False, used=False, completed=False)
        aa = Anchor.objects.create(phoneme='a', anchor_set=a)
        self.assertTrue(isinstance(aa, Anchor))


class SourceModelMethodTest(TestCase):
    def test_source_model_creating(self):
        s = SourceModel.objects.create(model_name='a b c')
        self.assertTrue(isinstance(s, SourceModel))
        self.assertEqual(s.__unicode__(), s.model_name)
        s.save()
        self.assertEqual(s.slug, 'a-b-c')

    def test_slug_creating(self):
        s = SourceModel.objects.create(model_name='a b c')
        s.save()
        self.assertEqual(s.slug, 'a-b-c')


class UtteranceMethodTest(TestCase):
    def test_utterance_model_creating(self):
        s = SourceModel.objects.create(model_name='a b c')
        u = Utterance.objects.create(source_model=s, name='qwer')
        self.assertTrue(isinstance(u, Utterance))
        self.assertEqual(u.__unicode__(), u.name)


class GoldenSpeakerMethodTest(TestCase):
    def test_golden_speaker_model_creating(self):
        uu = User.objects.create(user_name='u')
        a = AnchorSet.objects.create(anchor_set_name='b', user=uu, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        g = GoldenSpeaker.objects.create(speaker_name='a b c', anchor_set=a, source_model=s, user=uu)
        g.save()
        self.assertTrue(isinstance(g, GoldenSpeaker))
        self.assertEqual(g.__unicode__(), g.speaker_name)


    def test_slug_creating(self):
        uu = User.objects.create(user_name='u')
        a = AnchorSet.objects.create(anchor_set_name='b', user=uu, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        g = GoldenSpeaker.objects.create(speaker_name='a b c', anchor_set=a, source_model=s, user=uu)
        g.save()
        self.assertEqual(g.slug, 'a-b-c')

    def test_speaker_name_unique(self):
        uu = User.objects.create(user_name='u')
        a = AnchorSet.objects.create(anchor_set_name='b', user=uu, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        g = GoldenSpeaker.objects.create(speaker_name='a b c', anchor_set=a, source_model=s, user=uu)
        with self.assertRaises(IntegrityError):
            g = GoldenSpeaker.objects.create(speaker_name='a b c', anchor_set=a, source_model=s, user=uu)


class AnchorSetFormTests(TestCase):
    def test_valid_data(self):
        form = AnchorSetForm({
            'anchor_set_name': "test",
        })
        self.assertTrue(form.is_valid())
        anchor_set = form.save(commit=False)
        self.assertEqual(anchor_set.anchor_set_name, "test")

    # def test_blank_data(self):
    #     form = AnchorSetForm({})
    #     self.assertFalse(form.is_valid())
    #     self.assertEqual(form.errors, {
    #         'anchor_set_name': ['This field is required.'],
    #     })


class IndexViewTests(TestCase):
    def test_index_view_using_html(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'speech/index.html')

    def test_index_view_without_login(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertEqual('profile' not in session, True)
        self.assertContains(response, 'Login')

    def test_index_view_with_login(self):
        session = self.client.session
        session['profile'] = {'nickname': 'burning'}
        session.save()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual('profile' in session, True)
        self.assertContains(response, 'Welcome')


class ManageAnchorSetViewTests(TestCase):
    def test_manage_anchor_set_view_using_html(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        a = AnchorSet.objects.create(anchor_set_name='bbb', user=u, active=False, used=False, completed=False)
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session.save()
        response = self.client.get(reverse('manage_anchorset'))
        self.assertTemplateUsed(response, 'speech/manage_anchorset.html')

    def test_manage_anchor_set_view(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        a = AnchorSet.objects.create(anchor_set_name='bbb', user=u, active=False, used=False, completed=False)
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session.save()
        response = self.client.get(reverse('manage_anchorset'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bbb')
        num_anchorsets = len(response.context['anchorsets'])
        self.assertEqual(num_anchorsets, 1)


# class AnchorSetViewTests(TestCase):
#     def test_anchor_set_view_using_html(self):
#         u = User.objects.create(user_name='shjd')  # setup user before log in
#         # r = Recording.objects.create(record_name='1', phoneme='a', user=u)
#         a = AnchorSet.objects.create(anchor_set_name='a b c', user=u, active=False, used=False, completed=False)
#         # aa = Anchor.objects.create(recording=r, anchor_set=a)
#         a.set_saved_phonemes("[]")
#         a.save()
#         session = self.client.session
#         session['profile'] = {'nickname': 'shjd'}
#         session.save()
#         response = self.client.get(reverse('anchorset', args=['a-b-c']))
#         self.assertTemplateUsed(response, 'speech/anchorset.html')
#
#     def test_anchor_set_view(self):
#         u = User.objects.create(user_name='shjd')  # setup user before log in
#         # r = Recording.objects.create(record_name='1', phoneme='a', user=u)
#         a = AnchorSet.objects.create(anchor_set_name='a b c', user=u, active=False, used=False, completed=False)
#         # aa = Anchor.objects.create(recording=r, anchor_set=a)
#         a.set_saved_phonemes("[]")
#         a.save()
#         session = self.client.session
#         session['profile'] = {'nickname': 'shjd'}
#         session.save()
#         response = self.client.get(reverse('anchorset', args=['a-b-c']))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.context['anchor_set_name'], 'a b c')
#         num_anchors = len(response.context['anchors'])
#         self.assertEqual(num_anchors, 1)
#         self.assertEqual(response.context['saved_phonemes'], '"[]"')


class AddAnchorSetViewTests(TestCase):
    def test_add_anchor_set_view_using_html(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session.save()
        response = self.client.get(reverse('add_anchorset'))
        self.assertTemplateUsed(response, 'speech/add_anchorset.html')

    def test_add_anchor_set_get_view(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session.save()
        response = self.client.get(reverse('add_anchorset'))
        self.assertEqual(response.status_code, 200)


class DeleteAnchorSetViewTests(TestCase):
    def test_delete_anchor_set_view(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session['current_anchorset'] = 'abc'
        session.save()
        a = AnchorSet.objects.create(anchor_set_name='abc', user=u, active=False, used=False, completed=False)
        response = self.client.get(reverse('start_record_session', args={'abc'}))
        session = self.client.session
        self.assertEqual(response.status_code, 302)
        # self.assertEqual('current_anchorset' not in session, True)


class StartRecordSessionViewTests(TestCase):
    def test_start_record_session_view(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session.save()
        response = self.client.get(reverse('start_record_session', args={'abc'}))
        session = self.client.session
        self.assertEqual(response.status_code, 302)
        self.assertEqual(session['current_anchorset'], 'abc')


class RecordViewTests(TestCase):
    def test_add_anchor_set_view_using_html(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session['current_anchorset'] = 'abc'
        session.save()
        a = AnchorSet.objects.create(anchor_set_name='abc', user=u, active=False, used=False, completed=False)
        a.set_saved_phonemes([])
        a.save()
        response = self.client.get(reverse('record', args={'index'}))
        self.assertTemplateUsed(response, 'speech/record.html')

    def test_record_view_without_saved_phonemes(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session['current_anchorset'] = 'abc'
        session.save()
        a = AnchorSet.objects.create(anchor_set_name='abc', user=u, active=False, used=False, completed=False)
        a.set_saved_phonemes([])
        a.save()
        response = self.client.get(reverse('record', args={'index'}))
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['name'], 'shjd')
        self.assertEqual(response.context['is_login'], True)
        self.assertEqual(response.context['phoneme'], 'index')
        self.assertEqual(response.context['saved_phoneme'], '[]')
        self.assertEqual(response.context['completed'], False)

    def test_record_view_with_saved_phonemes(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session['current_anchorset'] = 'abc'
        session.save()
        a = AnchorSet.objects.create(anchor_set_name='abc', user=u, active=False, used=False, completed=False)
        a.set_saved_phonemes(['b'])
        a.save()
        aa = Anchor.objects.create(phoneme='a', anchor_set=a)
        aa = Anchor.objects.create(anchor_set=a, phoneme='b', L=0.1, C=0.2, R=0.3)
        r = Recording.objects.create(record_name='shjd_copy_test_AA', phoneme='AA', user=u, anchor=aa)
        with open("data/recordings/shjd_copy_test_AA.wav", "rb") as recording_file:
            recording_blob = recording_file.read()
        recording_base64 = base64.b64encode(recording_blob)
        json_record_details = json.dumps([aa.L, aa.R, aa.C, recording_base64])
        response = self.client.get(reverse('record', args={'b'}))
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['name'], 'shjd')
        self.assertEqual(response.context['is_login'], True)
        self.assertEqual(response.context['phoneme'], 'b')
        self.assertEqual(response.context['saved_phoneme'], '["b"]')
        self.assertEqual(response.context['completed'], False)
        self.assertEqual(response.context['record_details'], json_record_details)

# cannot establish all save_phoneme, so it's hard to test
# class FinishRecordSessionViewTests(TestCase):
#     def test_finish_record_view_without_saved_pitch(self):


# cannot test with celery, also cannot prepare for the data needed to be fed
# class BuildSabrViewTests(TestCase):


# cannot test upload functions, hard to prepare the json
# class UploadAnnotationViewTests(TestCase):


# cannot test upload functions, hard to prepare the json
# class UploadPitchViewTests(TestCase):


class BuildAndSynthesizeViewTests(TestCase):
    def build_and_synthesize_view_test_using_html(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session.save()
        a = AnchorSet.objects.create(anchor_set_name='abc', user=u, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        u = Utterance.objects.create(source_model=s, name='qwer')
        response = self.client.get(reverse('build_synthesize'))
        self.assertTemplateUsed(response, 'speech/build_synthesize.html')

    def build_and_synthesize_view_test(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session.save()
        a = AnchorSet.objects.create(anchor_set_name='abc', user=u, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        u = Utterance.objects.create(source_model=s, name='qwer')
        response = self.client.get(reverse('build_synthesize'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['name'], 'shjd')
        self.assertEqual(response.context['is_login'], True)
        source_model = response.context['source_model']
        source_model_num = len(source_model)
        self.assertEqual(source_model_num, 1)
        anchor_sets = response.context['anchor_sets']
        anchor_sets_num = len(anchor_sets)
        self.assertEqual(anchor_sets_num, 1)
        utt = response.context['utterances']
        utt_num = len(utt)
        self.assertEqual(utt_num, 1)


class GetUtterancesViewTests(TestCase):
    def test_get_utterance_view(self):
        u = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        session.save()
        s = SourceModel.objects.create(model_name='a b c')
        u = Utterance.objects.create(source_model=s, name='qwer', transcription='abcdefg')
        response = self.client.get('/speech/get_utterances/?source_model=a-b-c')
        self.assertEqual(response.status_code, 200)


class PracticeViewTests(TestCase):
    def test_practice_view_using_html(self):
        uu = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        a = AnchorSet.objects.create(anchor_set_name='b', user=uu, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        g = GoldenSpeaker.objects.create(speaker_name='a b c', anchor_set=a, source_model=s, user=uu)
        session.save()
        response = self.client.get(reverse('practice', args={'index'}))
        self.assertTemplateUsed(response, 'speech/practice.html')

    def test_practice_view_index(self):
        uu = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        a = AnchorSet.objects.create(anchor_set_name='b', user=uu, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        g = GoldenSpeaker.objects.create(speaker_name='a b c', anchor_set=a, source_model=s, user=uu)
        session.save()
        response = self.client.get(reverse('practice', args={'index'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['if_choose'], True)
        gs = response.context['golden_speakers']
        gs_num = len(gs)
        self.assertEqual(gs_num, 1)

    def test_practice_view_not_index(self):
        uu = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        a = AnchorSet.objects.create(anchor_set_name='b', user=uu, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        g = GoldenSpeaker.objects.create(speaker_name='a b c', anchor_set=a, source_model=s, user=uu)
        session.save()
        response = self.client.get(reverse('practice', args={'a-b-c'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['if_choose'], False)
        gs = response.context['gs']
        self.assertEqual(gs.speaker_name, 'a b c')
        self.assertEqual(response.context['cwd'], os.getcwd())


class DeleteGoldenSpeakerViewTest(TestCase):
    def test_delete_golden_speaker_view(self):
        uu = User.objects.create(user_name='shjd')  # setup user before log in
        session = self.client.session
        session['profile'] = {'nickname': 'shjd'}
        a = AnchorSet.objects.create(anchor_set_name='b', user=uu, active=False, used=False, completed=False)
        s = SourceModel.objects.create(model_name='a b c')
        g = GoldenSpeaker.objects.create(speaker_name='a b c', anchor_set=a, source_model=s, user=uu)
        session.save()
        response = self.client.get(reverse('delete_golden_speaker', args={'a-b-c'}))
        self.assertEqual(response.status_code, 302)