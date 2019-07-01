from django.shortcuts import render
from request.models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.contrib import auth
from django.shortcuts import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse
import json,os
from public.make_testcase import Make_testcase
from public.system import *
from public.sqldb import create_db
from public.run import interface
from public.job import Job
from django.db.models import Min,Avg,Max,Sum
from decimal import Decimal
from django.utils.timezone import now,timedelta

#分页显示数
NumberColumns=15

#当页面编辑新增删除后拿的全部数据，返回第一页的数据
def get_firstPage(dataModel):
    data_list = dataModel.objects.all()
    paginator = Paginator(data_list,NumberColumns)
    contacts = paginator.page(1)
    return contacts

#登录首页
def get_index(request):
    return render(request,"index.html")

#登录
def login(request):
    if request.method == "POST":
        Username = request.POST.get("username")
        Password = request.POST.get("password")
        user = auth.authenticate(username=Username,password=Password)
        if user != None:
            auth.login(request,user)
            request.session["Username"] = Username
            #User.objects.filter(username=Username).update(password=base64.b64encode(bytes(Password,'utf-8')).decode())
            return HttpResponseRedirect("/first_page/")
        else:
            return render(request,"index.html",{"error":"账号或密码错误"})

#首页
@login_required
def first_page(request):
    try:
        Username = request.session["Username"]
        return render(request,"first_page.html",{"Username":Username})
    except:
        return render(request,"index.html")

#环境配置
@login_required
def env(request):
    #获取请求参数
    env_ip = request.GET.get("ip")
    env_host = request.GET.get("host")
    env_port = request.GET.get("port")
    #获取Environment对象列表
    try:
        env_list = Environment.objects.filter(Q(env_ip__contains=env_ip),Q(env_host__contains=env_host),
                                              Q(env_port__contains=env_port))
    except:
        env_list = Environment.objects.all()
    #分页显示
    paginator = Paginator(env_list,NumberColumns)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    #当向page()传入一个不是整数的值时抛出
    except PageNotAnInteger:
        contacts = paginator.page(1)
    #当向page()提供一个有效值，但是页面上没有任何对象时抛出
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    #返回响应
    response = {"envs":contacts}
    if env_ip != None:
        response["env_ip"] = env_ip
    if env_host != None:
        response["env_host"] = env_host
    if env_port != None:
        response["env_port"] = env_port
    return render(request,"./main/env.html",response)

@login_required
def env_add_data(request):
    env_ip = request.POST.get("ip")
    env_host = request.POST.get("host")
    env_port = request.POST.get("port")
    env_desc = request.POST.get("desc")
    isRepeat = len(Environment.objects.filter(env_desc=env_desc).values())
    # 不重复则新增数据
    if isRepeat == 0:
        Environment.objects.create(env_ip=env_ip, env_host=env_host, env_port=env_port, env_desc=env_desc)
    contacts = get_firstPage(Environment)
    return render(request, "./main/env.html", {"envs": contacts, "isRepeat": isRepeat})

@login_required
def env_edit_data(request):
    env_id = request.POST.get("id")
    env_ip = request.POST.get("ip")
    env_host = request.POST.get("host")
    env_port = request.POST.get("port")
    env_desc = request.POST.get("desc")
    Environment.objects.filter(id=env_id).update(env_ip=env_ip,env_host=env_host,env_port=env_port,env_desc=env_desc)
    contacts = get_firstPage(Environment)
    return render(request,"./main/env.html",{"envs":contacts})

@login_required
def env_delete_data(request):
    env_ids = request.POST.get("id")
    env_ids = env_ids.split(',')
    for env_id in env_ids:
        if env_id != "":
            Environment.objects.filter(id=env_id).delete()
    contacts = get_firstPage(Environment)
    return render(request,"./main/env.html",{"envs":contacts})

'''
@login_required
def env_search_name(request):
    env_ip = request.GET.get("ip")
    env_host = request.GET.get("host")
    env_port = request.GET.get("port")
    env_list = Environment.objects.filter(Q(env_ip=env_ip),Q(env_host=env_host),Q(env_port=env_port))
    contacts = get_firstPage(env_list)
    return render(request,"./main/env.html",{"envs":contacts,"env_ip":env_ip,"env_host":env_host,"env_port":env_port})
'''

#数据库配置
@login_required
def database(request):
    db_ip = request.GET.get("db_ip")
    db_name = request.GET.get("db_name")
    db_typename = request.GET.get("db_typename")
    try:
        database_list = Database.objects.filter(Q(db_ip__contains=db_ip),Q(db_name__contains=db_name),
                                                Q(db_typename__contains=db_typename))
    except:
        database_list = Database.objects.all()
    paginator = Paginator(database_list,NumberColumns)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    response = {"databases":contacts}
    if db_ip != None:
        response["db_ip"] = db_ip
    if db_name != None:
        response["db_name"] = db_name
    if db_typename != None:
        response["db_typename"] = db_typename
    return render(request,"./main/database.html",response)

@login_required
def database_add_data(request):
    db_typename = request.POST.get("db_type")
    db_name = request.POST.get("db_name")
    db_ip = request.POST.get("db_ip")
    db_port = request.POST.get("db_port")
    db_user = request.POST.get("db_user")
    db_password = request.POST.get("db_password")
    db_remark = request.POST.get("db_remark")
    isRepeat = len(Database.objects.filter(db_remark=db_remark).values())
    if isRepeat == 0:
        if db_typename == "Mysql":
            Database.objects.create(db_type=0,db_typename=db_typename,db_name=db_name,db_ip=db_ip,db_port=db_port,
                                    db_user=db_user,db_password=db_password,db_remark=db_remark)
        if db_typename == "SqlServer":
            Database.objects.create(db_type=1,db_typename=db_typename,db_name=db_name,db_ip=db_ip,
                                    db_user=db_user,db_password=db_password,db_remark=db_remark)
    contacts = get_firstPage(Database)
    return render(request,"./main/database.html",{"databases":contacts,"isRepeat":isRepeat})

@login_required
def database_edit_data(request):
    db_id = request.POST.get("id")
    db_typename = request.POST.get("db_type")
    db_name = request.POST.get("db_name")
    db_ip = request.POST.get("db_ip")
    db_port = request.POST.get("db_port")
    db_user = request.POST.get("db_user")
    db_password = request.POST.get("db_password")
    db_remark = request.POST.get("db_remark")
    if db_typename == "Mysql":
        Database.objects.filter(id=db_id).update(db_type=0,db_typename=db_typename,db_name=db_name, db_ip=db_ip,
                                                 db_port=db_port,db_user=db_user, db_password=db_password,
                                                 db_remark=db_remark)
    if db_typename == "SqlServer":
        Database.objects.filter(id=db_id).update(db_type=1,db_typename=db_typename,db_name=db_name, db_ip=db_ip,
                                                 db_user=db_user, db_password=db_password,db_remark=db_remark)
    contacts = get_firstPage(Database)
    return render(request,"./main/database.html",{"databases":contacts})

@login_required
def database_delete_data(request):
    db_ids = request.POST.get("id")
    db_ids = db_ids.split(',')
    for db_id in db_ids:
        if db_id != "":
            Database.objects.filter(id=db_id).delete()
    contacts = get_firstPage(Database)
    return render(request,"./main/database.html",{"databases":contacts})

