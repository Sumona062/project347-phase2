from django.shortcuts import render, redirect
from user.decorators import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
@show_to_company(allowed_roles=['admin', 'is_company'])
def post_job(request):
    form = PostJobForm()

    if request.method == 'POST':
        form = PostJobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            form.save()
            return redirect('company-profile', request.user.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('post-job')

    context = {
        'form': form
    }
    return render(request, 'job/post-job.html', context)


@login_required(login_url='login')
@show_to_company(allowed_roles=['admin', 'is_company'])
def edit_job(request, pk):
    job = JobModel.objects.get(id=pk)
    form = PostJobForm(instance=job)
    if request.method == 'POST':
        form = PostJobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            return redirect('job-profile', job.id)
        else:
            messages.error(request, 'There are a few problems')
            return redirect('edit-job', request.JobModel.id)

    context = {
        'form': form,
    }
    return render(request, 'job/post-job.html', context)


@login_required(login_url='login')
@show_to_company(allowed_roles=['admin', 'is_company'])
def delete_job(request, pk):
    job = JobModel.objects.get(id=pk)
    if request.method == 'POST':
        job.delete()
        return redirect('company-profile', request.user.id)

    context = {
        'item': job,
    }
    return render(request, 'job/delete-job.html', context)


@login_required(login_url='login')
def job_profile(request, pk):
    job = JobModel.objects.get(id=pk)

    try:
        applicant_applied = AppliedJobModel.objects.get(applicant=request.user, job=job)
    except:
        applicant_applied = None

    application_form = ApplicationForm()

    if request.method == 'POST':
        application_form = ApplicationForm(request.POST)
        if application_form.is_valid():
            application = application_form.save(commit=False)
            application.job = job
            application.applicant = request.user
            if applicant_applied is None:
                application.save()
                return redirect('job-profile', job.id)
            else:
                applicant_applied = AppliedJobModel.objects.get(applicant=request.user, job=job)
                applicant_applied.delete()
                return redirect('job-profile', job.id)



        else:
            messages.error(request, 'There are a few problems')
            return redirect('job-profile', job.id)

    context = {
        'job': job,
        'application_form': application_form,
        'applicant_applied': applicant_applied,
    }
    return render(request, 'job/job-profile.html', context)


@login_required(login_url='login')
@show_to_company(allowed_roles=['admin', 'is_company'])
def applicant_list(request, pk):
    job = JobModel.objects.get(id=pk)
    applications = AppliedJobModel.objects.filter(job=job)

    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'job/applicant-list.html', context)

