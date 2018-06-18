import pysam

enc_file = pysam.TabixFile("crypto_read/enc_test.vcf.gz")
plain_file = pysam.TabixFile("crypto_read/test.vcf.gz")

enc_read = ""
plain_read = ""

for read in enc_file.fetch('chr1'):
    enc_read = read

for read in plain_file.fetch('chr1'):
    plain_read = read

if enc_read == plain_read:
    print("Successfully decrypted!")
