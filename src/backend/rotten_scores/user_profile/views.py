from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from .forms import ChangePersonalDataForm, ChangePasswordForm


def my_rating_and_reviews(request):
    return render(request, 'profile/base_profile.html')


def custom_logout(request):
    if request.user.is_authenticated:
        # Получаем текущего пользователя и вызываем его метод logout
        user = request.user
        user.logout()

        # Очищаем сессию
        request.session.flush()

    return redirect('core:homepage')


def load_section(request):
    section = request.GET.get('section', 'profile')

    section_mapping = {
        'ratings': 'ratings.html',
        'account': 'account.html',
        'statistics': 'statistics.html',
        'admin': 'admin.html'
    }

    template_name = f'profile/sections/{section_mapping.get(section, "ratings.html")}'

    try:
        return render(request, template_name)
    except:
        return HttpResponseNotFound("Section not found")


class MyAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/base_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personal_form'] = ChangePersonalDataForm(user=self.request.user, initial={
            'username': self.request.user.username,
            'email': self.request.user.email
        })
        context['password_form'] = ChangePasswordForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')

        if form_type == 'personal':
            form = ChangePersonalDataForm(request.POST, user=request.user)
        elif form_type == 'password':
            form = ChangePasswordForm(request.POST, user=request.user)
        else:
            messages.error(request, "Invalid form type")
            return self.get(request, *args, **kwargs)  # Показываем форму заново

        if form.is_valid():
            form.save()
            return redirect(f"{request.path}?section=account")
        else:
            messages.error(request, f"Please correct the errors in the {form_type} form.")

            context = self.get_context_data()
            if form_type == 'personal':
                context['personal_form'] = form
            elif form_type == 'password':
                context['password_form'] = form

            return self.render_to_response(context)


def statistics(request):
    return HttpResponse("Заглушка")
def admin_panel(request):
    return HttpResponse("Заглушка")