#测试项目
@login_required
def project(request):
    project_name = request.GET.get("project_name")
    Testers = request.GET.get("Testers")
    Developer = request.GET.get("Developer")
    select = request.GET.get("select")
    try:
        if select != '2':
            project_list = Project.objects.filter(Q(project_name__contains=project_name),Q(Testers__contains=Testers),
                                                  Q(Developer__contains=Developer),Q(status=select))
        else:
            project_list = Project.objects.filter(Q(project_name__contains=project_name),Q(Testers__contains=Testers),
                                                  Q(Developer__contains=Developer))
    except:
        project_list = Project.objects.all()
    paginator = Paginator(project_list,NumberColumns)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)  #页面总数
    response = {"projects":contacts}
    if project_name != None:
        response["project_name"] = project_name
    if Testers != None:
        response["Testers"] = Testers
    if Developer != None:
        response["Developer"] = Developer
    if select != None:
        response["select"] = select
    else:
        select = '2'
        response["select"] = select
    return render(request,"./main/project.html",response)

@login_required
def project_add_data(request):
    project_name = request.POST.get("project_name")
    project_desc = request.POST.get("project_desc")
    testers = request.POST.get("testers")
    developer = request.POST.get("developer")
    status = request.POST.get("status")
    isRepeat = len(Project.objects.filter(project_name=project_name).values())
    # 不重复则新增数据
    if isRepeat == 0:
        if status != None:
            Project.objects.create(project_name=project_name,project_desc=project_desc,Testers=testers,
                                   Developer=developer,status=1)
        else:
            Project.objects.create(project_name=project_name,project_desc=project_desc,Testers=testers,
                                   Developer=developer,status=0)
    contacts = get_firstPage(Project)
    return render(request,"./main/project.html",{"projects":contacts,"select":'2',"isRepeat":isRepeat})

@login_required
def project_edit_data(request):
    project_id = request.POST.get("id")
    project_name = request.POST.get("project_name")
    project_desc = request.POST.get("project_desc")
    testers = request.POST.get("testers")
    developer = request.POST.get("developer")
    status = request.POST.get("status")
    if status != None:
        Project.objects.filter(id=project_id).update(project_name=project_name,project_desc=project_desc,
                                                     Testers=testers,Developer=developer,status=1)
    else:
        Project.objects.filter(id=project_id).update(project_name=project_name,project_desc=project_desc,
                                                     Testers=testers,Developer=developer,status=0)
    contacts = get_firstPage(Project)
    return render(request,"./main/project.html",{"projects":contacts,"select":'2'})

@login_required
def project_delete_data(request):
    project_ids = request.POST.get("id")
    project_ids = project_ids.split(',')
    for project_id in project_ids:
        if project_id != "":
            Project.objects.filter(id=project_id).delete()
    contacts = get_firstPage(Project)
    return render(request,"./main/project.html",{"projects":contacts,"select":'2'})

#测试模块
#把测试项目的project_name取出，当成新增编辑页面项目的可选的列
def get_project_name():
    project_names = []
    startproject_names = Project.objects.filter(status=1).values("project_name")
    for i in range(len(startproject_names)):
        project_names.append(startproject_names[i]["project_name"])
    return project_names

@login_required
def modules(request):
    modules_name = request.GET.get("modules_name")
    project_name = request.GET.get("project_name")
    Testers = request.GET.get("Testers")
    Developer = request.GET.get("Developer")
    select = request.GET.get("select")
    try:
        if project_name == '0':
            if select != '2':
                modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                      Q(Testers__contains=Testers),
                                                      Q(Developer__contains=Developer),Q(status=select))
            else:
                modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                      Q(Testers__contains=Testers),Q(Developer__contains=Developer))
        else:
            # 得到外键数据
            project =Project.objects.get(project_name=project_name)
            if select != '2':
                modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                      Q(Testers__contains=Testers),Q(Developer__contains=Developer),
                                                      Q(status=select),Q(Project=project))
            else:
                modules_list = Modules.objects.filter(Q(Modules_name__contains=modules_name),
                                                      Q(Testers__contains=Testers),Q(Developer__contains=Developer),
                                                      Q(Project=project))
    except:
        modules_list = Modules.objects.all()
    paginator = Paginator(modules_list,NumberColumns)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    response = {"modules":contacts}
    project_names = get_project_name()
    if modules_name != None:
        response["modules_name"] = modules_name
    if Testers != None:
        response["Testers"] = Testers
    if Developer != None:
        response["Developer"] = Developer
    if project_names != None:
        response["project_names"] = project_names
    if project_name != None:
        response["project_name"] = project_name
    else:
        project_name = '0'
        response["project_name"] = project_name
    if select != None:
        response["select"] = select
    else:
        select = '2'
        response["select"] = select
    return render(request,"./main/modules.html",response)

@login_required
def modules_add_data(request):
    Modules_name = request.POST.get("modules_name")
    Modules_desc = request.POST.get("modules_desc")
    testers = request.POST.get("testers")
    developer = request.POST.get("developer")
    status = request.POST.get("status")
    project_name = request.POST.get('project_name')
    # 得到外键数据，用get方法，如果用filter方法返回的是一个queryset对象
    project = Project.objects.get(project_name=project_name)
    isRepeat = len(Modules.objects.filter(Modules_name=Modules_name, Project=project).values())
    # 不重复则新增数据
    if isRepeat == 0:
        if status != None:
            Modules.objects.create(Modules_name=Modules_name, Modules_desc=Modules_desc, Testers=testers,
                                   Developer=developer, status=1, Project=project)
        else:
            Modules.objects.create(Modules_name=Modules_name, Modules_desc=Modules_desc, Testers=testers,
                                   Developer=developer, status=0, Project=project)
    contacts = get_firstPage(Modules)
    project_names = get_project_name()
    return render(request, "./main/modules.html",{"modules": contacts, "project_names": project_names, "isRepeat": isRepeat})

@login_required
def modules_edit_data(request):
    Modules_id = request.POST.get("id")
    Modules_name = request.POST.get("modules_name")
    Modules_desc = request.POST.get("modules_desc")
    testers = request.POST.get("testers")
    developer = request.POST.get("developer")
    status = request.POST.get("status")
    project_name = request.POST.get('project_name')
    # 得到外键数据
    project = Project.objects.get(project_name=project_name)
    if status != None:
        Modules.objects.filter(id=Modules_id).update(Modules_name=Modules_name,Modules_desc=Modules_desc,
                                                     Testers=testers,Developer=developer,status=1,Project=project)
    else:
        Modules.objects.filter(id=Modules_id).update(Modules_name=Modules_name,Modules_desc=Modules_desc,
                                                     Testers=testers,Developer=developer,status=0,Project=project)
    contacts = get_firstPage(Modules)
    project_names = get_project_name()
    return render(request,"./main/modules.html",{"modules":contacts,"project_names":project_names})

@login_required
def modules_delete_data(request):
    modules_ids = request.POST.get("id")
    modules_ids = modules_ids.split(',')
    for modules_id in modules_ids:
        if modules_id != None:
            Modules.objects.filter(id=modules_id).delete()
    contacts = get_firstPage(Modules)
    project_names = get_project_name()
    return render(request,"./main/modules.html",{"modules":contacts,"project_names":project_names})

