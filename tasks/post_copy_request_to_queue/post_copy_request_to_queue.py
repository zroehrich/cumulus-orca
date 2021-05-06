"""
Name: post_copy_request_to_queue.py
Description:  lambda function that queries the db for file metadata, updates the status
of recovered file to staged, and sends the staged file info to staged_recovery queue for further processing.

"""
from enum import Enum
import json
import os
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from shared_recovery import (
    OrcaStatus,
    RequestMethod,
    post_status_for_file_to_queue,
    post_status_for_job_to_queue,
)
from requests_db import get_dbconnect_info
from database import single_query, result_to_json
from requests_db import DatabaseError
from cumulus_logger import CumulusLogger

# instantiate CumulusLogger
LOGGER = CumulusLogger()

def task(records, db_queue_url, recovery_queue_url):
    """
    Task called by the handler to perform the work.

    This task queries all entries from orca_recoverfile table
    that match the given filename and whose status_id is 'PENDING'.
    The result is then sent to the staged-recovery-queue SQS and status-update-queue SQS.

    Args:
        records: A dictionary passed through from the handler.
        db_queue_url: The SQS URL of status_update_queue
        recovery_queue_url: The SQS URL of staged_recovery_queue
    """

    # grab the filename from event
    for record in records:
        filename = record["s3"]["object"]["key"]

    sql = """
        SELECT
            job_id, granule_id, restore_destination
        FROM
            orca_recoverfile
        WHERE
            filename = %s
        AND
            status_id = %d
    """
    # Gets the dbconnection info.

    db_connect_info = get_dbconnect_info()

    try:
        rows = single_query(sql, db_connect_info, (filename, OrcaStatus.PENDING.value))
    except Exception as ex:
        LOGGER.error(ex)

    if len(rows) == 0:
        LOGGER.fatal("DB tables cannot be empty")
        raise Exception(
            "No metadata found for {filename}"
        )
    # convert db result to json
    try:
        db_result_json = result_to_json(rows)
    except Exception as e:


    # grab the parameters from the db in json format
    job_id = db_result_json["job_id"]
    granule_id = db_result_json["granule_id"]
    restore_destination = db_result_json["restore_destination"]

    # post to staged-recovery-queue
    post_status_for_file_to_queue(
        job_id,
        granule_id,
        filename,
        restore_destination,
        OrcaStatus.STAGED.value,
        None,
        RequestMethod.NEW.value,
        RECOVERY_QUEUE_URL,
    )

    # post to DB-queue
    post_status_for_file_to_queue(
        job_id,
        granule_id,
        filename,
        restore_destination,
        OrcaStatus.STAGED.value,
        None,
        RequestMethod.UPDATE.value,
        DB_QUEUE_URL,
    )

def handler(event, context):
    """
    Lambda handler. This lambda calls the task function to perform db queries
    and send message to SQS.

        Environment Vars:
            PREFIX (string): the prefix
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
            DB_QUEUE_URL (string): the SQS URL for status-update-queue
            RECOVERY_QUEUE_URL (string): the SQS URL for staged_recovery_queue
        Parameter store:
            {prefix}-drdb-host (string): host name that will be retrieved from secrets manager
            {prefix}-drdb-user-pass (string):db password that will be retrieved from secrets manager
    Args:
        event:
            A dictionary from the S3 bucket. See schemas/input.json for more information.
        context: An object required by AWS Lambda. Unused.
    Raises:
        None

    """
    LOGGER.setMetadata(event, context)
    # retrieving db_queue_url from env variable
    db_queue_url = os.environ["DB_QUEUE_URL"]
    if len(db_queue_url) == 0 or db_queue_url is None:
        LOGGER.error("db_queue_url cannot be None or empty")
        raise Exception("db_queue_url cannot be None or empty")
    # retrieving recovery_queue_url from env variable
    recovery_queue_url = os.environ["RECOVERY_QUEUE_URL"]
    if len(recovery_queue_url) == 0 or recovery_queue_url is None:
        LOGGER.error("recovery_queue_url cannot be None or empty")
        raise Exception("recovery_queue_url cannot be None or empty")

    records = event["Records"]
    # calling the task function to perform the work
    task(records, db_queue_url, recovery_queue_url)
