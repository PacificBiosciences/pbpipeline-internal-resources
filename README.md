# pbpipeline-internal-resources

Internal Pipeline resources used by smrtflow and pbsmrtpipe


Add custom tool contracts:

```
export PB_TOOL_CONTRACT_DIR=$(pwd)/tool-contracts
```


Add custom pipelines:

```
export PB_PIPELINE_TEMPLATE_DIR=$(pwd)/resolved-pipeline-templates
```

Or 

```
source setup-env.sh
```

## Emit Pipelines

```
make emit-pipelines
```


## Run Tests


Sanity and validity test of pipeline

```
make test-sanity
```

## Run Testkit jobs 

Integration tests for pipelines

```
make run-teskit
```