#测试用例
#当数据是部分时把列表的项目名取出
def filter_project_listnames(case_list):
    modules = case_list.values('Modules')
    project_listnames = []
    for i in modules:
        project_id = Modules.objects.filter(id=i['Modules']).values('Project')
        project_name =Project.objects.filter(id=project_id[0]['Project']).values('project_name')
        project_listnames.append(project_name[0]['project_name'])
    return project_listnames

#当数据是全部时把列表的项目名取出
def get_project_listnames():
    modules = Case.objects.all().values('Modules').order_by("id")
    project_listnames = []
    for i in modules:
        projects_id = Modules.objects.filter(id=i['Modules']).values("Project")
        project_name = Project.objects.filter(id=projects_id[0]['Project']).values("project_name")
        project_listnames.append(project_name[0]['project_name'])
    return project_listnames

#把测试模块的modules_name取出，当成新增编辑页面项目的可选的列
def get_modules_name(project_name):
    # 得到外键数据
    project = Project.objects.get(project_name=project_name)
    modules_names =[]
    startmodules_names = Modules.objects.filter(Project=project,status=1).values('Modules_name')
    for i in range(len(startmodules_names)):
        modules_names.append(startmodules_names[i]['Modules_name'])
    return modules_names

@login_required
def case(request):
    case_name = request.GET.get("case_name")
    selectproject = request.GET.get("project_name")
    selectmodules = request.GET.get("modules_name")
    api = request.GET.get("api")
    version = request.GET.get("version")
    select = request.GET.get("select")
    checkedenv_ids = request.GET.get("checkedenv_ids")
    # 三层嵌套，最内为status是否等于‘2’，中间为modules是否等于‘0’，最外为project是否等于‘0’
    try:
        if selectproject == '0':
            if select != '2':
                case_list = Case.objects.filter(Q(case_name__contains=case_name),Q(api__contains=api),
                                                Q(version__contains=version),Q(status=select))
            else:
                case_list = Case.objects.filter(Q(case_name__contains=case_name),Q(api__contains=api),
                                                Q(version__contains=version))
        else:
            if selectmodules == '0':
                # 得到模块的外键数据
                project = Project.objects.filter(project_name=selectproject)
                # 得到用例的外键数据
                modules = Modules.objects.filter(Project=project)
                if select != '2':
                    case_list = Case.objects.filter(Q(case_name__contains=case_name),Q(api__contains=api),
                                                Q(version__contains=version),Q(status=select),Q(Modules__in=modules))
                else:
                    case_list = Case.objects.filter(Q(case_name__contains=case_name),Q(api__contains=api),
                                                    Q(version__contains=version),Q(Modules__in=modules))
            else:
                # 得到模块的外键数据
                project = Project.objects.filter(project_name=selectproject)
                # 得到用例的外键数据
                modules = Modules.objects.filter(Modules_name=selectmodules,Project=project)
                if select != '2':
                    case_list = Case.objects.filter(Q(case_name__contains=case_name),Q(api__contains=api),
                                                Q(version__contains=version),Q(status=select),Q(Modules__in=modules))
                else:
                    case_list = Case.objects.filter(Q(case_name__contains=case_name),Q(api__contains=api),
                                                    Q(version__contains=version),Q(Modules__in=modules))
    except:
        case_list = Case.objects.all()
    paginator = Paginator(case_list,NumberColumns)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    # 得到列表项目名根据页面去提取
    project_listnames = get_project_listnames()
    newproject_listnames = []
    try:
        first_number = NumberColumns*int(page)-NumberColumns
        last_number = NumberColumns*int(page)
        if last_number>len(project_listnames):
            last_number=len(project_listnames)
        for i in range(first_number,last_number):
            newproject_listnames.append(project_listnames[i])
    except:
        newproject_listnames = project_listnames

    project_names = get_project_name()
    #修复没有数据索引越界的问题
    try:
        project_name = project_names[0]
        modules_names = get_modules_name(project_name)
    except:
        project_name = None
        modules_names = None
    # 把项目名和用例列表数据打包
    contactszip = zip(contacts,newproject_listnames)
    # 给项目选择框对应的数据
    if selectproject != '0' and selectproject != None:
        selectmodules_names = get_modules_name(selectproject)
    else:
        selectmodules_names = None

    response = {"casees":contacts,"cases":contactszip,"selectmodules_names":selectmodules_names}
    if case_name != None:
        response["case_name"] = case_name
    if api != None:
        response["api"] = api
    if version!=None:
        response["version"]=version
    if project_names!=None:
        response["project_names"]=project_names
    if modules_names!=None:
        response["modules_names"]=modules_names
    if selectproject != None:
        response["selectproject"] = selectproject
    else:
        selectproject = '0'
        response["selectproject"] = selectproject
    if selectmodules != None:
        response["selectmodules"] = selectmodules
    else:
        selectmodules = '0'
        response["selectmodules"] = selectmodules
    if select != None:
        response["select"] = select
    else:
        select = '2'
        response["select"] = select
    if checkedenv_ids != None:
        response["checkedenv_ids"] = checkedenv_ids
    else:
        response["checkedenv_ids"] = None
    return render(request,"./main/case.html",response)

#通过项目名去获取模块名并返回
@login_required
def get_modules(request):
    project_name = request.GET.get("project_name")
    modules_names = get_modules_name(project_name)
    return JsonResponse({"modules_names":modules_names})

@login_required
def case_add_data(request):
    case_name = request.POST.get("case_name")
    project_name = request.POST.get("project_name")
    modules_name = request.POST.get("modules_name")
    api = request.POST.get("api")
    version = request.POST.get("version")
    case_desc = request.POST.get('case_desc')
    status = request.POST.get('status')
    # 得到项目的外键数据
    project = Project.objects.get(project_name=project_name)
    # 得到用例的外键数据
    modules = Modules.objects.get(Modules_name=modules_name,Project=project)
    isRepeat = len(Case.objects.filter(case_name=case_name).values())
    # 不重复则新增数据
    if isRepeat == 0:
        if status != None:
            Case.objects.create(case_name=case_name,case_desc=case_desc,api=api,version=version,status=1,Modules=modules)
        else:
            Case.objects.create(case_name=case_name,case_desc=case_desc,api=api,version=version,status=0,Modules=modules)
    contacts = get_firstPage(Case)
    # 得到列表项目名
    project_listnames = get_project_listnames()
    # 把项目名和用例列表数据打包
    contactszip = zip(contacts,project_listnames)
    project_names = get_project_name()
    project_name = project_names[0]
    modules_names = get_modules_name(project_name)
    return render(request,"./main/case.html",{"cases":contactszip,"modules_names":modules_names,
                                              "project_names":project_names,"casees":contacts,"isRepeat":isRepeat})

@login_required
def case_edit_data(request):
    case_id = request.POST.get("id")
    case_name = request.POST.get("case_name")
    project_name = request.POST.get("project_name")
    modules_name = request.POST.get("modules_name")
    api = request.POST.get("api")
    version = request.POST.get("version")
    case_desc = request.POST.get('case_desc')
    status = request.POST.get('status')
    # 得到项目的外键数据
    project = Project.objects.get(project_name=project_name)
    # 得到用例的外键数据
    modules = Modules.objects.get(Modules_name=modules_name,Project=project)
    if status != None:
        Case.objects.filter(id=case_id).update(case_name=case_name,api=api,version=version,case_desc=case_desc,
                                               status=1,Modules=modules)
    else:
        Case.objects.filter(id=case_id).update(case_name=case_name,api=api,version=version,case_desc=case_desc,
                                               status=0,Modules=modules)
    contacts = get_firstPage(Case)
    # 得到列表项目名
    project_listnames = get_project_listnames()
    # 把项目名和用例列表数据打包
    contactszip = zip(contacts,project_listnames)
    project_names = get_project_name()
    project_name = project_names[0]
    modules_names = get_modules_name(project_name)
    return render(request,"./main/case.html",{"cases":contactszip,"modules_names":modules_names,
                                              "project_names":project_names,"casees":contacts})

