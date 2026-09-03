FROM almalinux/8-minimal

ARG MPDECIMAL_VERSION=4.0.1
ARG OPENSSL_VERSION=3.5.8
ARG SQLITE_VERSION=sqlite-autoconf-3530400
ARG ZSTD_VERSION=1.5.7

ENV PIP_ROOT_USER_ACTION=ignore
ENV PATH="/opt/rh/gcc-toolset-14/root/usr/bin:${PATH}"

RUN microdnf -y upgrade && microdnf -y install gcc-toolset-14-gcc gcc-toolset-14-gcc-c++ tar findutils perl-IPC-Cmd perl-Time-Piece zlib-devel xz-devel lz4-devel xz git pkg-config bzip2-devel ncurses-devel readline-devel gdbm-devel libuuid-devel libffi-devel

# Upgrade openssl
RUN curl -LO https://github.com/openssl/openssl/releases/download/openssl-$OPENSSL_VERSION/openssl-$OPENSSL_VERSION.tar.gz && \
    tar -xf openssl-$OPENSSL_VERSION.tar.gz && \
    cd openssl-$OPENSSL_VERSION && \
    linux32 ./Configure --prefix=/usr/local --openssldir=/etc/pki/tls shared zlib && \
    make -j$(nproc) && \
    make install_sw && \
    cd .. && \
    rm -rf openssl*

# Upgrade zstd
RUN curl -LO https://github.com/facebook/zstd/releases/download/v$ZSTD_VERSION/zstd-$ZSTD_VERSION.tar.gz && \
    tar -xf zstd-$ZSTD_VERSION.tar.gz && \
    cd zstd-$ZSTD_VERSION && \
    make -j$(nproc) prefix=/usr/local && \
    make prefix=/usr/local install && \
    cd .. && \
    rm -rf zstd*

# Upgrade mpdecimal
RUN curl -LO https://www.bytereef.org/software/mpdecimal/releases/mpdecimal-$MPDECIMAL_VERSION.tar.gz && \
    tar -xf mpdecimal-$MPDECIMAL_VERSION.tar.gz && \
    cd mpdecimal-$MPDECIMAL_VERSION && \
    ./configure --disable-doc && \
    make -j$(nproc) prefix=/usr/local && \
    make prefix=/usr/local install && \
    cd .. && \
    rm -rf mpdecimal*

# Upgrade SQLite
RUN curl -LO https://www.sqlite.org/2026/$SQLITE_VERSION.tar.gz && \
    tar -xf $SQLITE_VERSION.tar.gz && \
    cd $SQLITE_VERSION && \
    ./configure --prefix=/usr/local --enable-all && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    rm -rf sqlite*

COPY --chmod=0755 install-python.sh .
COPY --chmod=0755 freeze-server32.sh .

CMD ["linux32", "bash"]
