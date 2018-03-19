# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.utils import timezone
from job.models import Document
from job.forms import DocumentForm
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import os
import json

def display(request):
	documents = Document.objects.all()
	return HttpResponse(documents)
	
def status(request):
        print "hello"
	if request.method == 'GET':
		id = request.GET['id']
		#jbname = "job_"+str(request.user.id)+"_"+str(jobpk)
		uid = str(request.user.id)
		path = "media/"+uid+"/"+str(id)+"/output.txt"
		
		try:
			file = open(path,'r')
			res = file.read()
			file.close()
		except:
			res = "Can not found !"
			#res = os.popen("cat path").read()
		
		return HttpResponse(
			json.dumps({"result": res, "id" : id}),
			content_type="application/json"
		)
	else:
		return HttpResponse(
			json.dumps({"error": "not_GET"}),
			content_type="application/json"
		)
		
		
def execute(request):
	if request.method == 'GET':
	
		jobpk = request.GET['id']
		#cmd = "cp scripts/run_script.sh media/"+str(request.user.id)+"/"+str(jobpk)+"/run_script.sh"
		jbname = "job_"+str(request.user.id)+"_"+str(jobpk)
		cmd = "\
			cd media/"+str(request.user.id)+"/"+str(jobpk)+";\
			INPUT=input.txt;\
			INPUT_DIR=/input;\
			OUTPUT=output.txt;\
			OUTPUT_DIR=/output/;\
                        arg3=`cat input.txt|wc -l`;\
			MinSUPP=`cat min_sup.txt`;\
			k=`cat k.txt`;\
                        arg5=`cat input.txt | wc -L`;\
			sh /home/hadoop/hadoop-1.2.1/bin/hadoop dfs -rm -r -f $INPUT_DIR;\
			sh /home/hadoop/hadoop-1.2.1/bin/hadoop dfs -mkdir /input;\
			sh /home/hadoop/hadoop-1.2.1/bin/hadoop dfs -put $INPUT $INPUT_DIR;\
			sh /home/hadoop/hadoop-1.2.1/bin/hadoop dfs -rm -r -f $OUTPUT_DIR;\
			sh /home/hadoop/hadoop-1.2.1/bin/hadoop jar ~/BitMining_argvis5_for_webtest.jar $INPUT_DIR $OUTPUT_DIR $arg3 $MinSUPP $arg5;\
			sh /home/hadoop/hadoop-1.2.1/bin/hadoop dfs -cat /output/8/part* > $OUTPUT;\
		"
		res = os.popen(cmd).read()
		
		return HttpResponse(
			json.dumps({"result": "ok", "id" : jobpk}),
			content_type="application/json"
		)
	
	else:
		return HttpResponse(
			json.dumps({"error": "not_GET"}),
			content_type="application/json"
		)
		
@login_required
def job(request):
	r = Document.objects.order_by('-datetime')
	form = DocumentForm()
	return render(request,"job.html",locals())

def delete(request,id):

	if request.method == 'DELETE':
	
		uid = str(request.user.id)
		path = "media/"+uid+"/"+str(id)
		res = os.popen("rm -r "+path).read()
		document = Document.objects.get(id=id)
		document.delete()
		

		return HttpResponse(
			json.dumps({"result": "ok", "id" : id}),
			content_type="application/json"
		)
	else:
		return HttpResponse(
			json.dumps({"error": "not_DELETE"}),
			content_type="application/json"
		)
	
def upload(request):

    # Handle file upload
	if request.method == 'POST':

		f = DocumentForm(request.POST)
		if f.is_valid():
		
			jobname = f.cleaned_data['jobname']
			time_now = timezone.now()
			c = Document.objects.create(
					datetime = time_now,
					user = request.user,
					jobname = jobname,
					status = "NEW JOB"
				)
			id = c.id

			uid = (request.user.id)
			path = "media/"+str(uid)+"/"+str(id)
			if not os.path.exists(path):
				os.makedirs(path)
			
			file1 = f.cleaned_data['file1']
			ff = open(path+"/min_sup.txt",'w')  
			ff.write(file1)
			ff.close()
			
			file1 = f.cleaned_data['file2']
			ff = open(path+"/k.txt",'w')  
			ff.write(file1)
			ff.close()
			
			file1 = f.cleaned_data['file3']
			ff = open(path+"/input.txt",'w')  
			ff.write(file1)
			ff.close()		
			
			response_data = {}
			response_data['jobname'] = c.jobname
			response_data['created_time'] = c.datetime.strftime('%b. %d, %Y %I:%M %P')
			response_data['id'] = c.id
			response_data['status'] = c.status
			
			return HttpResponse(
				json.dumps(response_data),
				content_type="application/json"
			)
		else:

			# Prepare JSON for parsing
			errors_dict = {}
			if f.errors:
				for error in f.errors:
					e = f.errors[error]
					errors_dict[error] = e
			return HttpResponseBadRequest(json.dumps(errors_dict))

	else:
		return HttpResponse(
			json.dumps({"error": "not_POST"}),
			content_type="application/json"
		)
