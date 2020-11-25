from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from job.models import JobModel, AppliedJobModel
from .decorators import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .filters import JobFilter
import math


@unauthenticated_user
def home(request):
    applicants = User.objects.filter(is_applicant=True)
    companies = User.objects.filter(is_company=True)
    jobs = JobModel.objects.filter()
    context = {
        'applicants': applicants,
        'applicants_len': applicants.count(),
        'companies': companies,
        'companies_len': companies.count(),
        'jobs': jobs,
        'jobs_len': jobs.count(),
    }
    return render(request, 'user/index.html', context)


@unauthenticated_user
def login_page(request):
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user and user.is_applicant:
                login(request, user)
                return redirect('applicant-feed')
            elif user and user.is_company:
                login(request, user)
                return redirect('company-profile', user.id)
            else:
                messages.error(request, 'Username or Password is incorrect.')
        # else:
        #     return render(request, 'user/login.html', {'form': form})
    form = LoginForm()
    context = {
        'form': form
    }
    return render(request, 'user/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


@unauthenticated_user
def applicant_register(request):
    if request.method == 'POST':
        form = ApplicantRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            ApplicantProfileModel.objects.create(user=user)
            messages.success(request, "Account created successfully.")
            return redirect('applicant-feed')

    form = ApplicantRegistrationForm()
    context = {
        "form": form
    }
    return render(request, 'user/applicant/applicant-register.html', context)


@unauthenticated_user
def company_register(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            CompanyProfileModel.objects.create(user=user)
            messages.success(request, "Account created successfully.")
            return redirect('company-profile', user.id)

    form = CompanyRegistrationForm()
    context = {
        "form": form
    }
    return render(request, 'user/company/company-register.html', context)


def match_skill(job_list, skill_list):
    # print(job_list)
    recomendation_list = []
    for skill in skill_list:
        for job in job_list:
            split_text = skill.skill_title.lower().split(' ')

            for s in split_text:

                index = job.requirements.lower().find(s)
                if (index >= 0) and job not in recomendation_list:
                    recomendation_list.append(job)

    return recomendation_list


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def applicant_feed(request):
    applicants = User.objects.filter(is_applicant=True)
    companies = User.objects.filter(is_company=True)

    recommended_job_list = JobModel.objects.all()
    skill_set = SkillSetModel.objects.filter(user=request.user)

    job_list = JobModel.objects.all().order_by('id')


    myFilter = JobFilter(request.GET, queryset=job_list)
    job_list = myFilter.qs

    page = request.GET.get('page', 1)
    paginator = Paginator(job_list, 5)

    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    context = {
        'applicants': applicants,
        'applicants_len': applicants.count(),
        'companies': companies,
        'companies_len': companies.count(),
        'jobs': jobs,
        'job_list': job_list,
        'jobs_len': job_list.count(),
        'myFilter': myFilter,
        'recommended_job_list': recommended_job_list,
        'skill_set': skill_set
    }
    return render(request, 'user/applicant/applicant-feed.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def applicant_profile(request, pk):
    user = User.objects.get(id=pk)
    skill_set = SkillSetModel.objects.filter(user=user)
    work_experience = WorkExperienceModel.objects.filter(user=user)
    educations = EducationModel.objects.filter(user=user)
    references = ReferenceModel.objects.filter(user=user)
    awards = AwardModel.objects.filter(user=user)
    applied_jobs = AppliedJobModel.objects.filter(applicant=user)

    context = {
        'user': user,
        'skill_set': skill_set,
        'work_experience': work_experience,
        'educations': educations,
        'references': references,
        'awards': awards,
        'applied_jobs': applied_jobs,
    }
    return render(request, 'user/applicant/applicant-profile.html', context)


@login_required(login_url='login')
def applicant_public_profile(request, pk):
    user = User.objects.get(id=pk)
    skill_set = SkillSetModel.objects.filter(user=user)
    work_experience = WorkExperienceModel.objects.filter(user=user)
    educations = EducationModel.objects.filter(user=user)
    references = ReferenceModel.objects.filter(user=user)
    awards = AwardModel.objects.filter(user=user)

    context = {
        'user': user,
        'skill_set': skill_set,
        'work_experience': work_experience,
        'educations': educations,
        'references': references,
        'awards': awards,
    }
    return render(request, 'user/applicant/applicant-public-profile.html', context)


@login_required(login_url='login')
def company_profile(request, pk):
    applicants = User.objects.filter(is_applicant=True)
    companies = User.objects.filter(is_company=True)
    user = User.objects.get(id=pk)
    job_list = JobModel.objects.filter(user=user)

    context = {
        'user': user,
        'applicants': applicants,
        'applicants_len': applicants.count(),
        'companies': companies,
        'companies_len': companies.count(),
        'job_list': job_list,
    }
    return render(request, 'user/company/company-profile.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def applicant_edit_profile(request):
    applicant = request.user.applicantprofilemodel
    form = ApplicantEditProfileForm(instance=applicant)
    if request.method == 'POST':
        form = ApplicantEditProfileForm(request.POST, request.FILES, instance=applicant)
        if form.is_valid():
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('applicant-edit-profile')

    context = {
        'form': form,
    }
    return render(request, 'user/applicant/applicant-edit-profile.html', context)


@login_required(login_url='login')
@show_to_company(allowed_roles=['admin', 'is_company'])
def company_edit_profile(request):
    company = request.user.companyprofilemodel
    form = CompanyEditProfileForm(instance=company)
    if request.method == 'POST':
        form = CompanyEditProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('company-edit-profile')

    context = {
        'form': form,
    }
    return render(request, 'user/company/company-edit-profile.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def add_experience(request):
    form = WorkExperienceForm()
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save()
            experience.user = request.user
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('add-experience')

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-experience.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def edit_experience(request, pk):
    experience = WorkExperienceModel.objects.get(id=pk)
    form = WorkExperienceForm(instance=experience)
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('edit-experience', request.workexperiencemodel.id)

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-experience.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def delete_experience(request, pk):
    experience = WorkExperienceModel.objects.get(id=pk)
    if request.method == 'POST':
        experience.delete()
        return redirect('applicant-profile', request.user.id)

    context = {
        'item': experience,
    }
    return render(request, 'user/applicant-details/delete-experience.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def add_education(request):
    form = EducationForm()
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('add-education')

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-education.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def edit_education(request, pk):
    education = EducationModel.objects.get(id=pk)
    form = EducationForm(instance=education)
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('edit-education', request.educationmodel.id)

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-education.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def delete_education(request, pk):
    education = EducationModel.objects.get(id=pk)
    if request.method == 'POST':
        education.delete()
        return redirect('applicant-profile', request.user.id)

    context = {
        'item': education,
    }
    return render(request, 'user/applicant-details/delete-education.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def add_skill(request):
    form = SkillSetForm()
    if request.method == 'POST':
        form = SkillSetForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('add-skill')

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-skill.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def edit_skill(request, pk):
    skill = SkillSetModel.objects.get(id=pk)
    form = SkillSetForm(instance=skill)
    if request.method == 'POST':
        form = SkillSetForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('edit-skill', request.skillsetmodel.id)

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-skill.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def delete_skill(request, pk):
    skill = SkillSetModel.objects.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        return redirect('applicant-profile', request.user.id)

    context = {
        'item': skill,
    }
    return render(request, 'user/applicant-details/delete-skill.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def add_reference(request):
    form = ReferenceForm()
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            reference = form.save()
            reference.user = request.user
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('add-reference')

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-reference.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def edit_reference(request, pk):
    reference = ReferenceModel.objects.get(id=pk)
    form = ReferenceForm(instance=reference)
    if request.method == 'POST':
        form = ReferenceForm(request.POST, instance=reference)
        if form.is_valid():
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('edit-reference', request.referencemodel.id)

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-reference.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def delete_reference(request, pk):
    reference = ReferenceModel.objects.get(id=pk)
    if request.method == 'POST':
        reference.delete()
        return redirect('applicant-profile', request.user.id)

    context = {
        'item': reference,
    }
    return render(request, 'user/applicant-details/delete-reference.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def add_award(request):
    form = AwardForm()
    if request.method == 'POST':
        form = AwardForm(request.POST)
        if form.is_valid():
            award = form.save()
            award.user = request.user
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('add-award')

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-award.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def edit_award(request, pk):
    award = AwardModel.objects.get(id=pk)
    form = AwardForm(instance=award)
    if request.method == 'POST':
        form = AwardForm(request.POST, instance=award)
        if form.is_valid():
            form.save()
            return redirect('applicant-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('edit-award', request.awardmodel.id)

    context = {
        'form': form,
    }
    return render(request, 'user/applicant-details/add-edit-award.html', context)


@login_required(login_url='login')
@show_to_applicant(allowed_roles=['admin', 'is_applicant'])
def delete_award(request, pk):
    award = AwardModel.objects.get(id=pk)
    if request.method == 'POST':
        award.delete()
        return redirect('applicant-profile', request.user.id)

    context = {
        'item': award,
    }
    return render(request, 'user/applicant-details/delete-award.html', context)



def about(request):
    applicants = User.objects.filter(is_applicant=True)
    companies = User.objects.filter(is_company=True)
    jobs = JobModel.objects.filter()

    context = {
        'applicants': applicants,
        'applicants_len': applicants.count(),
        'companies': companies,
        'companies_len': companies.count(),
        'jobs': jobs,
        'jobs_len': jobs.count(),
    }
    return render(request, 'user/about.html', context)


def contact(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email_add = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        send_mail(

            subject + "  from " + email_add,
            message,
            email_add,

            ['officialjobland777@gmail.com', ],
            # the mail adddress that the email will be sent to
        )
        messages.success(request, "Feedback sent successfully.")

        return render(request, 'user/contact.html', {})
    else:
        return render(request, 'user/contact.html', {})
