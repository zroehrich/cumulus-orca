[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_files_to_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

**Lambda function request_status_for_granule **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc request_status_for_granule](#pydoc)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
Input with granule_id and asyncOperationId.
```json
{
  "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85"
}
```
Input with no asyncOperationId. Only the most recent operation for the granule will be queried.
```json
{
  "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250"
}
```

### Example Output
```json
{
  "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "files": [
    {
      "fileName": "f1.doc",
      "status": "pending"
    },
    {
      "fileName": "f2.pdf",
      "status": "failed",
      "errorMessage": "Access Denied"
    },
    {
      "fileName": "f3.txt",
      "status": "success"
    }
  ],
  "restoreDestination": "bucket_name",
  "requestTime": 628021800000,
  "completionTime": 628021900000
}
```
<a name="pydoc"></a>
## pydoc request_status_for_granule
```
Help on module request_status_for_granule:

NAME
    request_status_for_granule

FUNCTIONS
    create_http_error_dict(error_type: str, http_status_code: int, request_id: str, message: str) -> Dict[str, Any]
        Creates a standardized dictionary for error reporting.
        Args:
            error_type: The string representation of http_status_code.
            http_status_code: The integer representation of the http error.
            request_id: The incoming request's id.
            message: The message to display to the user and to record for debugging.
        Returns:
            A dict with the following keys:
                'errorType' (str)
                'httpStatus' (int)
                'requestId' (str)
                'message' (str)
    
    get_file_entries_for_granule_in_job(granule_id: str, job_id: str, engine: sqlalchemy.future.engine.Engine) -> List[Dict]
        Gets the individual status entries for the files for the given job+granule.
        
        Args:
            granule_id: The id of the granule to get file statuses for.
            job_id: The id of the job to get file statuses for.
            engine: The sqlalchemy engine to use for contacting the database.
        
        Returns: A Dict with the following keys:
            'file_name' (str): The name and extension of the file.
            'restore_destination' (str): The name of the glacier bucket the file is being copied to.
            'status' (str): The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.
            'error_message' (str): If the restoration of the file errored, the error will be stored here. Otherwise, None.
    
    get_file_entries_for_granule_in_job_sql() -> <function text at 0x1092ed830>
    
    get_job_entry_for_granule(granule_id: str, job_id: str, engine: sqlalchemy.future.engine.Engine) -> Union[Dict[str, Any], NoneType]
        Gets the recovery_file status entries for the associated granule_id.
        If async_operation_id is non-None, then it will be used to filter results.
        Otherwise, only the item with the most recent request_time will be returned.
        
        Args:
            granule_id: The unique ID of the granule to retrieve status for.
            job_id: An optional additional filter to get a specific job's entry.
            engine: The sqlalchemy engine to use for contacting the database.
        Returns: A Dict with the following keys:
            'granule_id' (str): The unique ID of the granule to retrieve status for.
            'job_id' (str): The unique ID of the asyncOperation.
            'request_time' (int): The time, in milliseconds since 1 January 1970 UTC,
                when the request to restore the granule was initiated.
            'completion_time' (int, Null): The time, in milliseconds since 1 January 1970 UTC,
                when all granule_files were no longer 'pending'/'staged'.
    
    get_job_entry_for_granule_sql() -> <function text at 0x1092ed830>
    
    get_most_recent_job_id_for_granule(granule_id: str, engine: sqlalchemy.future.engine.Engine) -> Union[str, NoneType]
        Gets the job_id for the most recent job that restores the given granule.
        
        Args:
            granule_id: The unique ID of the granule.
            engine: The sqlalchemy engine to use for contacting the database.
        
        Returns: The job_id for the given granule's restore job.
    
    get_most_recent_job_id_for_granule_sql() -> <function text at 0x1092ed830>
    
    handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]
        Entry point for the request_status_for_granule Lambda.
        Args:
            event: A dict with the following keys:
                granule_id: The unique ID of the granule to retrieve status for.
                asyncOperationId (Optional): The unique ID of the asyncOperation.
                    May apply to a request that covers multiple granules.
            context: An object provided by AWS Lambda. Used for context tracking.
        
        Environment Vars: See shared_db.py's get_configuration for further details.
        
        Returns: A Dict with the following keys:
            'granule_id' (str): The unique ID of the granule to retrieve status for.
            'asyncOperationId' (str): The unique ID of the asyncOperation.
            'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
                'file_name' (str): The name and extension of the file.
                'restore_destination' (str): The name of the glacier bucket the file is being copied to.
                'status' (str): The status of the restoration of the file.
                    May be 'pending', 'staged', 'success', or 'failed'.
                'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
            'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
            'completion_time' (DateTime, Optional):
                The time, in UTC isoformat, when all granule_files were no longer 'pending'/'staged'.
        
            Or, if an error occurs, see create_http_error_dict
                400 if granule_id is missing. 500 if an error occurs when querying the database, 404 if not found.
    
    task(granule_id: str, db_connect_info: Dict, request_id: str, job_id: str = None) -> Dict[str, Any]
        Args:
            granule_id: The unique ID of the granule to retrieve status for.
            db_connect_info: The {database}.py defined db_connect_info.
            request_id: An ID provided by AWS Lambda. Used for context tracking.
            job_id: An optional additional filter to get a specific job's entry.
        Returns: See output.json
        
            Will also return a dict from create_http_error_dict with error NOT_FOUND if job/granule could not be found.

DATA
    Any = typing.Any
    Dict = typing.Dict
    INPUT_GRANULE_ID_KEY = 'granuleId'
    INPUT_JOB_ID_KEY = 'asyncOperationId'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    OUTPUT_COMPLETION_TIME_KEY = 'completionTime'
    OUTPUT_ERROR_MESSAGE_KEY = 'errorMessage'
    OUTPUT_FILENAME_KEY = 'fileName'
    OUTPUT_FILES_KEY = 'files'
    OUTPUT_GRANULE_ID_KEY = 'granuleId'
    OUTPUT_JOB_ID_KEY = 'asyncOperationId'
    OUTPUT_REQUEST_TIME_KEY = 'requestTime'
    OUTPUT_RESTORE_DESTINATION_KEY = 'restoreDestination'
    OUTPUT_STATUS_KEY = 'status'
    Union = typing.Union
```