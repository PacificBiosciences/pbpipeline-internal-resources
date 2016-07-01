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

This might require tasks that depend on pbinternal2, pbcommandR, internal tools repo (private).

- [pbinternal2](https://github.com/PacificBiosciences/pbinternal2) (python)
- [pbcommandR](https://github.com/PacificBiosciences/pbcommandR) (R)
- (Private) [internaltools](https://github.com/PacificBiosciences/internaltools) (R) 

