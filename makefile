PROJ_DIR := $(abspath $(lastword $(MAKEFILE_LIST)))


emit-pa-pipelines:
	python custom_pa_pipelines.py --log-level=INFO resolved-pipeline-templates

emit-custom-pipelines:
	python custom_pipelines.py --log-level=INFO resolved-pipeline-templates

emit-pipelines: emit-pa-pipelines emit-custom-pipelines

show-pipelines:
	pbsmrtpipe show-templates | grep internal


emit-tool-contracts:
	# this is missing mh_toy.py
	python -m pbinternal2.analysis_tools emit-tool-contracts -o tool-contracts
	python -m pbinternal2.pa_tasks emit-tool-contracts -o tool-contracts

test-dev:
	cd testkit-data && pbtestkit-multirunner --debug --nworkers 8 testkit.fofn

run-testkit: test-dev

test-pipelines:
	python -c "import pbsmrtpipe.loader as L; L.load_all()"

test-loader:
	python -c "import pbsmrtpipe.loader as L; L.load_all()"

test-contracts:
	python -c "import pbsmrtpipe.loader as L; L.load_all()"

test-chunk-operators:
	python -c "import pbsmrtpipe.loader as L; L.load_and_validate_chunk_operators()"

test-sanity: test-contracts test-pipelines test-chunk-operators test-loader 

clean:
	find . -name "*.pyc" | xargs rm -rf
	find . -name "job_output" | xargs rm -rf
	find . -name "0.std*" -delete

