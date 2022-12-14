# Beta Calculation Single Ticker

Beta Calculation using AWS Pure Serverless Environment.
Technical Stack: Python, Flask, AWS Lambda, AWS API Gateway, plain html frontend, AWS S3 document db. 
This calculator shows how to use Lambda Adapter to run an Flask application on managed python runtime. 

### How does it work?
Prerequisites:
a. Docker Desktop
b. SAM CLI
c. AWS CLI
d. Python 3.9
e. AWS Account

We add Lambda Adapter layer to the function and configure wrapper script. 

1. attach Lambda Adapter layer to your function. This layer containers Lambda Adapter binary and a wrapper script. 
    1. x86_64: `arn:aws:lambda:${AWS::Region}:753240598075:layer:LambdaAdapterLayerX86:7`
    2. arm64: `arn:aws:lambda:${AWS::Region}:753240598075:layer:LambdaAdapterLayerArm64:7`
2. configure Lambda environment variable `AWS_LAMBDA_EXEC_WRAPPER` to `/opt/bootstrap`. This is a wrapper script included in the layer.
3. set function handler to a startup command: `run.sh`. The wrapper script will execute this command to boot up your application. 


To get more information of Wrapper script, please read Lambda documentation [here](https://docs.aws.amazon.com/lambda/latest/dg/runtimes-modify.html#runtime-wrapper). 

### Build and Deploy

Run the following commands to build and deploy the application to lambda. 

```bash
sam build --use-container
sam deploy --guided
```
When the deployment completes, take note of FlaskApi's Value. It is the API Gateway endpoint URL. 
![alt text](https://d2908q01vomqb2.cloudfront.net/1b6453892473a467d07372d45eb05abc2031647a/2020/12/16/process.png)
### Verify it works

Open FlaskApi's URL in a browser, you should see "calc beta Rest API endpint" on the page. 

