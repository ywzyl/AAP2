"""AAP2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from request import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^index/$', views.get_index),
    url('^login/$', views.login),
    url('^first_page/$', views.first_page),
    url('^$', views.get_index),
#环境配置
    url('^env/$',views.env),
    url('^env_add_data/$',views.env_add_data),
    url('^env_edit_data/$',views.env_edit_data),
    url('^env_delete_data/$',views.env_delete_data),
    #url('^env_search_name/$',views.env_search_name),
#数据库配置
    url('^database/$',views.database),
    url('^database_add_data/$',views.database_add_data),
    url('^database_edit_data/$',views.database_edit_data),
    url('^database_delete_data/$',views.database_delete_data),
#测试项目
    url('^project/$',views.project),
    url('^project_add_data/$',views.project_add_data),
    url('^project_edit_data/$',views.project_edit_data),
    url('^project_delete_data/$',views.project_delete_data),
#测试模块
    url('^modules/$',views.modules),
    url('^modules_add_data/$',views.modules_add_data),
    url('^modules_edit_data/$',views.modules_edit_data),
    url('^modules_delete_data/$',views.modules_delete_data),
#测试用例
    url('^case/$',views.case),
    url('^get_modules_name/$',views.get_modules),
    url('^case_add_data/$',views.case_add_data),
    url('^case_edit_data/$',views.case_edit_data),
    url('^case_delete_data/$',views.case_delete_data),
#测试步骤
    url('^step/$',views.step),
    url('^step_add_data/$',views.step_add_data),
    url('^step_edit_data/$',views.step_edit_data),
    url('^step_delete_data/$',views.step_delete_data),
#测试sql
    url('^sql/$',views.sql),
    url('^sql_add_data/$',views.sql_add_data),
    url('^sql_edit_data/$',views.sql_edit_data),
    url('^sql_delete_data/$',views.sql_delete_data),
#生成脚本
    url('^make_case_data/$',views.make_case_data),
#定时任务
    url('^task/$',views.task),
    url('^tasks_delete_data/$',views.tasks_delete_data),
    url('^task_run/$',views.task_run),
    url('^start_timing_task/$', views.start_timing_task),
    url('^get_progress_bar/$', views.get_progress_bar),

    #执行结果
    url('^htmlreport/$', views.htmlreport),

    #报告
    url('^report/$', views.report),

]