@login_required
def case_delete_data(request):
    case_ids = request.POST.get("id")
    case_ids = case_ids.split(',')
    for case_id in case_ids:
        if case_id != "":
            Case.objects.filter(id=case_id).delete()
    contacts = get_firstPage(Case)
    project_listnames = get_project_listnames()
    contactszip = zip(contacts,project_listnames)
    project_names = get_project_name()
    project_name = project_names[0]
    modules_names = get_modules_name(project_name)
    return render(request,"./main/case.html",{"cases":contactszip,"modules_names":modules_names,
                                              "project_names":project_names,"casees":contacts})

#测试步骤

#把测试用例的project_name取出，当成新增编辑页面项目的可选的列
def get_case_name():
    case_names = []
    case_namelist = Case.objects.filter(status=1).values("case_name")
    for i in range(len(case_namelist)):
        case_names.append(case_namelist[i]["case_name"])
    return case_names

@login_required
def step(request):
    step_name = request.GET.get("step_name")
    method = request.GET.get("method")
    steplevel = request.GET.get("steplevel")
    select = request.GET.get("select")
    case_name = request.GET.get("case_name")
    try:
        if case_name == "0":
            if method == "0":
                if select == '2':
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel))
                else:
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(status=select))
            else:
                if select == '2':
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(method=method))
                else:
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(status=select), Q(method=method))
        else:
            # 得到外键数据
            case = Case.objects.get(case_name=case_name)
            if method == "0":
                if select == '2':
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(case=case))
                else:
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(status=select), Q(case=case))
            else:
                if select == '2':
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(method=method), Q(case=case))
                else:
                    step_list = Step.objects.filter(Q(step_name__contains=step_name), Q(steplevel__contains=steplevel), \
                                                    Q(status=select), Q(method=method), Q(case=case))
    except:
        step_list=Step.objects.all()
    paginator=Paginator(step_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"steps":contacts}
    # 新增和编辑时的用例名
    case_names = get_case_name()
    step_names=get_step_name()
    if step_name!=None:
        response["step_name"]=step_name
    if steplevel!=None:
        response["steplevel"]=steplevel
    if case_names!=None:
        response["case_names"]=case_names
    if step_names!=None:
        response["step_names"]=step_names
    if case_name!=None:
        response["selectcase_name"]=case_name
    else:
        case_name = '0'
        response["selectcase_name"] = case_name
    if method!=None:
        response["selectmethod"]=method
    else:
        method = '0'
        response["selectmethod"] = method
    if select!=None:
        response["select"]=select
    else:
        select = '2'
        response["select"] = select
    return render(request, "./main/step.html",response)

    contacts = get_firstPage(Step)
    case_names=get_case_name()
    #print (case_names)
    return render(request, "./main/step.html", {"steps": contacts, "case_names": case_names})

#获取权重
def get_weights(step_name,api_dependency):
    oldstep_weights=0
    api_dependencyjson = json.loads(api_dependency)
    for variable in api_dependencyjson.keys():
        for reference_step_name in api_dependencyjson[variable].keys():
            oldreference_step_weights = Step.objects.filter(step_name=reference_step_name).values('step_weights')[0]['step_weights']
            if oldreference_step_weights+1>oldstep_weights:
                Step.objects.filter(step_name=step_name).update(step_weights=oldreference_step_weights+1)
                oldstep_weights=oldreference_step_weights+1

#获取权重
def get_case_weights(step_name,api_dependency):
    oldcase_weights=0
    print(step_name)
    print("----")
    print(len(Step.objects.filter(step_name=step_name).values('case_id')))
    case_id = Step.objects.filter(step_name=step_name).values('case_id')[0]['case_id']
    step_names=Step.objects.filter(case=case_id).values('step_name')
    #用例下所有步骤
    for case_step_name in step_names:
        reference_step_names=Reference_step.objects.filter(step_name=case_step_name['step_name']).values('reference_step_name')
        oldstep_weights = 0
        for reference_step_name in reference_step_names:
            reference_case_id=Step.objects.filter(step_name=reference_step_name['reference_step_name']).values('case_id')[0]['case_id']
            reference_case_step_names=Step.objects.filter(case=reference_case_id).values('step_name')
            #被依赖下的用例下的所有步骤
            for reference_case_step_name in reference_case_step_names:
                old_case_step_weights = Step.objects.filter(step_name=reference_case_step_name['step_name']).values('step_weights')[0]['step_weights']
                if old_case_step_weights + 1 > oldstep_weights:
                    oldstep_weights = old_case_step_weights + 1
        if oldstep_weights>oldcase_weights:
            oldcase_weights=oldstep_weights
    Case.objects.filter(id=case_id).update(case_weights=oldcase_weights)

#当中间步骤树节点变化时 向上遍历直到结尾
def change_step_case(step_name):
    # 先修改涉及到的步骤权重，根据步骤名从关联步骤表中获取对应的步骤名列表
    Dependent_step_cases = Reference_step.objects.filter(reference_step_name=step_name).values('step_name')
    count = 0
    # 上一步中的步骤名列表不等于0，则进行while循环，是为了更新步骤表中的步骤权重值
    while len(Dependent_step_cases) != count:
        count = 0
        Dependent_steps = []
        for Dependent_step_case in Dependent_step_cases:
            # 根据步骤名列表中的步骤名从步骤表中获取接口依赖的值
            api_dependency = Step.objects.filter(step_name=Dependent_step_case['step_name']).values('api_dependency')[0]['api_dependency']
            # 根据上一步中的步骤名和接口依赖的值通过get_weights（）函数获取步骤权重，并更新至步骤表中
            get_weights(Dependent_step_case['step_name'],api_dependency)
            # 将步骤名添加至新的Dependent_steps列表中
            Dependent_steps.append(Dependent_step_case['step_name'])
            # 上一个for循环是要将第一步得到的步骤名列表遍历完，把步骤权重值更新至步骤表中；
            # 再将整个列表进行第二次for循环，是为了结束while循环
        for Dependent_step_case in Dependent_steps:
            # 根据上一步中的步骤名从关联步骤表中获取对应的步骤名列表
            Dependent_step_cases = Reference_step.objects.filter(reference_step_name=Dependent_step_case).values('step_name')
            # 一直往下遍历得到步骤名，直到结尾，则count加1，导致while循环结束
            if len(Dependent_step_cases) == 0:
                count+=1
        else:
            Dependent_steps = []
    # 再修改用例权重，逻辑同上一个while循环一样，区别在于修改的权重值目标不一样
    Dependent_step_cases = Reference_step.objects.filter(reference_step_name=step_name).values('step_name')
    count = 0
    while len(Dependent_step_cases) != count:
        count = 0
        Dependent_steps = []
        for Dependent_step_case in Dependent_step_cases:
            api_dependency = Step.objects.filter(step_name=Dependent_step_case['step_name']).values('api_dependency')[0]['api_dependency']
            get_case_weights(Dependent_step_case['step_name'],api_dependency)
            Dependent_steps.append(Dependent_step_case['step_name'])
        for Dependent_step_case in Dependent_steps:
            Dependent_step_cases = Reference_step.objects.filter(reference_step_name=Dependent_step_case).values('step_name')
            if len(Dependent_step_cases) == 0:
                count+=1
        else:
            Dependent_steps = []

