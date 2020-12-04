import os
import logging
import jsonpickle
import boto3
import COPASI
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()

client = boto3.client('lambda')
client.get_account_settings()

dm = COPASI.CRootContainer.addDatamodel()
assert(isinstance(dm, COPASI.CDataModel))

def execute_active_task(file_name):
    """
    This function loads the given COPASI file, goes through the tasks and executes the first one marked 
    as 'schedule' afterwards it will save the copasi_file (forcing update model to be checked, so that the 
    updated state is saved. 
    
    This function returns a tuple of (report_file, copasi_file) where the report file is the report file created
    and filename the file with the updated state.
    """
    logger.info('## Loading file: ' + file_name)
    if not dm.loadModel(file_name): 
        raise ValueError("Couldn't open file: {0}".format(file_name))

    for task in dm.getTaskList():   
        if task.isScheduled():
            assert(isinstance(task, COPASI.CCopasiTask))
            logger.info("## Task {0} was marked as executable".format(task.getObjectName()))
            report_file = task.getReport().getTarget()
            if not report_file: 
                logger.info("## no report file defined for scheduled task {0} skipping".format(task.getObjectName()))
                continue

            # make it an absolute path
            report_file = os.path.abspath(os.path.join(
                os.path.split(file_name)[0],
                report_file
            ))

            task.setUpdateModel(True) # ensure the model is updated with new values at the end
            
            # now execute task
            task.initializeRaw(COPASI.CCopasiTask.OUTPUT_SE)
            task.processRaw(True)

            # and save the model
            output_file = os.path.abspath(os.path.join(
                os.path.split(file_name)[0],
                os.path.splitext(os.path.basename(file_name))[0] + '_out.cps'
            ))
            # remember when this is run concurrently, ensure that the filenames are unique in a better way
            dm.saveModel(output_file, True)

            # return the values
            return report_file, output_file
    
    logger.error("## no task was marked as executable (or had no report defined), nothing was run")
    raise ValueError('Need to have scheduled task with report defined to run')


def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    logger.info('## COPASI VERSION\r' + jsonpickle.encode(COPASI.CVersion.VERSION.getVersion()))

    # this basic example expects the event to contain a filename to be simulated. 
    # in a real example, you'd first get the COPASI file from an S3 bucket, save it to 
    # /tmp and then call the function below with the filename. 
    
    # for parameter estimation we need to also copy all the experimental data files, 
    # or you could choose to export a COMBINE archive from COPASI and upload that to AWS
    # it will contain the experimental data.
    
    # here we just bundled the 'brusselator.cps' file right next to the script, so lets take it from here
    
    file_name = event['Records'][0]['body']
    file_name = os.path.abspath(os.path.join(os.path.split(__file__)[0], file_name))
    report_file, copasi_file = execute_active_task(file_name)

    # at this point you'd copy the report_file and the copasi_file to a target S3 bucket for later.
    # here i just return the time course result in the body, including the filenames
    
    with open(report_file, 'r') as data_file:
      data = data_file.read()
    
    response = { 
        'data': data, 
        'report_file': report_file, 
        'copasi_file': copasi_file
        }
    return response
