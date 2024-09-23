from django.contrib import admin
from meta.models import FAQ, About, WhoWeAre, Philosophy, PrivacyPolicy, TermsAndCondition
# Register your models here.
admin.site.register(About)
admin.site.register(WhoWeAre)
admin.site.register(Philosophy)
admin.site.register(FAQ)
admin.site.register(PrivacyPolicy)
admin.site.register(TermsAndCondition)