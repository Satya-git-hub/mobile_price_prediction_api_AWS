#uses CreateModelStep to save approved model to Sagemaker Models that can be used later for endpoints to real time inferencing

import os, sys, boto3, json, argparse
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

import sagemaker 
from sagemaker.workflow.parameters import ParameterInteger, ParameterString
from sagemaker.processing import ProcessingInput, ProcessingOutput 
from sagemaker.workflow.step import ProcessingStep
from sagemaker.workflow.pipeline import Pipeline 
from utils import load_config, get_session 
from datetime import datetime 
from sagemaker import utils 
from sagemaker.model import Model 
from sagemaker.workflow.steps import CreateModelStep 
from sagemaker.inputs import CreateModelInput 
from datetime import datetime 
from sagemaker import get_execution_role

cwd = os.getcwd()
sys.path.append(cwd)
os.chdir(cwd)

os.environ['AWS_DEFAULT_REGION'] = "ap-southeast-1"

try:
    constants = json.load(open("opt/ml/code/pipelines/sagemaker_jobs/constants.json",))
except Exception as e:
    constants = json.load(open("constants json",))
    print("Running consatants locally")
    
image_uri = sys.argv[1]
model_s3_uri = sys.argv[2]
environment = sys.argv[3]

bucket_name = constants[environment]["bucket_name"]["mlops_zone"]

# Pipeline Parameters
config_path = os.path.join("pipelines/sagemaker_jobs/config")
evaluate_config, training_pipeline_config, inference_pipeline_config, train_config, model_config, preprocess_config, explainability_config = load_config(config_path)

# Accessing configuration parameters

# Pipeline parameters
framework_version = inference_pipeline_config["pipeline"]["framework_version"]
region = inference_pipeline_config["pipeline"]["region"]
role = get_execution_role()
pipeline_name = "TopAdvisor-Pipeline-SG-Models"
usecase = inference_pipeline_config["pipeline"]["usecase"]

s3 = boto3.client("s3", region_name = "ap-southeast-1")
sm_client = boto3.client("sagemnaker")

def main(image_uri, bucket_name, model_s3_uri):
    sagemaker_session = get_session(region, bucket_name)
    s3_client = boto3.client("s3")

    #############################################   Create Model  #####################################################

    custom_prefix = "TopAdvisor-Model"
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    sg_model_name = f"{custom_prefix}-{timestamp}"

    model = Model(
        image_uri = image_uri,
        model_data = model_s3_uri,
        sagemaker_session = sagemaker_session,
        role = role,
        name = sg_model_name,
    )

    inputs = CreateModelInput(
        instance_type = "ml.m5.4xlarge",
        accelerator_type = "ml.eia1.medium",
    )

    step_create_model = CreateModelStep(
        name = custom_prefix, 
        model = model, 
        inputs = inputs,
        display_name = sg_model_name,
    )

    #############################################   Pipeline  #####################################################

    #Execution of Pipeline

    pipeline = Pipeline(
        name = pipeline_name,
        parameters = [ 
        ],
        steps = [step_create_model],
    )

    pipeline.upsert(role_arn = role)
    execution = pipeline.start()
    execution.wait(delay=300, max_attempts = 5)
    execution.list_steps()

if __name__ == "__main__":
    main(image_uri, bucket_name, model_s3_uri)