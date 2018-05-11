wget 'http://www.rarlab.com/rar/unrarsrc-5.1.6.tar.gz'
tar -xvzf unrarsrc-5.1.6.tar.gz
cd unrar
wget 'http://simon.aldrich.eu/download/unrar/unrar-deleteOnExtract.patch'
patch -p1 < unrar-deleteOnExtract.patch
make