@login_required
def step_add_data(request):
    step_name=request.POST.get('step_name')
    case_name=request.POST.get('case_name')
    method = request.POST.get('method')
    headers = request.POST.get('headers')
    params = request.POST.get('params')
    asserts = request.POST.get('asserts')
    api_dependency=request.POST.get('ApiDependencys')
    steplevel = request.POST.get('steplevel')
    step_desc = request.POST.get('step_desc')
    status = request.POST.get('status')
    paramsbody = request.POST.get('paramsbody')
    # 得到外键数据
    case = Case.objects.get(case_name=case_name)
    if asserts == None:
        asserts=""
    if api_dependency == None:
        api_dependency=""
    isRepeat = len(Step.objects.filter(step_name=step_name).values())

    # 不重复则新增数据
    if isRepeat == 0:
        if method=="get" or method=="postform":
            if status != None:
                Step.objects.create(step_name=step_name,step_desc=step_desc,steplevel=steplevel,method=method, \
                                    headers=headers,params=params,assert_response=asserts,api_dependency=api_dependency,status=1,case=case)
            else:
                Step.objects.create(step_name=step_name, step_desc=step_desc, steplevel=steplevel, method=method, \
                                    headers=headers, params=params, assert_response=asserts,api_dependency=api_dependency, status=0, case=case)
        elif method=="postbody":
            if status != None:
                Step.objects.create(step_name=step_name,step_desc=step_desc,steplevel=steplevel,method=method, \
                                    headers=headers,params=paramsbody,assert_response=asserts,api_dependency=api_dependency,status=1,case=case)
            else:
                Step.objects.create(step_name=step_name, step_desc=step_desc, steplevel=steplevel, method=method, \
                                    headers=headers, params=paramsbody, assert_response=asserts,api_dependency=api_dependency, status=0, case=case)

    if api_dependency!="":
        #得到外键数据
        step = Step.objects.get(step_name=step_name)
        #插入接口依赖数据
        api_dependencyjson=json.loads(api_dependency)
        for variable in api_dependencyjson.keys():
            for reference_step_name in api_dependencyjson[variable].keys():
                Reference_step.objects.create(variable=variable, step_name=step_name, path=api_dependencyjson[variable][reference_step_name], reference_step_name=reference_step_name, step=step)
        # 获取权重
        get_weights(step_name, api_dependency)
    else:
        Step.objects.filter(step_name=step_name).update(step_weights=0)
    #获得权重
    get_case_weights(step_name, api_dependency)
    change_step_case(step_name)
    #用作接口依赖选择框
    step_names = get_step_name()
    #新增和编辑时的用例名
    contacts = get_firstPage(Step)
    case_names = get_case_name()
    return render(request, "./main/step.html", {"steps": contacts,"case_names": case_names,"isRepeat":isRepeat,"step_names":step_names})

@login_required
def step_edit_data(request):
    step_id = request.POST.get("id")
    step_name = request.POST.get('step_name')
    case_name = request.POST.get('case_name')
    method = request.POST.get('method')
    headers = request.POST.get('headers')
    params = request.POST.get('params')
    asserts = request.POST.get('asserts')
    api_dependency = request.POST.get('ApiDependencys')
    steplevel = request.POST.get('steplevel')
    step_desc = request.POST.get('step_desc')
    status = request.POST.get('status')
    paramsbody = request.POST.get('paramsbody')
    # 得到外键数据
    case = Case.objects.get(case_name=case_name)
    if asserts == None:
        asserts = ""
    if  api_dependency == None:
        api_dependency = ""
    oldapi_dependencys = Step.objects.filter(step_name=step_name).values('api_dependency')

    if method == "get" or method == "postform":
        if status != None:
            Step.objects.filter(id=step_id).update(step_name=step_name, step_desc=step_desc, steplevel=steplevel,
                                                   method=method,headers=headers, params=params,
                                                   assert_response=asserts,api_dependency=api_dependency,
                                                   status=1, case=case)
        else:
            Step.objects.filter(id=step_id).update(step_name=step_name, step_desc=step_desc, steplevel=steplevel,
                                                   method=method,headers=headers, params=params,
                                                   assert_response=asserts,api_dependency=api_dependency,
                                                   status=0, case=case)
    elif method == "postbody":
        if status != None:
            Step.objects.filter(id=step_id).update(step_name=step_name,step_desc=step_desc,steplevel=steplevel,
                                                   method=method,headers=headers,params=paramsbody,
                                                   assert_response=asserts,api_dependency=api_dependency,
                                                   status=1,case=case)
        else:
            Step.objects.filter(id=step_id).update(step_name=step_name,step_desc=step_desc,steplevel=steplevel,
                                                   method=method,headers=headers,params=paramsbody,
                                                   assert_response=asserts,api_dependency=api_dependency,
                                                   status=0,case=case)
    # 得到外键数据
    step =Step.objects.get(step_name=step_name)
    if api_dependency != "":
        # 先删除接口依赖的数据
        Reference_step.objects.filter(step=step).delete()
        # 插入接口依赖数据
        api_dependencyjson = json.loads(api_dependency)
        for variable in api_dependencyjson.keys():
            for reference_step_name in api_dependencyjson[variable].keys():
                Reference_step.objects.create(variable=variable,step_name=step_name,
                                              path=api_dependencyjson[variable][reference_step_name],
                                              reference_step_name=reference_step_name,step=step)
        # 获取权重
        get_weights(step_name,api_dependency)
    else:
        # 先删除接口依赖的数据
        Reference_step.objects.filter(step=step).delete()
        # 写入权重
        Step.objects.filter(step_name=step_name).update(step_weights=0)
    # 获得权重
    get_case_weights(step_name,api_dependency)
    change_step_case(step_name)
    # 用作接口依赖选择框
    step_names = get_step_name()
    # 新增和编辑时的用例名
    contacts = get_firstPage(Step)
    case_names = get_case_name()
    return render(request,"./main/step.html",{"steps":contacts,"case_names":case_names,"step_names":step_names})

@login_required
def step_delete_data(request):
    step_ids = request.POST.get("id")
    step_ids = step_ids.split(',')
    for step_id in step_ids:
        if step_id != "":
            Step.objects.filter(id=step_id).delete()
    step_names = get_step_name()
    contacts = get_firstPage(Step)
    case_names = get_case_name()
    return render(request,"./main/step.html",{"steps":contacts,"step_names":step_names,"case_names":case_names})

#测试sql
#把测试步骤的step_name取出，当成新增编辑页面项目的可选的列
def get_step_name():
    step_names = []
    startstep_names = Step.objects.filter(status=1).values("step_name")
    for i in range(len(startstep_names)):
        step_names.append(startstep_names[i]["step_name"])
    return step_names

