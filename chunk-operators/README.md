# Custom Chunk Operators

Add custom chunk operator XML files to this directory (requires pbsmrtpipe >= 0.43.2)

See [Chunking Docs for more details](http://pbsmrtpipe.readthedocs.io/en/latest/chunking.html)

See [More Examples](https://github.com/PacificBiosciences/pbsmrtpipe/tree/master/pbsmrtpipe/chunk_operators)

Use `pbsmrtpipe show-chunk-operators` to get a summary of the chunk operators loaded from pbsmrtpipe.


## Example
 
See [testkit-job within pbsmrtpipe](https://github.com/PacificBiosciences/pbsmrtpipe/tree/master/testkit-data/dev_local_fasta_chunk) for an example that is runnable from `pbtestkit-runner`

```xml
<?xml version="1.0" encoding="utf-8" ?>
<chunk-operator id="pbsmrtpipe.operators.chunk_dev_filter_fasta">

    <task-id>pbsmrtpipe.tasks.dev_filter_fasta</task-id>

    <scatter>
        <scatter-task-id>pbcoretools.tasks.dev_scatter_filter_fasta</scatter-task-id>
        <chunks>
            <chunk out="$chunk.fasta_id" in="pbsmrtpipe.tasks.dev_filter_fasta:0"/>
        </chunks>
    </scatter>
    <!-- Define the Gather Mechanism -->
    <gather>
        <chunks>
            <chunk>
                <!-- This is actually a txt -->
                <gather-task-id>pbcoretools.tasks.gather_fasta</gather-task-id>
                <chunk-key>$chunk.filtered_fasta_id</chunk-key>
                <task-output>pbsmrtpipe.tasks.dev_filter_fasta:0</task-output>
            </chunk>
        </chunks>
    </gather>
</chunk-operator>
```
