FROM kalilinux/kali-rolling:latest

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 \
        git \
        nmap \
        whois \
        subfinder \
        dnsenum \
        sqlmap \
        metasploit-framework \
        nikto \
        nuclei \
        gobuster \
        wfuzz \
        jq \
        curl \
        whatweb \
        wpscan \
        hydra \
        gvm-tools \
        openvas-scanner \
        amass \
        theharvester \
        python3-shodan && \
    git clone https://github.com/drwetter/testssl.sh.git /opt/testssl.sh && \
    ln -s /opt/testssl.sh/testssl.sh /usr/local/bin/testssl.sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/toolbox