@login_required
def sql(request):
    step_name = request.GET.get("step_name")
    selectisselect = request.GET.get("selectisselect")
    select = request.GET.get("select")
    try:
        if step_name == '0':
            if select != '2':
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(is_select=selectisselect),Q(status=select))
                else:
                    sql_list = Sql.objects.filter(Q(status=select))
            else:
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(is_select=selectisselect))
                else:
                    sql_list = Sql.objects.filter()
        else:
            step = Step.objects.get(step_name=step_name)
            if select != '2':
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(step=step),Q(is_select=selectisselect),Q(status=select))
                else:
                    sql_list = Sql.objects.filter(Q(step=step),Q(status=select))
            else:
                if selectisselect != '2':
                    sql_list = Sql.objects.filter(Q(step=step),Q(is_select=selectisselect))
                else:
                    sql_list = Sql.objects.filter(Q(step=step))
    except:
        sql_list = Sql.objects.all()
    paginator = Paginator(sql_list,NumberColumns)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    response = {"sqls":contacts}
    step_names = get_step_name()
    if step_names != None:
        response['step_names'] = step_names
    if step_name != None:
        response['selectstep'] = step_name
    else:
        step_name = '0'
        response['selectstep'] = step_name
    if selectisselect != None:
        response['selectisselect'] = selectisselect
    else:
        selectisselect = '2'
        response['selectisselect'] = selectisselect
    if select != None:
        response['select'] = select
    else:
        select = '2'
        response['select'] = select
    return render(request,"./main/sql.html",response)

@login_required
def sql_add_data(request):
    step_name = request.POST.get("step_name")
    isselect  = request.POST.get("isselect")
    variable = request.POST.get("variable")
    sql = request.POST.get("sql")
    sql_condition = request.POST.get("sql_condition")
    remake = request.POST.get('remake')
    status = request.POST.get('status')
    step = Step.objects.get(step_name=step_name)
    if isselect == None:
        isselect = 0
        variable = ""
    else:
        isselect = 1
    if status != None:
        Sql.objects.create(is_select=isselect,variable=variable,sql=sql,sql_condition=sql_condition,remake=remake,
                           status=1,step=step)
    else:
        Sql.objects.create(is_select=isselect, variable=variable, sql=sql, sql_condition=sql_condition, remake=remake,
                           status=0, step=step)
    contacts = get_firstPage(Sql)
    step_names = get_step_name()
    return render(request,"./main/sql.html",{"step_names":step_names,"sqls":contacts})

@login_required
def sql_edit_data(request):
    sql_id = request.POST.get("id")
    step_name = request.POST.get("step_name")
    isselect = request.POST.get("isselect")
    variable = request.POST.get("variable")
    sql = request.POST.get("sql")
    sql_condition = request.POST.get("sql_condition")
    remake = request.POST.get('remake')
    status = request.POST.get('status')
    # 得到外键数据
    step = Step.objects.get(step_name=step_name)
    if isselect == None:
        isselect = 0
        variable = ""
    else:
        isselect = 1
    if status!=None:
        Sql.objects.filter(id=sql_id).update(is_select=isselect,variable=variable,sql=sql,sql_condition=sql_condition,remake=remake,status=1,step=step)
    else:
        Sql.objects.filter(id=sql_id).update(is_select=isselect,variable=variable,sql=sql,sql_condition=sql_condition,remake=remake,status=0,step=step)
    contacts = get_firstPage(Sql)
    step_names = get_step_name()
    return render(request, "./main/sql.html", {"sqls": contacts, "step_names": step_names})

@login_required
def sql_delete_data(request):
    sql_ids = request.POST.get("id")
    sql_ids = sql_ids.split(',')
    for sql_id in sql_ids:
        if sql_id != "":
            Sql.objects.filter(id=sql_id).delete()
    contacts = get_firstPage(Sql)
    step_names = get_step_name()
    return render(request,"./main/sql.html",{"sqls":contacts,"step_names":step_names})

#创建任务表
def create_task(case_ids,task_name,remark):
    for case_id in case_ids:
        case_data = Case.objects.filter(id=case_id).values("case_name","api")[0]
        case = Case.objects.get(id=case_id)
        Task.objects.create(task_name=task_name,remark=remark,case=case,status=0)

#用例生成脚本
#得到根据用例id拿到数据
def get_py_data(case_ids,testcasedir):
    for case_id in case_ids:
        case_data = Case.objects.filter(id=case_id).values("case_name","api","case_desc")[0]
        case = Case.objects.get(id=case_id)
        step_list_data = Step.objects.filter(case=case,status=1).values("id","step_name","method","params","headers",
                                                                        "files","assert_response","api_dependency",
                                                                        "step_desc")
        for step_data in step_list_data:
            step = Step.objects.get(id=step_data["id"])
            sql_list_data = Sql.objects.filter(step=step,status=1).values("sql_condition","is_select","variable","sql")
            step_data['sql_list_data'] = sql_list_data
        case_data['step_list_data'] = step_list_data
        make_testcase = Make_testcase(testcasedir,case_data)

#判断是不是windows,在task目录下创建本次任务目录，再创建case
def crate_task(task_name):
    if os.name == 'nt':
        task_dir = os.getcwd()+r'\task'
        task_name = task_dir+r"\\"+task_name
        testcase = task_name+r"\testcase"
        report = task_name+r"\report"
    else:
        task_dir = os.getcwd()+r"/task"
        task_name = task_dir+r"/"+task_name
        testcase = task_name+r"/testcase"
        report = task_name+r"/report"
    create_dir(task_name)
    create_dir(testcase)
    create_dir(report)
    # 创建一个初始化文件__init__.py
    filename = testcase+"/__init__.py"
    create_file(filename)
    return testcase

#生成脚本
@login_required
def make_case_data(request):
    case_ids = request.POST.get("id")
    task_name = request.POST.get("task_name")
    remark = request.POST.get("remark")
    isRepeat = len(Task.objects.filter(task_name=task_name).values())
    if isRepeat == 0:
        case_ids = case_ids.split(',')
        case_ids = case_ids[1:]
        create_task(case_ids,task_name,remark)
        testcasedir = crate_task(task_name)
        get_py_data(case_ids,testcasedir)
    else:
        isRepeat = 2
    contacts = get_firstPage(Case)
    # 得到列表项目名
    project_listnames = get_project_listnames()
    # 把项目名和用例列表数据打包
    contactszip = zip(contacts,project_listnames)
    project_names = get_project_name()
    project_name = project_names[0]
    modules_names = get_modules_name(project_name)
    return render(request,"./main/case.html",{"cases":contactszip,"modules_names":modules_names,
                                              "project_names":project_names,"casees":contacts,"isRepeat":isRepeat})

#得到环境和数据库的描述和邮件
@login_required
def get_env_database_desc(request):
    env_descs = []
    db_remarks=[]
    subjects=[]
    #环境
    startenv_descs = Environment.objects.values("env_desc")
    for i in range(len(startenv_descs)):
        env_descs.append(startenv_descs[i]['env_desc'])
    #数据库
    startdb_remarks = Database.objects.values("db_remark")
    for i in range(len(startdb_remarks)):
        db_remarks.append(startdb_remarks[i]['db_remark'])
    # 邮件
    start_subjects = Email.objects.values("subject")
    for i in range(len(start_subjects)):
        subjects.append(start_subjects[i]['subject'])
    return env_descs,db_remarks,subjects


