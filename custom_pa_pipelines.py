
import logging
import os.path as op
import os
import sys

# FIXME. This is going to be a problem.
# There's friction on reusing the `custom_pipelines.py` from other pbpipeline-*-resources
from pbsmrtpipe.pb_pipelines.pb_pipelines_sa3 import (
    Constants as BaseConstants,
    Tags,
    RESEQUENCING_TASK_OPTIONS,
    SAT_TASK_OPTIONS,
    to_entry,
    _core_align_plus,
    _core_gc_plus,
    _core_sat)


from pbsmrtpipe.core import PipelineRegistry
from pbsmrtpipe.cli_custom_pipeline import registry_runner_main


log = logging.getLogger(__name__)


class Constants(BaseConstants):
    PT_NAMESPACE = "pbpipelines_internal"
    
    ENTRY_TRC = to_entry("pa_trc")
    ENTRY_BAZ = to_entry("pa_baz")
    ENTRY_ADAPTER_FA = to_entry("adapter_fa")
    ENTRY_METADATA = to_entry("metadata")

registry = PipelineRegistry(Constants.PT_NAMESPACE)


def pa_register(relative_id, display_name, version, tags=(), task_options=None):
    tags = list(tags) + ["primary", Tags.DEV, Tags.INTERNAL]
    return registry(relative_id, display_name, version, tags=tags,
                    task_options=task_options)


def _core_baz2bam(baz_file):
    return [(baz_file, "pbinternal2.tasks.baz2bam:0"),
            (Constants.ENTRY_ADAPTER_FA, "pbinternal2.tasks.baz2bam:1"),
            (Constants.ENTRY_METADATA, "pbinternal2.tasks.baz2bam:2")]


@pa_register("baz2bam", "Basecalls H5 (.baz) to Subread DataSet", "0.1.0",
             tags=(Tags.CONVERTER,))
def basecalls_to_subreads():
    """
    Convert basecalls in .baz format to a SubreadSet.
    """
    return _core_baz2bam(Constants.ENTRY_BAZ)


def trace_to_subreads():
    """
    Convert a trace file (.trc) to a SubreadSet.
    """
    pass


def _core_baz_to_resequencing(baz_file):
    b1 = _core_baz2bam(baz_file)
    b2 = _core_align_plus("pbinternal2.tasks.baz2bam:0", Constants.ENTRY_DS_REF)
    b3 = _core_gc_plus("pbalign.tasks.pbalign:0", Constants.ENTRY_DS_REF)
    return b1 + b2 + b3


@pa_register("baz2aln", "Basecalls H5 (.baz) to AlignmentSet", "0.1.0",
             tags=(Tags.MAP, Tags.CONSENSUS),
             task_options=RESEQUENCING_TASK_OPTIONS)
def basecalls_to_resequencing():
    """
    Run the resequencing pipeline starting from a .baz file.
    """
    return _core_baz_to_resequencing(Constants.ENTRY_BAZ)


@pa_register("baz2sat", "Basecalls H5 (.baz) to Site Acceptance Test", "0.1.0",
             tags=(Tags.MAP, Tags.CONSENSUS, Tags.RPT, Tags.SAT),
             task_options=SAT_TASK_OPTIONS)
def basecalls_to_site_acceptance_test():
    """
    Run the SAT resequencing pipeline starting from a .baz file.
    """
    return _core_sat("pbpipelines_internal.pipelines.baz2aln")


@pa_register("trc2aln", "Trace to AlignmentSet", "0.1.0",
             tags=(Tags.MAP, Tags.CONSENSUS),
             task_options=RESEQUENCING_TASK_OPTIONS)
def trace_to_resequencing():
    """
    Run the resequencing pipeline starting from a .baz file.
    """
    b1 = [(Constants.ENTRY_TRC, "pbinternal2.tasks.basecaller:0")]
    b2 = _core_baz_to_resequencing("pbinternal2.tasks.basecaller:0")
    return b1 + b2


@pa_register("trc2sat", "Trace to Site Acceptance Test", "0.1.0",
             tags=(Tags.MAP, Tags.CONSENSUS, Tags.RPT, Tags.SAT),
             task_options=SAT_TASK_OPTIONS)
