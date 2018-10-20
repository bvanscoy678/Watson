from django.shortcuts import render, get_object_or_404
from .models import Post
from django.utils import timezone
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud.tone_analyzer_v3 import ToneInput
from watson_developer_cloud import LanguageTranslatorV3

language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    iam_apikey= '0bm9xWMc69mvjXffrTl_BUDv95fat4Jv9V_ogL4fUzOC',
    url= 'https://gateway.watsonplatform.net/language-translator/api'
)


service = ToneAnalyzerV3(
    # url is optional, and defaults to the URL below. Use the correct URL for your region.
    # url='https://gateway.watsonplatform.net/tone-analyzer/api',
    version= '2018-05-01',
    username='fbb1341f-7ab0-4110-a46f-f9d313bf8950',
    password='4Vq1ivAEZaMQ'
    )


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    names = []
    for post in posts:
        # Translate from English to French
        translation = language_translator.translate(
            text= post.text, model_id='en-fr').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']
        # IBM Tone Analyzer
        tone_input = post.text
        tone1 = service.tone(tone_input=tone_input, content_type="text/plain", sentances=False).get_result()
        tone2 = (json.dumps(tone1, indent=2))
        tone3 = json.loads(tone2)
        post.i = len(tone3['document_tone']['tones'])

        # tone details
        post.tone_s1 = tone3['document_tone']['tones'][0]['score']
        post.tone_n1 = tone3['document_tone']['tones'][0]['tone_name']
        post.tone_s2 = tone3['document_tone']['tones'][1]['score']
        post.tone_n2 = tone3['document_tone']['tones'][1]['tone_name']

        print("Tone count:  " + str(post.i))


    return render(request, 'blog/post_list.html', {'posts': posts })




def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
