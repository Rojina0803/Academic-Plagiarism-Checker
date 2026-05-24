from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import TextForm, UploadFileForm
from .forms import (
    CheckTextForm,
    UploadDocumentForm,
    CompareTextForm,
    CompareFilesForm,
    StyledUserCreationForm,
)
from django.contrib.auth import logout
from django.shortcuts import redirect

from .models import StoredDocument

from plagiarismchecker.utils.text_extractor import extract_text

from plagiarismchecker.algorithm.semantic_similarity import (
    detect_plagiarism
)

from plagiarismchecker.algorithm.webSearch import searchWeb

from nltk.tokenize import sent_tokenize
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from plagiarismchecker.forms import TextForm
from plagiarismchecker.algorithm.main import findSimilarity

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # ADMIN
            if user.is_superuser:
                return redirect('admin_dashboard')

            # NORMAL USER
            return redirect('landing')

    return render(
        request,
        'registration/login.html'
    )
@staff_member_required
def admin_dashboard(request):

    users = User.objects.all().count()

    reports = StoredDocument.objects.all().order_by('-created_at')

    total_reports = reports.count()

    high_risk = reports.filter(
        plagiarism_score__gte=70
    ).count()

    context = {
        'users': users,
        'reports': reports[:10],
        'total_reports': total_reports,
        'high_risk': high_risk,
    }

    return render(
        request,
        'pc/admin_dashboard.html',
        context
    )


@login_required
def home(request):
    return render(request, 'pc/landing.html')


def register_view(request):

    if request.method == 'POST':

        form = StyledUserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('landing')

    else:

        form = StyledUserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form
    })



# CHECK PASTED TEXT
@login_required
def test(request):

    result = None

    form = TextForm()

    if request.method == 'POST':

        form = TextForm(request.POST)

        if form.is_valid():

            text = form.cleaned_data['text']

            matches = []

            checked_links = set()

            # =========================
            # GOOGLE WEB CHECK
            # =========================

            sentences = sent_tokenize(text)

            for sentence in sentences[:15]:

                sentence = sentence.strip()

                if len(sentence.split()) < 4:
                    continue

                try:

                    output = {}

                    scores = {}

                    output, scores, _ = searchWeb(
                        sentence,
                        output,
                        scores
                    )

                    for link in output:

                        similarity = round(
                            scores.get(link, 0) * 100,
                            2
                        )

                        if similarity >= 8:

                            if link not in checked_links:

                                checked_links.add(link)

                                matches.append({

                                    'original': sentence,

                                    'matched': output[link]['snippet'],

                                    'similarity': similarity,

                                    'source': link
                                })

                except Exception as e:

                    print("TEXT WEB ERROR:")

                    print(e)

            # =========================
            # LOCAL DATABASE CHECK
            # =========================

            existing_docs = StoredDocument.objects.exclude(
                user=request.user
            )

            for doc in existing_docs:

                if not doc.content:
                    continue

                try:

                    semantic_result = detect_plagiarism(
                        text,
                        doc.content,
                        threshold=0.30
                    )

                    similarity = round(
                        semantic_result['overall_score'],
                        2
                    )

                    if similarity >= 25:

                        matches.append({

                            'original': text[:200],

                            'matched': (
                                f"Local Repository: "
                                f"{doc.filename}"
                            ),

                            'similarity': similarity
                        })

                except Exception as e:

                    print("TEXT LOCAL ERROR:")

                    print(e)

            # =========================
            # FINAL SCORE
            # =========================

            overall_score = 0

            if matches:

                overall_score = round(

                    sum(
                        match['similarity']
                        for match in matches
                    ) / len(matches),

                    2
                )

            if overall_score > 100:
                overall_score = 100

            result = {

                'overall_score': overall_score,

                'matches': matches
            }

    return render(
        request,
        'pc/check_text.html',
        {
            'form': form,
            'result': result
        }
    )



# FILE CHECK

