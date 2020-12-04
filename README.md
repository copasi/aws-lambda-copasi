## Using python-copasi with AWS Lambda
This basic example demonstrates the use of `python-copasi` for use with AWS lambda. It will 

* create a python3.8 layer that pulls python-copasi
* contain a sample function, that when invoked by a trigger, will take the given COPASI file, and simulate it, and returning the result of the simulation.

The project is based on the [`blank-python`](https://github.com/awsdocs/aws-lambda-developer-guide/tree/master/sample-apps/blank-python) sample app. So i suggest going there and reading up on the tutorial, as here i just follow the same steps. 

## The lambda
In this simple test, the brusselator model from the function directory will be simulated by the lambda. In an effort not to hard code too many things, the actual filename is taken from the lambda parameters (where the body contains the name of the file to load). Also the task to be executed is taken from the COPASI file. In the sample file i've ensured that the time course task is selected. The task to be executed will have to have a report defined (which the lambda then reads back in and returns).  

## Local Test: 

using a local Ubuntu 20.04 LTS version with python 3.8, and aws installed. Create a new virtual environment: 

	python3 -m venv aws-test

activate it: 

	. ./aws-test/bin/activate

install the requirements: 

	pip install -r ./function/requirements.txt


then you are ready to run the local unit tests by executing `./0-run-tests.sh`. This should yield output like this: 

	(aws-test) fbergmann@BQFRANK:/aws-lambda-copasi$ ./0-run-tests.sh
	## EVENT
	{"Records": [{"messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78", "receiptHandle": "MessageReceiptHandle", "body": "brusselator.cps", "attributes": {"ApproximateReceiveCount": "1", "SentTimestamp": "1523232000000", "SenderId": "123456789012", "ApproximateFirstReceiveTimestamp": "1523232000001"}, "messageAttributes": {}, "md5OfBody": "7b270e59b47ff90a553787216d55d91d", "eventSource": "aws:sqs", "eventSourceARN": "arn:aws:sqs:us-west-2:123456789012:MyQueue", "awsRegion": "us-west-2"}]}
	{'data': 'Time\t[X]\t[Y]\n0\t3\t3\n1.5\t0.876253\t1.87293\n3\t0.147433\t2.86368\n4.5\t0.141557\t3.40697\n6\t0.145096\t3.93852\n7.5\t0.149106\t4.46391\n9\t0.153591\t4.98247\n10.5\t0.158671\t5.49327\n12\t0.164515\t5.99515\n13.5\t0.17138\t6.4865\n15\t0.179681\t6.96512\n16.5\t0.190149\t7.42762\n18\t0.204272\t7.86829\n19.5\t0.225831\t8.27552\n21\t0.269739\t8.61505\n22.5\t0.618644\t8.48236\n24\t2.53937\t1.03681\n25.5\t0.232012\t2.53954\n27\t0.140639\t3.14359\n28.5\t0.143282\t3.6784\n30\t0.147084\t4.20688\n', 'report_file': '/aws-lambda-copasi/function/brusselator_data.txt', 'copasi_file': '/aws-lambda-copasi/function/brusselator_out.cps'}
	.
	----------------------------------------------------------------------
	Ran 1 test in 0.137s
	
	OK 

## Deploy to AWS

Now its time to deploy the package to AWS. Here we just run the same scripts as given by the sample app.  

### 1-create-bucket.sh
This script created a bucket on s3, for uploading the layer later on. 

### 2-build-layer.sh
this script creates a layer with `python-copasi` and `boto3`. After this is done all packages needed to run copasi tasks are present in the `./package` directory.

### 3-deploy.sh
this file uploads all the package things onto the bucket that was created.

	(aws-test) fbergmann@BQFRANK:/aws-lambda-copasi$ ./3-deploy.sh
	Uploading to 779c89fe429489b1642f2e43cf1448d9  19812441 / 19812441.0  (100.00%)
	Successfully packaged artifacts and wrote output template to file out.yml.
	Execute the following command to deploy the packaged template
	aws cloudformation deploy --template-file /aws-lambda-copasi/out.yml --stack-name <YOUR STACK NAME>
	
	Waiting for changeset to be created..
	Waiting for stack create/update to complete
	Successfully created/updated stack - copasi-python 

### 4-invoke.sh 
runs the lambda function with the data from the local json file. I get output like this, when running it: 
	
	(aws-test) fbergmann@BQFRANK:/aws-lambda-copasi$ ./4-invoke.sh
	{
	    "StatusCode": 200,
	    "ExecutedVersion": "$LATEST"
	}
	{"data": "Time\t[X]\t[Y]\n0\t3\t3\n1.5\t0.876253\t1.87293\n3\t0.147433\t2.86368\n4.5\t0.141557\t3.40697\n6\t0.145096\t3.93852\n7.5\t0.149106\t4.46391\n9\t0.153591\t4.98247\n10.5\t0.158671\t5.49327\n12\t0.164515\t5.99515\n13.5\t0.17138\t6.4865\n15\t0.179681\t6.96512\n16.5\t0.190149\t7.42762\n18\t0.204272\t7.86829\n19.5\t0.225831\t8.27552\n21\t0.269739\t8.61505\n22.5\t0.618644\t8.48236\n24\t2.53937\t1.03681\n25.5\t0.232012\t2.53954\n27\t0.140639\t3.14359\n28.5\t0.143282\t3.6784\n30\t0.147084\t4.20688\n", "report_file": "/var/task/brusselator_data.txt", "copasi_file": "/var/task/brusselator_out.cps"}
	{
	    "StatusCode": 200,
	    "ExecutedVersion": "$LATEST"
	}
	{"data": "Time\t[X]\t[Y]\n0\t3\t3\n1.5\t0.876253\t1.87293\n3\t0.147433\t2.86368\n4.5\t0.141557\t3.40697\n6\t0.145096\t3.93852\n7.5\t0.149106\t4.46391\n9\t0.153591\t4.98247\n10.5\t0.158671\t5.49327\n12\t0.164515\t5.99515\n13.5\t0.17138\t6.4865\n15\t0.179681\t6.96512\n16.5\t0.190149\t7.42762\n18\t0.204272\t7.86829\n19.5\t0.225831\t8.27552\n21\t0.269739\t8.61505\n22.5\t0.618644\t8.48236\n24\t2.53937\t1.03681\n25.5\t0.232012\t2.53954\n27\t0.140639\t3.14359\n28.5\t0.143282\t3.6784\n30\t0.147084\t4.20688\n", "report_file": "/var/task/brusselator_data.txt", "copasi_file": "/var/task/brusselator_out.cps"}

### 5-cleanup.sh
deletes the buckets and stacks created.

## Conclusion
the python api works great on AWS. But it did not run out of the box for me, COPASI needed a HOME variable to be set, and that was not the case on the AWS environment. So that is why the template script here does set the variable. A future version of COPASI will not require this. 