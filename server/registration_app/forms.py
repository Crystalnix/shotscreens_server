from django import forms

from registration_app import fields as recaptcha_fields

from registration.forms import RegistrationForm

class RecaptchaRegistrationForm(RegistrationForm):
    recaptcha = recaptcha_fields.ReCaptchaField()