#定时任务
@login_required
def task(request):
    env_descs,db_remarks,subjects=get_env_database_desc(request)
    task_name = request.GET.get("task_name")
    try:
        data_list = Task.objects.filter(Q(task_name__contains=task_name)).values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject").distinct().order_by('task_name')
    except:
        data_list = Task.objects.values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject").distinct().order_by('task_name')
    paginator=Paginator(data_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"tasks":contacts}
    project_names = get_project_name()
    if task_name!=None:
        response["task_name"]=task_name
    if env_descs!=None:
        response["env_descs"]=env_descs
    if db_remarks!=None:
        response["db_remarks"]=db_remarks
    if subjects!=None:
        response["subjects"]=subjects

    return render(request, "./main/task.html",response)


#删除任务目录以及文件
def rm_task(task_name):
    task_dir = os.getcwd()+r"/task/"+task_name
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir)


@login_required
def tasks_delete_data(request):
    task_names = request.POST.get("task_names")
    env_descs, db_remarks, subjects = get_env_database_desc(request)
    #print (task_names)
    task_names=task_names.split(',')
    for task_name in task_names:
        if task_name!="":
            # 删除任务目录以及文件
            rm_task(task_name)
            Task.objects.filter(task_name=task_name).delete()
    # 得到一页数据
    data_list = Task.objects.values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject").distinct().order_by('task_name')
    paginator = Paginator(data_list, NumberColumns)
    contacts = paginator.page(1)
    return render(request, "./main/task.html", {"tasks": contacts,"env_descs":env_descs,"db_remarks":db_remarks,"subjects":subjects})

#拼接ip和启动数据库对象
@login_required
def get_ip_database(request,env_desc,database_desc):
    #环境
    env_list=Environment.objects.filter(env_desc=env_desc).values("env_ip","env_host","env_port")
    if env_list[0]['env_ip'] != "":
        if env_list[0]['env_port'] != "":
            env_ip = "http://{host}:{port}".format(host=env_list[0]['env_ip'], port=env_list[0]['env_port'])
        else:
            env_ip = "http://{host}".format(host=env_list[0]['env_ip'])
    else:
        if env_list[0]['env_port'] != "":
            env_ip = "http://{host}:{port}".format(host=env_list[0]['env_host'], port=env_list[0]['env_port'])
        else:
            env_ip = "http://{host}".format(host=env_list[0]['env_host'])
    #数据库
    if database_desc!="":
        db_list=Database.objects.filter(db_remark=database_desc).values('db_type','db_name','db_ip','db_port','db_user','db_password')
    #不需要数据库
    else:
        db_list=[]
        db_list.append({"db_type":"","db_ip":"","db_port":"","db_user":"","db_password":"","db_name":""})
    create_db(db_list[0]['db_type'],db_list[0]['db_ip'],db_list[0]['db_port'], db_list[0]['db_user'],db_list[0]['db_password'],db_list[0]['db_name'],env_ip)

#写入定时任务数据
@login_required
def write_task(request,task_name,env_desc,database_desc,failcount,schedule,status,email_data):
    # 环境
    env_id = Environment.objects.filter(env_desc=env_desc).values("id")[0]['id']
    #数据库
    if database_desc != "":
        db_id = Database.objects.filter(db_remark=database_desc).values("id"[0]['id'])
    # 不使用数据库
    else:
        db_id = ""
    if status != None:
        if email_data == None:
            Task.objects.filter(task_name=task_name).update(id=env_id,db=db_id,failcount=failcount,
                                                            task_run_time_regular=schedule,status=1,env_desc=env_desc,
                                                            db_remark=database_desc)
        else:
            Task.objects.filter(task_name=task_name).update(id=env_id,db=db_id,failcount=failcount,
                                                            task_run_time_regular=schedule,status=1,env_desc=env_desc,
                                                            db_remark=database_desc,email=email_data['id'],subject=email_data['subject'])
    else:
        if email_data == None:
            Task.objects.filter(task_name=task_name).update(id=env_id,db=db_id,failcount=failcount,
                                                            task_run_time_regular=schedule,status=0,env_desc=env_desc,
                                                            db_remark=database_desc)
        else:
            Task.objects.filter(task_name=task_name).update(id=env_id,db=db_id,failcount=failcount,
                                                            task_run_time_regular=schedule,status=0,env_desc=env_desc,
                                                            db_remark=database_desc,email=email_data['id'],subject=email_data['subject'])

#执行任务
@login_required
def task_run(request):
    # 声明一个全局变量 finish
    global finish
    task_name = request.POST.get("task_name")
    env_desc = request.POST.get("env_desc")
    database_desc = request.POST.get("database_desc")
    subject = request.POST.get("subject")
    failcount = request.POST.get("failcount")
    schedule = request.POST.get("schedule")
    status = request.POST.get("status")
    env_descs,db_remarks,subjects = get_env_database_desc(request)
    # 如果要发送邮件拿到邮件配置数据
    if subject != None:
        email_data = Email.objects.filter(subject=subject).values('id','sender','receivers','host_dir','email_port','username','passwd','Headerfrom','Headerto','subject')[0]
    else:
        email_data = None
    # 选择一次性执行还是配置定时任务
    if schedule == None:
        # 启动数据库对象，拼接ip
        get_ip_database(request,env_desc,database_desc)
        interface(task_name,failcount,email_data)
        print("一次性执行")
    else:
        write_task(request,task_name,env_desc,database_desc,failcount,schedule,status,email_data)
        # 创建一个Job任务对象
        job = Job(task_name,schedule)
        if status != None:
            # 新建任务
            job.create_job(request,env_desc,database_desc,failcount,subject)
        else:
            # 删除任务
            job.delete_job()
    search_task_name = None
    try:
        data_list = Task.objects.filter(Q(task_name__contains=search_task_name)).values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject").distinct().order_by('task_name')
    except:
        data_list = Task.objects.values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject").distinct().order_by('task_name')
    paginator = Paginator(data_list,NumberColumns)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    response = {"tasks":contacts}
    project_names = get_project_name()
    if search_task_name != None:
        response["search_task_name"] = search_task_name
    if env_descs != None:
        response["env_descs"] = env_descs
    if db_remarks != None:
        response["db_remarks"] = db_remarks
    if subjects != None:
        response["subjects"] = subjects
    finish = 1
    return render(request,"./main/task.html",response)
#得到定时任务数据
def get_task_data(request):
    task_name_list = Task.objects.filter(status=1).values("task_name","task_run_time_regular","db_remark","env_desc","failcount","status",'email','subject').distinct().order_by('task_name')
    for i in range(len(task_name_list)):
        job = Job(task_name_list[i]['task_name'], task_name_list[i]['task_run_time_regular'])
        # 新建任务
        job.create_job(request,task_name_list[i]['env_desc'], task_name_list[i]['db_remark'], task_name_list[i]['failcount'],task_name_list[i]['subject'])
