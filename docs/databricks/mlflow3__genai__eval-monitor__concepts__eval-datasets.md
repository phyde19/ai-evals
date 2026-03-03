<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/eval-datasets -->

On this page

Last updated on **Oct 28, 2025**

# Evaluation dataset reference

This page describes the evaluation dataset schema and includes links to the SDK reference for some of the most frequently used methods and classes.

For general information and examples of how to use evaluation datasets, see [Evaluate GenAI during development](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>).

## Evaluation dataset schemaâ

Evaluation datasets must use the schema described in this section.

### Core fieldsâ

The following fields are used in both the evaluation dataset abstraction or if you pass data directly.

Column| Data Type| Description| Required| `inputs`| `dict[Any, Any]`| Inputs for your app (e.g., user question, context), stored as a JSON-seralizable `dict`.| Yes| `expectations`| `dict[Str, Any]`| Ground truth labels, stored as a JSON-seralizable `dict`.| Optional  
---|---|---|---  
  
#### `expectations` reserved keysâ

`expectations` has several reserved keys that are used by built-in LLM judges: `guidelines`, `expected_facts`, and `expected_response`.

Field| Used by| Description| `expected_facts`| `Correctness` judge| List of facts that should appear| `expected_response`| `Correctness` judge| Exact or similar expected output| `guidelines`| `Guidelines` judge| Natural language rules to follow| `expected_retrieved_context`| `document_recall` scorer| Documents that should be retrieved  
---|---|---  
  
### Additional fieldsâ

The following fields are used by the evaluation dataset abstraction to track lineage and version history.

Column| Data Type| Description| Required| `dataset_record_id`| string| The unique identifier for the record.| Automatically set if not provided.| `create_time`| timestamp| The time when the record was created.| Automatically set when inserting or updating.| `created_by`| string| The user who created the record.| Automatically set when inserting or updating.| `last_update_time`| timestamp| The time when the record was last updated.| Automatically set when inserting or updating.| `last_updated_by`| string| The user who last updated the record.| Automatically set when inserting or updating.| `source`| struct| The source of the dataset record. See Source field.| Optional| `tags`| dict[str, Any]| Key-value tags for the dataset record.| Optional  
---|---|---|---  
  
#### Source fieldâ

The `source` field tracks where a dataset record came from. Each record can have **only one** source type.

**Human source** : Record created manually by a person

Python
    
    
    {  
        "source": {  
            "human": {  
                "user_name": "jane.doe@company.com"  # user who created the record  
            }  
        }  
    }  
    

**Document source** : Record synthesized from a document

Python
    
    
    {  
        "source": {  
            "document": {  
                "doc_uri": "s3://bucket/docs/product-manual.pdf",  # URI or path to the source document  
                "content": "The first 500 chars of the document..."  # Optional, excerpt or full content from the document  
            }  
        }  
    }  
    

**Trace source** : Record created from a production trace

Python
    
    
    {  
        "source": {  
            "trace": {  
                "trace_id": "tr-abc123def456". # unique identifier of the source trace  
            }  
        }  
    }  
    

## MLflow evaluation dataset UIâ

## MLflow evaluation dataset SDK referenceâ

The evaluation datasets SDK provides programmatic access to create, manage, and use datasets for GenAI app evaluation. For details, see the API reference: [`mlflow.genai.datasets`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#module-mlflow.genai.datasets>). Some of the most frequently used methods and classes are the following:

  * [`mlflow.genai.datasets.create_dataset`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.create_dataset>)
  * [`mlflow.genai.datasets.get_dataset`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.get_dataset>)
  * [`mlflow.genai.datasets.delete_dataset`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.delete_dataset>)
  * [`EvaluationDataset`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.EvaluationDataset>). This class provides methods to interact with and modify evaluation datasets.