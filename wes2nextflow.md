### WES 2 Nextflow
This is proof of concept to run nextflow workflows through WES + nextflow tower. 

```
wes-server --backend=wes_service.nextflow_wes
export WES_API_HOST=localhost:8080
export WES_API_AUTH='Header: value'
export WES_API_PROTO=http

wes-client challenge_workflow.nf nextflow.config --attachments nextflow.config
```

Some issues:

* Nextflow configuration file is in groovy which modify_jsonyaml doesn't like
