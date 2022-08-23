# serializeImageData Lambda Function

import json
import boto3
import base64

s3_resource = boto3.resource('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    
    my_bucket = s3_resource.Bucket(bucket)
    my_bucket.download_file(key, '/tmp/image.png')
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }



#--------------------------------------------------------------------------#
# scones-classification-function Lambda Function

import json
import boto3
import base64

runtime= boto3.client('runtime.sagemaker')
# Fill this in with the name of your deployed model
ENDPOINT = "scones-endpoint"

def lambda_handler(event, context):

    # Decode the image data
    print(event.keys())
    image = base64.b64decode(event['image_data'])

    # Make_prediction
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT, ContentType='image/png', Body=image)
    
    # We return the data back to the Step Function    
    event["inferences"] = json.loads(response['Body'].read().decode('utf-8'))
    return {
        'statusCode': 200,
        'body': event
    }



#--------------------------------------------------------------------------#
# scones-filter-low-confidence Lambda Function

import json


THRESHOLD = .93


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any([x >THRESHOLD for x in inferences])
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': event
    }