#启动定时任务
@login_required
def start_timing_task(request):
    #启动全部定时任务
    get_task_data(request)

    env_descs, db_remarks, subjects = get_env_database_desc(request)
    task_name = None
    try:
        data_list = Task.objects.filter(Q(task_name__contains=task_name)).values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject").distinct().order_by('task_name')
    except:
        data_list = Task.objects.values("task_name","task_run_time_regular","db_remark","env_desc","failcount","remark","status","subject").distinct().order_by('task_name')
    paginator=Paginator(data_list,NumberColumns)
    page=request.GET.get("page")
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    response={"tasks":contacts}
    project_names = get_project_name()
    if task_name!=None:
        response["task_name"]=task_name
    if env_descs!=None:
        response["env_descs"]=env_descs
    if db_remarks!=None:
        response["db_remarks"]=db_remarks
    if subjects!=None:
        response["subjects"]=subjects

    return render(request, "./main/task.html",response)
#请求进度条
@login_required
def get_progress_bar(request):
    response={}
    global finish
    getfinish=finish
    print (getfinish)
    finish = 0
    response["getfinish"]=getfinish
    return JsonResponse(response)

#定时任务
@login_required
def htmlreport(request):
    task_name = request.GET.get("task_name")
    find_way = request.GET.get("find_way")
    #查找日志
    if find_way=="findtextreport":
        id=CarryTask.objects.filter(task_name=task_name).aggregate(id=Max('id'))['id']
        if id==None:
            successmessage = "未生成有正确日志"
            failmessage = "未生成断言错误日志"
            print ("任务未被执行")
        else:
            lognames=CarryTask.objects.filter(id=id).values("successlogname","errorlogname")[0]
            successtext = lognames['successlogname']
            failtext = lognames['errorlogname']
            try:
                with open(successtext, 'r') as fp:
                    successmessage=fp.read()
                    fp.close()
            except:
                successmessage="未生成有正确日志"
            try:
                with open(failtext, 'r') as fp:
                    failmessage=fp.read()
                    fp.close()
            except:
                failmessage="未生成断言错误日志"
        return render(request, "../task/textreport.html",{"successmessage":successmessage,"failmessage":failmessage})
    #查找html
    elif find_way=="findhtmlreport":
        id = CarryTask.objects.filter(task_name=task_name).aggregate(id=Max('id'))['id']
        if id == None:
            htmlreport = "../task/nohtmlreport.html"
            print("任务未被执行")
        else:
            htmlnames = CarryTask.objects.filter(id=id).values("htmlreport")[0]
            htmlreport = htmlnames['htmlreport']
            try:
                with open(htmlreport, 'r') as fp:
                    fp.close()
            except:
                htmlreport="../task/nohtmlreport.html"
        return render(request, htmlreport)

#报告
@login_required
def report(request):
    response={}
    #case数目
    casenumber=len(Case.objects.filter(status=1).all())
    #定时任务数目
    tasknumber=len(Task.objects.filter(status=1).values('task_name').distinct())
    response['casenumber']=casenumber
    response['tasknumber'] = tasknumber
    try:
        #通过数，失败数，错误断言数，总执行次数，错误率
        passnumber=len(LogAndHtmlfeedback.objects.filter(test_status=1))
        failnumber=len(LogAndHtmlfeedback.objects.filter(test_status=0))
        asserterrornumber = len(LogAndHtmlfeedback.objects.filter(test_status=2))
        carrynumber=passnumber+failnumber+asserterrornumber
        errorratio=(failnumber+asserterrornumber)*100/carrynumber
        errorratio=Decimal(errorratio).quantize(Decimal('0.00'))
        response['errorratio']=errorratio
        response['passnumber'] = passnumber
        response['failnumber'] = failnumber
        response['asserterrornumber'] = asserterrornumber

        #如果StatisticsData表有数据则更新，没有则新增一条
        if len(StatisticsData.objects.all())>=1:
            StatisticsData.objects.update(casenumber=casenumber, tasknumber=tasknumber, carrynumber=carrynumber,
                                          passnumber=passnumber, asserterrornumber=asserterrornumber, failnumber=failnumber,
                                          errorratio=errorratio*100)
        else:
            StatisticsData.objects.create(casenumber=casenumber, tasknumber=tasknumber, carrynumber=carrynumber,
                                          passnumber=passnumber, asserterrornumber=asserterrornumber, failnumber=failnumber,
                                          errorratio=errorratio*100)

        #获取今日反馈量
        date = now().date() + timedelta(days=0)  # 今天
        todayfeedbacknumber=len(LogAndHtmlfeedback.objects.filter(update_time__gte=date))
        response["todayfeedbacknumber"]=todayfeedbacknumber

        #取每日执行数量
        test_carryTaskid = CarryTask.objects.values("id").aggregate(id=Max('id'))['id']
        passnumberlist=[]
        failnumberlist=[]
        asserterrornumberlist=[]
        carrynumberlist=[]
        for i in range(test_carryTaskid,test_carryTaskid-5,-1):
            passnumberlist.append(len(LogAndHtmlfeedback.objects.filter(test_carryTaskid=i,test_status=1).all()))
            failnumberlist.append(len(LogAndHtmlfeedback.objects.filter(test_carryTaskid=i, test_status=0).all()))
            asserterrornumberlist.append(len(LogAndHtmlfeedback.objects.filter(test_carryTaskid=i, test_status=2).all()))
            carrynumberlist.append(len(LogAndHtmlfeedback.objects.filter(test_carryTaskid=i).all()))
        response['passnumberlist']=passnumberlist
        response['failnumberlist'] = failnumberlist
        response['asserterrornumberlist'] = asserterrornumberlist
        response['carrynumberlist'] = carrynumberlist

        #获取反馈信息
        feedbackmessages=LogAndHtmlfeedback.objects.values('test_step','test_response','test_status','update_time').order_by("-id")
        for i in range(len(feedbackmessages)):
            if feedbackmessages[i]['test_response']=="":
                feedbackmessages[i]['test_response']="接口内部错误"
            if feedbackmessages[i]['test_status']==1:
                feedbackmessages[i]['test_status']="pass"
            elif feedbackmessages[i]['test_status']==0:
                feedbackmessages[i]['test_status'] = "fail"
            else:
                feedbackmessages[i]['test_status'] = "asserterror"
        response['messages']=feedbackmessages

        #获取今日报错信息
        errorfeedbackmessages = LogAndHtmlfeedback.objects.filter(~Q(test_status=1),update_time__gte=date).values('test_step', 'test_response', 'test_status',
                                                             'update_time').order_by("-id")
        #print (errorfeedbackmessages)
        for i in range(len(errorfeedbackmessages)):
            if errorfeedbackmessages[i]['test_response'] == "":
                errorfeedbackmessages[i]['test_response'] = "接口内部错误"
            if errorfeedbackmessages[i]['test_status'] == 1:
                errorfeedbackmessages[i]['test_status'] = "pass"
            elif errorfeedbackmessages[i]['test_status'] == 0:
                errorfeedbackmessages[i]['test_status'] = "fail"
            else:
                errorfeedbackmessages[i]['test_status'] = "asserterror"
        response['errorsmessages'] = errorfeedbackmessages
        return render(request, "./main/report.html", response)
    except:
        response['errorratio'] = 0
        response['passnumber'] = 0
        response['failnumber'] = 0
        response['asserterrornumber'] = 0
        response["todayfeedbacknumber"] = 0
        response['passnumberlist'] = [0,0,0,0,0]
        response['failnumberlist'] = [0,0,0,0,0]
        response['asserterrornumberlist'] = [0,0,0,0,0]
        response['carrynumberlist'] = [0,0,0,0,0]
        return render(request, "./main/report.html",response)