@login_required
def filetest(request):

    result = None

    filename = None

    form = UploadDocumentForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and form.is_valid():

        uploaded_file = form.cleaned_data['docfile']

        filename = str(uploaded_file)

        value = extract_text(
            uploaded_file,
            filename
        )

        if value:

            sentences = sent_tokenize(value)

            total_sentences = 0

            matches = []

            checked_links = set()

            # =========================
            # GOOGLE WEB CHECK
            # =========================

            for sentence in sentences[:25]:

                sentence = sentence.strip()

                # Ignore weak sentences
                if len(sentence.split()) < 4:
                    continue

                if len(sentence) < 40:
                    continue

                total_sentences += 1

                try:

                    output = {}

                    scores = {}

                    output, scores, _ = searchWeb(
                        sentence,
                        output,
                        scores
                    )

                    for link in output:

                        similarity = round(
                            scores.get(link, 0) * 100,
                            2
                        )

                        # Detection threshold
                        if similarity >= 8:

                            if link not in checked_links:

                                checked_links.add(link)

                                matches.append({

                                    'original': sentence,

                                    'matched': link,

                                    'similarity': similarity
                                })

                except Exception as e:

                    print("WEB CHECK ERROR:")

                    print(e)

            # =========================
            # LOCAL DATABASE CHECK
            # =========================

            existing_docs = StoredDocument.objects.exclude(
                user=request.user
            )

            for doc in existing_docs:

                if not doc.content:
                    continue

                try:

                    semantic_result = detect_plagiarism(
                        value,
                        doc.content,
                        threshold=0.30
                    )

                    similarity = round(
                        semantic_result['overall_score'],
                        2
                    )

                    if similarity >= 25:

                        matches.append({

                            'original': filename,

                            'matched': (
                                f"Local Repository: "
                                f"{doc.filename}"
                            ),

                            'similarity': similarity
                        })

                except Exception as e:

                    print("LOCAL DB ERROR:")

                    print(e)

            # =========================
            # FINAL SCORE
            # =========================

            overall_score = 0

            if matches:

                overall_score = round(

                    sum(
                        match['similarity']
                        for match in matches
                    ) / len(matches),

                    2
                )

            # Limit impossible score
            if overall_score > 100:
                overall_score = 100

            result = {

                'overall_score': overall_score,

                'matches': matches
            }

            # =========================
            # SAVE HISTORY
            # =========================

            if request.user.is_authenticated:

                StoredDocument.objects.create(

                    user=request.user,

                    filename=filename,

                    content=value,

                    overall_similarity_score=overall_score,

                    risk_level=(

                        'high'

                        if overall_score >= 70

                        else 'medium'

                        if overall_score >= 40

                        else 'low'
                    )
                )

    return render(

        request,

        'pc/upload.html',

        {

            'form': form,

            'result': result,

            'filename': filename,
        }
    )


# COMPARE PAGE

@login_required
def fileCompare(request):

    text_form = CompareTextForm()

    files_form = CompareFilesForm()

    return render(request, 'pc/compare.html', {
        'text_form': text_form,
        'files_form': files_form,
    })



# TEXT VS TEXT

@login_required
def twofiletest1(request):

    result = None

    text_form = CompareTextForm(
        request.POST or None
    )

    files_form = CompareFilesForm()

    if request.method == 'POST' and text_form.is_valid():

        text1 = text_form.cleaned_data['q1'].strip()

        text2 = text_form.cleaned_data['q2'].strip()

        if text1 and text2:

            result = detect_plagiarism(
                text1,
                text2
            )

    return render(request, 'pc/compare.html', {
        'text_form': text_form,
        'files_form': files_form,
        'result': result,
    })



# FILE VS FILE

@login_required
def twofilecompare1(request):

    result = None

    text_form = CompareTextForm()

    files_form = CompareFilesForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and files_form.is_valid():

        file1 = files_form.cleaned_data['docfile1']

        file2 = files_form.cleaned_data['docfile2']

        text1 = extract_text(
            file1,
            str(file1)
        )

        text2 = extract_text(
            file2,
            str(file2)
        )

        if text1 and text2:

            result = detect_plagiarism(
                text1,
                text2
            )

    return render(request, 'pc/compare.html', {
        'text_form': text_form,
        'files_form': files_form,
        'result': result,
    })



# DASHBOARD


@login_required
def dashboard(request):

    reports = StoredDocument.objects.filter(
        user=request.user
    )

    total_checked = reports.count()

    avg_similarity = 0

    if total_checked > 0:

        avg_similarity = round(
            sum(
                r.overall_similarity_score
                for r in reports
            ) / total_checked,
            2
        )

    return render(request, 'pc/dashboard.html', {
        'total_documents': total_checked,
        'avg_similarity': avg_similarity,
        'total_checked': total_checked,
        'remaining_checks': 999,
        'risk_counts': {
            'low': reports.filter(risk_level='low').count(),
            'medium': reports.filter(risk_level='medium').count(),
            'high': reports.filter(risk_level='high').count(),
            'total': total_checked,
        },
        'recent_reports': reports.order_by('-id')[:5],
    })



# HISTORY


@login_required
def history(request):

    reports = StoredDocument.objects.filter(
        user=request.user
    ).order_by('-id')

    q = request.GET.get('q', '')

    risk = request.GET.get('risk', '')

    if q:

        reports = reports.filter(
            filename__icontains=q
        )

    if risk:

        reports = reports.filter(
            risk_level=risk
        )

    return render(request, 'pc/history.html', {
        'reports': reports,
        'q': q,
        'risk': risk
    })


@login_required
def profile(request):

    reports = StoredDocument.objects.filter(
        user=request.user
    )

    count = reports.count()

    avg_similarity = 0

    if count > 0:

        avg_similarity = round(
            sum(
                r.overall_similarity_score
                for r in reports
            ) / count,
            2
        )

    return render(request, 'pc/profile.html', {
        'report_count': count,
        'avg_similarity': avg_similarity,
    })


@login_required
def report_detail(request, report_id):

    report = StoredDocument.objects.get(
        id=report_id,
        user=request.user
    )

    return render(request, 'pc/report_detail.html', {
        'report': report
    })

def logoutUser(request):

    logout(request)

    return redirect('login')