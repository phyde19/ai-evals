<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/link-production-traces-to-app-versions -->

On this page

Last updated on **Feb 5, 2026**

# Link Production Traces to App Versions

The [track application versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>) guide showed how to track application versions using [`LoggedModel`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html?highlight=loggedmodel#mlflow.entities.LoggedModel>) during development.

When deploying a `LoggedModel` to production, you need to link the traces it generates back to the specific version for monitoring and debugging. This guide shows how to configure your deployment to include version information in production traces.

tip

**Deploying on Apps or Model Serving** Trace linking is automatically configured for you. Skip to Trace Linking on Databricks for details.

## Prerequisitesâ

  1. For production deployments **outside of Databricks Model Serving** , install the `mlflow-tracing` package:

Bash
         
         pip install --upgrade "mlflow-tracing>=3.1.0"  
         

This package is specifically optimized for production environments, offering:

     * **Minimal dependencies** for faster, leaner deployments
     * **Performance optimizations** for high-volume tracing

note

MLflow 3 is required for production tracing. MLflow 2.x is not supported for production deployments due to performance limitations and missing features for production use.

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).




## Environment Variable Configurationâ

  1. Navigate to the **versions** tab to get the `LoggedModel` ID. In your CI/CD pipeline, you can generate a new `LoggedModel` by using [`create_external_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=create_external_model#mlflow.create_external_model>) as shown below. We suggest using the



Python
    
    
    import mlflow  
    import subprocess  
      
    # Define your application and its version identifier  
    app_name = "customer_support_agent"  
      
    # Get current git commit hash for versioning  
    try:  
        git_commit = (  
            subprocess.check_output(["git", "rev-parse", "HEAD"])  
            .decode("ascii")  
            .strip()[:8]  
        )  
        version_identifier = f"git-{git_commit}"  
    except subprocess.CalledProcessError:  
        version_identifier = "local-dev"  # Fallback if not in a git repo  
      
    logged_model_name = f"{app_name}-{version_identifier}"  
      
    # Create a new LoggedModel  
    model = mlflow.create_external_model(name=logged_model_name)  
    

  2. Add the `LoggedModel` ID to your production environment configuration in the `MLFLOW_ACTIVE_MODEL_ID` environment variable alongside the standard MLflow tracing variables from the setup your environment quickstart.



Bash
    
    
    # Standard MLflow tracing configuration  
    export DATABRICKS_HOST="https://your-workspace.databricks.com"  
    export DATABRICKS_TOKEN="your-databricks-token"  
    export MLFLOW_TRACKING_URI=databricks  
    # Either use MLFLOW_EXPERIMENT_NAME or MLFLOW_EXPERIMENT_ID  
    export MLFLOW_EXPERIMENT_NAME="/Shared/production-genai-app"  
      
    # Add LoggedModel version tracking by specifying your LoggedModel ID  
    # Ensure this matches a LoggedModel in your MLFlow Experiment  
    export MLFLOW_ACTIVE_MODEL_ID="customer_support_agent-git-98207f02"  
    

## Automatic Trace Linkingâ

important

When you set the `MLFLOW_ACTIVE_MODEL_ID` environment variable, **all traces are automatically linked to that LoggedModel**. You don't need to manually tag traces - MLflow handles this for you!

Your application code remains exactly the same as during development:

Python
    
    
    import mlflow  
    from fastapi import FastAPI, Request  
      
    app = FastAPI()  
      
    @mlflow.trace  
    def process_message(message: str) -> str:  
        # Your actual application logic here  
        # This is just a placeholder  
        return f"Processed: {message}"  
      
    @app.post("/chat")  
    def handle_chat(request: Request, message: str):  
        # Your traces are automatically linked to the LoggedModel  
        # specified in MLFLOW_ACTIVE_MODEL_ID  
      
        # Your application logic here  
        response = process_message(message)  
        return {"response": response}  
    

To add additional context to your traces (such as user IDs, session IDs, or custom metadata), see [Add context to traces](</aws/en/mlflow3/genai/tracing/add-context-to-traces>) in the production tracing guide.

## Deployment Examplesâ

### Dockerâ

When deploying with Docker, pass all necessary environment variables through your container configuration:

Dockerfile
    
    
    # Dockerfile  
    FROM python:3.9-slim  
      
    # Install dependencies  
    COPY requirements.txt .  
    RUN pip install -r requirements.txt  
      
    # Copy application code  
    COPY . /app  
    WORKDIR /app  
      
    # Declare required environment variables (no defaults)  
    ENV DATABRICKS_HOST  
    ENV DATABRICKS_TOKEN  
    ENV MLFLOW_TRACKING_URI  
    ENV MLFLOW_EXPERIMENT_NAME  
    ENV MLFLOW_ACTIVE_MODEL_ID  
      
    CMD ["python", "app.py"]  
    

Run the container with environment variables:

Bash
    
    
    docker run -d \  
      -e DATABRICKS_HOST="https://your-workspace.databricks.com" \  
      -e DATABRICKS_TOKEN="your-databricks-token" \  
      -e MLFLOW_TRACKING_URI=databricks \  
      -e MLFLOW_EXPERIMENT_NAME="/Shared/production-genai-app" \  
      -e MLFLOW_ACTIVE_MODEL_ID="customer_support_agent-git-98207f02" \  
      -e APP_VERSION="1.0.0" \  
      your-app:latest  
    

### Kubernetesâ

For Kubernetes deployments, use ConfigMaps and Secrets to manage configuration:

YAML
    
    
    # configmap.yaml  
    apiVersion: v1  
    kind: ConfigMap  
    metadata:  
      name: mlflow-config  
    data:  
      DATABRICKS_HOST: 'https://your-workspace.databricks.com'  
      MLFLOW_TRACKING_URI: 'databricks'  
      MLFLOW_EXPERIMENT_NAME: '/Shared/production-genai-app'  
      MLFLOW_ACTIVE_MODEL_ID: 'customer_support_agent-git-98207f02'  
      
    ---  
    # secret.yaml  
    apiVersion: v1  
    kind: Secret  
    metadata:  
      name: databricks-secrets  
    type: Opaque  
    stringData:  
      DATABRICKS_TOKEN: 'your-databricks-token'  
      
    ---  
    # deployment.yaml  
    apiVersion: apps/v1  
    kind: Deployment  
    metadata:  
      name: genai-app  
    spec:  
      replicas: 2  
      selector:  
        matchLabels:  
          app: genai-app  
      template:  
        metadata:  
          labels:  
            app: genai-app  
        spec:  
          containers:  
            - name: app  
              image: your-app:latest  
              ports:  
                - containerPort: 8000  
              envFrom:  
                - configMapRef:  
                    name: mlflow-config  
                - secretRef:  
                    name: databricks-secrets  
              env:  
                - name: APP_VERSION  
                  value: '1.0.0'  
              resources:  
                requests:  
                  memory: '256Mi'  
                  cpu: '250m'  
                limits:  
                  memory: '512Mi'  
                  cpu: '500m'  
    

## Querying Version-Specific Tracesâ

Once deployed, you can view traces in the MLflow trace UI or you can query traces by model version in the SDK:

Python
    
    
    import mlflow  
      
    # Get the experiment ID  
    experiment = client.get_experiment_by_name("/Shared/production-genai-app")  
      
    # Find all traces from a specific model version  
    traces = mlflow.search_traces(  
        experiment_ids=[experiment.experiment_id],  
        model_id="customer_support_agent-git-98207f02",  
    )  
      
    # View the results  
    print(f"Found {len(traces)} traces for this model version")  
    

## Trace Linking on Databricks Apps and Model Servingâ

When you [Deploy on Apps](</aws/en/generative-ai/agent-framework/author-agent>) and MLflow 3 is installed in your development environment, trace linking is automatically configured.

To view traces from your Databricks Model Serving endpoint:

  1. Navigate to the MLflow Experiment that was active when you called `agents.deploy()`
  2. Click on the **Traces** tab to view traces
  3. All traces are automatically linked to the specific model version serving the requests



The only requirement is that your application code uses MLflow tracing (either through autologging or manual instrumentation with `@mlflow.trace`).

## Next stepsâ

For complete production tracing setup including authentication, monitoring, and feedback collection for deployments outside Databricks Model Serving, see [Production observability with tracing](</aws/en/mlflow3/genai/tracing/prod-tracing>).