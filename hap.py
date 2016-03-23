#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, urllib2
import yaml,sys

class Service():
    def setName(self,name):
        self.name = name

    def setUrl(self,url):
        self.url = url

    def setRequestType(self,requestType):
        self.requestType = requestType

    def setHeaders(self,headersDict):
        self.headers = headersDict

    def setRequestParams(self,requestParamsDict):
        self.requestParams = requestParamsDict

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url 

    def getRequestType(self):
        return self.requestType 

    def getHeaders(self):
        return self.headers

    def getRequestParams(self):
        return self.requestParams 

class Node():
    def __init__(self):
        self.service = []

    def setService(self,service):
        self.service.append(service)
    
    def getServices(self):
        return self.service

class ParseConfig():
    def __init__(self,fileName):
        configFile = open(fileName,"r")
        configData = yaml.load(configFile)
        #print configData
        self.nodesCount = len(configData.keys())
        self.configData=configData
        self.exception = ['interval']

    def getNodes(self):
        self.nodes = []
        for node in self.configData:
            nodeObj = Node()
            # self.configData[node]["interval"] -> will give u interval
            for service in self.configData[node]["services"]:
                print service
                if service not in self.exception:
                    serviceObj = Service()
                    serviceObj.setName(service['name'])
                    serviceObj.setUrl(service['url'])
                    serviceObj.setRequestParams(service['request_params'])
                    serviceObj.setHeaders(service['headers'])
                    serviceObj.setRequestType(service['request_type'])
                    nodeObj.setService(serviceObj)
            self.nodes.append(nodeObj)
        return self.nodes


class Http():
    def __init__(self, proxy = False, cookie_support = False):
        self.handlers = set()
        if proxy:
            self.handlers |= set([
                urllib2.ProxyHandler({'http': 'http://%s'%self.proxy}),
                urllib2.HTTPBasicAuthHandler()]
            )
        if cookie_support:
            self.handlers |= set( 
                [urllib2.HTTPCookieProcessor()]
            )
        if self.handlers:
            self.interface = urllib2.build_opener( *self.handlers )
        else:
            self.interface = urllib2.build_opener(urllib2.BaseHandler)
        urllib2.install_opener(self.interface)
        self.interface.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1')]
       
    def prepare_request(self, url):
        request = urllib2.Request(url)
        #if referer:
        #    request.add_header('Referer',referer)
        return request


class Web():
    def __init__(self, proxy = False, cookie_support = False, timeout = 10):
        self.timeout = timeout 
        self.web = Http(proxy, cookie_support)
      
    def fetch(self, url, post=False,params={},headers={}):
        if post:
            params = urllib.urlencode(params)
        else:
            paramStr=""
            for param in params:
                paramStr += param+"="+params[param]+"&"
            url += "?"+paramStr
        request = self.web.prepare_request(url)
        for header in headers:
            request.add_header(header,headers[header])

        if post:
            response = self.web.interface.open(request, params, timeout = self.timeout)
        else:
            response = self.web.interface.open(request, timeout = self.timeout)

        self.response = response

    def getReponseData(self):
        return self.response.read()

    def getResponseHTTPCode(self) :
        return self.response.getcode()

#example usage
if __name__ == "__main__":
    #w = Web()
    #print w.fetch('http://google.com')
    configObj = ParseConfig("conf.yml")
    nodes = configObj.getNodes()
    for node in nodes:
        services = node.getServices()
        for service in services:
            print service.getUrl()
            print service.getRequestParams()
            print service.getHeaders()
            w = Web()
            w.fetch(service.getUrl(),False,service.getRequestParams(),service.getHeaders())
            print w.getResponseHTTPCode() 