def trace_to_site_acceptance_test():
    """
    Run basecalling and the SAT resequencing pipeline starting from a .trc file.
    """
    return _core_sat("pbpipelines_internal.pipelines.trc2aln")


# XXX this doesn't exist in SA3 but we need it for 'bax2sat'
@pa_register("sa3_resequencing_fat", "RS movie Resequencing + Reports", "0.1.0",
             tags=(Tags.MAP, Tags.CONSENSUS, Tags.RPT),
             task_options=RESEQUENCING_TASK_OPTIONS)
def sa3_resequencing_fat():
    b1 = [(Constants.ENTRY_DS_HDF, "pbcoretools.tasks.h5_subreads_to_subread:0")]
    b2 = _core_align_plus("pbcoretools.tasks.h5_subreads_to_subread:0",
                          Constants.ENTRY_DS_REF)
    b3 = _core_gc_plus("pbalign.tasks.pbalign:0", Constants.ENTRY_DS_REF)
    return b1 + b2 + b3


@pa_register("bax2sat", "bax.h5 to Site Acceptance Test", "0.1.0",
             tags=(Tags.MAP, Tags.CONSENSUS, Tags.RPT, Tags.SAT),
             task_options=SAT_TASK_OPTIONS)
def bax_to_site_acceptance_test():
    return _core_sat("pbpipelines_internal.pipelines.sa3_resequencing_fat")


def _core_bam2bam(subread_ds):
    return [(subread_ds, "pbinternal2.tasks.bam2bam:0")]


def _core_unrolled_alignment(bam_reads):
    return [
        (bam_reads, "pbinternal2.tasks.pbalign_unrolled:0"),
        (Constants.ENTRY_DS_REF, "pbinternal2.tasks.pbalign_unrolled:1"),
        ("pbinternal2.tasks.pbalign_unrolled:0", "pbreports.tasks.mapping_stats:0")
    ]


@pa_register("bax2aln_unrolled",
             "Unrolled alignment from HdfSubreadSet", "0.1.0",
             tags=(Tags.MAP, Tags.RPT),
             task_options={})
def bax_to_unrolled_alignment():
    # XXX bax2bam doesn't produce a SubreadSet containing both subreads and
    # scraps BAMs suitable for bam2bam, but we can convert directly to
    # polymerase reads instead
    b1 = [(Constants.ENTRY_DS_HDF, "pbinternal2.tasks.bax2bam_polymerase:0")]
    b2 = _core_unrolled_alignment("pbinternal2.tasks.bax2bam_polymerase:0")
    return b1 + b2


@pa_register("bam2aln_unrolled", "Unrolled alignment from SubreadSet", "0.1.0",
             tags=(Tags.MAP, Tags.RPT),
             task_options={})
def bam_to_unrolled_alignment():
    b1 = _core_bam2bam(Constants.ENTRY_DS_SUBREAD)
    b2 = _core_unrolled_alignment("pbinternal2.tasks.bam2bam:0")
    return b1 + b2


@pa_register("baz2aln_unrolled", "Unrolled alignment from .baz", "0.1.0",
             tags=(Tags.MAP, Tags.RPT),
             task_options={})
def baz_to_unrolled_alignment():
    b1 = _core_baz2bam(Constants.ENTRY_BAZ)
    b2 = _core_bam2bam("pbinternal2.tasks.baz2bam:0")
    b3 = _core_unrolled_alignment("pbinternal2.tasks.bam2bam:0")
    return b1 + b2 + b3


@pa_register("trc2aln_unrolled", "Unrolled alignment from .trc", "0.1.0",
             tags=(Tags.MAP, Tags.RPT),
             task_options={})
def trc_to_unrolled_alignment():
    b1 = [(Constants.ENTRY_TRC, "pbinternal2.tasks.basecaller:0")]
    b2 = _core_baz2bam("pbinternal2.tasks.basecaller:0")
    b3 = _core_bam2bam("pbinternal2.tasks.baz2bam:0")
    b4 = _core_unrolled_alignment("pbinternal2.tasks.bam2bam:0")
    return b1 + b2 + b3 + b4


if __name__ == '__main__':
    sys.exit(registry_runner_main(registry)(argv=sys.argv))
