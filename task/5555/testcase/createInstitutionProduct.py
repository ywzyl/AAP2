#!/usr/bin/python
#-*- encoding:UTF-8 -*-

from public.request import *
from public.sqldb import *
from public.log import *
from public.run import *
from public.sqldb import Transferip_db
from public.mongodb import Transferip_mongodb
import unittest,re,json

class createInstitutionProduct(unittest.TestCase):
    ''''''
    @classmethod
    def setUpClass(cls):
        cls.transferlogname=Transferlogname()
        cls.transferip_db=Transferip_db()
        cls.transfermongodb = Transferip_mongodb()
        api="/xdd-finance-web/admin/createInstitutionProduct"
        cls.url=cls.transferip_db.ip+api
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def getAssertWay(self,assertway):
        if assertway=="assertEqual":
            Assertwaymessage="等于"
        elif assertway=="assertNotEqual":
            Assertwaymessage="不等于"
        elif assertway=="assertRegexpMatches":
            Assertwaymessage="包含"
        elif assertway=="assertNotRegexpMatches":
            Assertwaymessage="不包含"
        elif assertway=="assertGreater":
            Assertwaymessage="大于"
        elif assertway=="assertGreaterEqual":
            Assertwaymessage="大于等于"
        elif assertway=="assertLess":
            Assertwaymessage="小于"
        elif assertway=="assertLessEqual":
            Assertwaymessage="小于等于"
        elif assertway=="assertIn":
            Assertwaymessage="在列表中"
        elif assertway=="assertNotIn":
            Assertwaymessage="不在列表中"
        return Assertwaymessage

    def test_createInstitutionProduct02(self):
        '''创建机构产品'''
        step_name="createInstitutionProduct02"
        makesqldata=None
        newVariableObj={}
        sqlDatalist=[{'sql_condition': 1, 'is_select': True, 'variable': 'loan_amount', 'sql': "select loan_amount from f_institution_product where name='sxd'"}]
        api_dependency={}
        #查找接口依赖数据
        search_mongo_result=self.transfermongodb.mongodb.search_one(self.transferlogname.test_carryid,api_dependency)
        
        for sqlDatalistCount in range(len(sqlDatalist)):
            sqlData=sqlDatalist[sqlDatalistCount]
            if sqlData['sql_condition']==0:
                if sqlData['is_select']!=True:
                    self.transferip_db.db.ExecNoQuery(sqlData['sql'])
                else:
                    makesqldata=MakeSqlData(sqlData['variable'],sqlData['sql'])
                    newVariableObj=dict(newVariableObj,**makesqldata.variableObj)
                if makesqldata:
                    sqlDatalist=json.dumps(sqlDatalist,ensure_ascii = False)
                    for i in makesqldata.variableObj.keys():
                        regex=r"\${"+i+r"}"
                        sqlDatalist = re.sub(regex, str(makesqldata.variableObj[i]), sqlDatalist)
                    sqlDatalist=json.loads(sqlDatalist)
                else:
                    #makesqldata not exist,not sql
                    pass 
        params={"id": 21,"institutionId": 2,"institutionName": "XDL","interestRate": 2,"label": "2","labelId": 2,"loanAmount": "300000","loanSpeed": "3","name": "sxd","sort": 21,"status": 1}
        headers={"Content-Type":"application/json","userCookiesName":"km_ft_test","User-Agent":"PostmanRuntime/7.13.0","Accept":"*/*","Cache-Control":"no-cache","Postman-Token":"233fb312-a9c7-44ab-ac70-f1e66ddd0f47,379589a1-5b73-4b47-aa06-39ebee1a8019","Host":"finance.cs.xiangqianpos.com","cookie":"SERVERID=e98aa6e654c9fa4087fe9a140002da81|1558942076|1558942076","accept-encoding":"gzip, deflate","content-length":"216","Connection":"keep-alive","cache-control":"no-cache"}
        
        #追加替换变量字典
        newVariableObj.update(search_mongo_result)
        
        #replace variable
        if makesqldata or api_dependency!={}:
            params=json.dumps(params,ensure_ascii = False)
            headers=json.dumps(headers,ensure_ascii = False)
            for i in newVariableObj.keys():
                regex=r"\${"+i+r"}"
                params = re.sub(regex, str(newVariableObj[i]), params)
                headers = re.sub(regex, str(newVariableObj[i]), headers)
            params=json.loads(params)
            headers=json.loads(headers)
        else:
            #makesqldata not exist,not sql
            pass 
        responseJson=postbody(url=self.url,params=params,headers=headers)
        #print(responseJson)
        #print("=======")
        #插入mongodb数据
        document={}
        document['test_carryid'] = self.transferlogname.test_carryid
        document['step_name']=step_name
        document['responseJson'] = responseJson
        self.transfermongodb.mongodb.insert_one(document)
        
        #__init__
        makesqldata=None
        newVariableObj={}
        for sqlDatalistCount in range(len(sqlDatalist)):
            sqlData=sqlDatalist[sqlDatalistCount]
            if sqlData['sql_condition']==1:
                if sqlData['is_select']!=True:
                    self.transferip_db.db.ExecNoQuery(sqlData['sql'])
                else:
                    makesqldata=MakeSqlData(sqlData['variable'],sqlData['sql'])
                    newVariableObj=dict(newVariableObj,**makesqldata.variableObj)
                if makesqldata:
                    sqlDatalist=json.dumps(sqlDatalist,ensure_ascii = False)
                    for i in makesqldata.variableObj.keys():
                        regex=r"\${"+i+r"}"
                        sqlDatalist = re.sub(regex, str(makesqldata.variableObj[i]), sqlDatalist)
                    sqlDatalist=json.loads(sqlDatalist)
                else:
                    #makesqldata not exist,not sql
                    pass 
        assert_response={"['code']":{"assertEqual":"0"}}
        #replace assert_response
        if makesqldata:
            assert_response=json.dumps(assert_response,ensure_ascii = False)
            for i in newVariableObj.keys():
                regex=r"\${"+i+r"}"
                assert_response = re.sub(regex, str(newVariableObj[i]), assert_response)
            assert_response=json.loads(assert_response)
        else:
            #makesqldata not exist,not sql
            pass 
            
        way="postbody"
        for i in assert_response.keys():
            responseJsonAssert=responseJson
            #断言key遍历
            regexkey = r"\[(.+?)\]"
            resultlist = re.findall(regexkey, i)
            regexkey1 = r"'"
            for j in resultlist:
                if len(re.findall(regexkey1, j)) == 0:
                    j = int(j)
                else:
                    j = re.sub(regexkey1, "", j)
                responseJsonAssert = responseJsonAssert[j]
            #断言
            try:
                for k in assert_response[i].keys():
                    self.chooseAssertWay(str(responseJsonAssert),k,assert_response[i][k])
            except:
                @Log(self.transferlogname.Errorlogname, level="ERROR")
                def writeLog(step_name,url, way, header, params,message,assertResult):
                    print("write Errorlogname")
                Assertwaymessage=self.getAssertWay(k)
                #writeLog(step_name,self.url,way,headers,params,responseJson['message'],str(responseJsonAssert)+Assertwaymessage+assert_response[i][k])
                writeLog(step_name,self.url,way,headers,params,"接口测试断言错误",str(responseJsonAssert)+Assertwaymessage+assert_response[i][k])
                self.chooseAssertWay(str(responseJsonAssert), k, assert_response[i][k])
        pass
        @Log(self.transferlogname.Successlogname, level="INFO")
        def writeLog(step_name,url, way, header, params,message):
            print("write Successlogname")
        writeLog(step_name,self.url,way,headers,params,"接口测试通过")
