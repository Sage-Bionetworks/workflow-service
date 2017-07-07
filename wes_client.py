#!/usr/bin/env python

from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
import json
import time
import pprint
import sys
import os
import argparse
import logging

def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser(description='Workflow Execution Service')
    parser.add_argument("--host", type=str, default=os.environ.get("WES_API_HOST"))
    parser.add_argument("--auth", type=str, default=os.environ.get("WES_API_TOKEN"))
    parser.add_argument("--proto", type=str, default="https")
    parser.add_argument("--quiet", action="store_true", default=False)

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument("--run", action="store_true", default=False)
    exgroup.add_argument("--get", type=str, default=None)
    exgroup.add_argument("--list", action="store_true", default=False)

    parser.add_argument("workflow_url", type=str, nargs="?", default=None)
    parser.add_argument("job_order", type=str, nargs="?", default=None)
    args = parser.parse_args(argv)

    http_client = RequestsClient()
    http_client.set_api_key(
        args.host, args.auth,
        param_name='Authorization', param_in='header')
    client = SwaggerClient.from_url("%s://%s/swagger.json" % (args.proto, args.host),
                                    http_client=http_client, config={'use_models': False})

    if args.list:
        l = client.WorkflowExecutionService.ListWorkflows()
        json.dump(l.result(), sys.stdout, indent=4)
        return 0

    if args.get:
        l = client.WorkflowExecutionService.GetWorkflowLog(workflow_id=args.get)
        json.dump(l.result(), sys.stdout, indent=4)
        return 0

    with open(args.job_order) as f:
        input = json.load(f)

    workflow_url = args.workflow_url
    if not workflow_url.startswith("/") or ":" in workflow_url:
        workflow_url = os.path.abspath(workflow_url)

    if args.quiet:
        logging.basicConfig(level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.INFO)

    r = client.WorkflowExecutionService.RunWorkflow(body={
        "workflow_url": workflow_url,
        "workflow_params": input,
        "workflow_type": "CWL",
        "workflow_type_version": "v1.0"}).result()

    logging.info("Workflow id is %s", r["workflow_id"])

    r = client.WorkflowExecutionService.GetWorkflowStatus(workflow_id=r["workflow_id"]).result()
    while r["state"] == "Running":
        time.sleep(1)
        r = client.WorkflowExecutionService.GetWorkflowStatus(workflow_id=r["workflow_id"]).result()

    logging.info("State is %s", r["state"])

    s = client.WorkflowExecutionService.GetWorkflowLog(workflow_id=r["workflow_id"]).result()
    logging.info(s["workflow_log"]["stderr"])

    json.dump(s["outputs"], sys.stdout, indent=4)

    if r["state"] == "Complete":
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
