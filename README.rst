=====
Pysam with reading encrypted BGZF files functionality
=====

.. image:: https://circleci.com/gh/Munchic/pysam/tree/feature%2Fconnect-crypto-htslib.svg?style=shield
    :target: https://circleci.com/gh/Munchic/pysam/tree/feature%2Fconnect-crypto-htslib

|build-status| |docs|

Pysam is a python module for reading and manipulating files in the
SAM/BAM format. The SAM/BAM format is a way to store efficiently large
numbers of alignments (`Li 2009`_), such as those routinely created by
next-generation sequencing methods.

Pysam is a lightweight wrapper of the samtools_ C-API. Pysam also
includes an interface for tabix_.

Installation::

   $ git clone --branch=feature/connect-crypto-htslib https://github.com/Munchic/pysam/
   $ cd pysam
   $ python setup.py install --user

Usage (adapted from https://samtools.github.io/bcftools/bgzf-aes-encryption.pdf):: 
   
   # Generate a random private key and its hash (digest)
   $ KEY=`dd if=/dev/urandom bs=1 count=32 2>/dev/null | xxd -ps -c32`
   $ HASH=`echo $KEY | openssl sha256 | cut -f2 -d ' '`
   $ echo -e "$HASH\t$KEY" > hts-keys.txt
   
   # Configure environment variables, compress + encrypt, and index with built-in crypto htslib
   $ export HTS_KEYS=hts-keys.txt
   $ HTS_ENC=${PRIVATE_KEY} htslib/bgzip -c in.vcf > enc.vcf.gz
   $ HTS_ENC=${PRIVATE_KEY} htslib/tabix enc.vcf.gz
   
   # Read encrypted tabix-indexed file in Python with Pysam
   import pysam
   file = pysam.TabixFile("enc.vcf.gz")
   for read in file.fetch('chr1'):
       print(read)

The latest version is available through `pypi
<https://pypi.python.org/pypi/pysam>`_. To install, simply type::

   pip install pysam

If you are using the conda packaging manager (e.g. miniconda or anaconda),
you can install pysam from the `bioconda channel <https://bioconda.github.io/>`_:

   conda config --add channels r

   conda config --add channels bioconda

   conda install pysam


Pysam documentation is available through https://readthedocs.org/ from
`here <http://pysam.readthedocs.org/en/latest/>`_

Questions and comments are very welcome and should be sent to the
`pysam user group <http://groups.google.com/group/pysam-user-group>`_

.. _samtools: http://samtools.sourceforge.net/
.. _tabix: http://samtools.sourceforge.net/tabix.shtml
.. _Li 2009: http://www.ncbi.nlm.nih.gov/pubmed/19505943

.. |build-status| image:: https://travis-ci.org/pysam-developers/pysam.svg
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.org/pysam-developers/pysam

.. |docs| image:: https://readthedocs.org/projects/pysam/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://pysam.readthedocs.org/en/latest/?badge=latest
