from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^debug/(.*)/$', 'projectApp1.views.debug_helper_funcs'),
    (r'^$',   RedirectView.as_view(url='/login/')),
    (r'^login/$', 'projectApp1.views.siteLogin'),
    (r'^createUser/', 'projectApp1.views.createUser'),
    (r'^createGroup/', 'projectApp1.views.createGroup'),
    (r'^createGroupForm/$', 'projectApp1.views.createGroupForm'),
    (r'^home/$', 'projectApp1.views.home'),
    (r'^settings/$', 'projectApp1.views.settings'),
    (r'^permission/(\w+)/(enable|dissable)/$', 'projectApp1.views.enableDissablePermissions'),
    (r'^group/(\d+)/$', 'projectApp1.views.groupHome'),
    (r'^invite/(accept|decline)/(\d+)/$', 'projectApp1.views.changeInvite'),
    (r'^allInvites/$', 'projectApp1.views.showInvites'),
    (r'^allNotifications/$', 'projectApp1.views.showNotifications'),
    (r'^getJSON/users/$', 'projectApp1.views.getJSONusers'),
    (r'^deleteGroup/(\d+)/$', 'projectApp1.views.deleteGroup'),
    (r'^sentInvites/(\d+)/$', 'projectApp1.views.sentInvites'),
    (r'^changeGroup/(\d+)/$', 'projectApp1.views.changeGroup'),
    (r'^authorize/$', 'projectApp1.views.authorize'),


    (r'^email/$', 'TransactionApp.views.emailFunc'),
    (r'^csv/$', 'TransactionApp.views.csvFunc'),
    (r'^calculator/(.*)/$', 'TransactionApp.views.calculator'),
    (r'^onlineApp/$', 'TransactionApp.views.onlineApp'),
    (r'^transaction/(\d+)/$', 'TransactionApp.views.displaySingleTransaction'),
    (u'^transactionForm/$', 'TransactionApp.views.displayTransactionForm'),
    (u'^editTransactionForm/$', 'TransactionApp.views.editTransactionForm'),
    (u'^editTransaction/$', 'TransactionApp.views.editTransaction'),
    (r'^makeTransaction/$', 'TransactionApp.views.makeTransaction'),
    (r'^deleteTransaction/$', 'TransactionApp.views.deleteTransaction'),
    (r'^createCategory/(\d+)/$', 'TransactionApp.views.createCategory'),
    (r'^getJSONcategories/$', 'TransactionApp.views.getJSONcategories'),
    (r'^personal/statistics/$', 'TransactionApp.views.personalStatistics'),
    (r'^personal/transactionList/$', 'TransactionApp.views.personalTransactionList'),
    (r'^group/statistics/$', 'TransactionApp.views.groupStatistics'),
    (r'^group/transactionList/$', 'TransactionApp.views.groupTransactionList'),
    (r'^group/expenseList/$', 'TransactionApp.views.groupExpenseList'),
    (r'^group/outstandingList/$', 'TransactionApp.views.groupOutstandingList'),
    (r'^group/paidList/$', 'TransactionApp.views.groupPaidList'),
    (r'^group/settle/$', 'TransactionApp.views.groupSettle'),
    (r'^sanitize/$', 'TransactionApp.views.sanitize'),
    (r'^transactionHistory/$', 'TransactionApp.views.transactionHistory'),

    (r'^import/$', 'TransactionApp.views.import_from_json'),

    (r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/login/'}),
    (r'^passwordChange/', 'django.contrib.auth.views.password_change', {'template_name': 'password_change_form.html'}),
    (r'^passwordChangeDone/', 'django.contrib.auth.views.password_change_done', {'template_name': 'password_change_success.html'}),
    (r'^passwordReset/', 'django.contrib.auth.views.password_reset',
        {
            'template_name': 'password_reset.html',
            'subject_template_name': 'password_reset_email_subject.txt',
        }),
    (r'^passwordResetDone/', 'django.contrib.auth.views.password_reset_done', {'template_name': 'password_reset_done.html'}),
    (r'^passwordResetConfirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'password_reset_confirm.html'}),
    (r'^passwordResetComplete/', 'django.contrib.auth.views.password_reset_complete', {'template_name': 'password_reset_complete.html'}),


)
