
ifeq "openssl-enabled" "openssl-enabled"

HTSLIB_LIBS += `pkg-config openssl --libs`

endif

