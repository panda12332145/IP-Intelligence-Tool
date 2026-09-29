"""Coleta de dados sobre um IP: tipo, latência, MAC, VPN/DNS, RDAP."""
import ipaddress
import platform
import subprocess
import time

import requests
from ipwhois import IPWhois

DNS_ASNS = {15169, 13335, 14992}  # Google, Cloudflare, OpenDNS


def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except ValueError:
        return False


def identify_ip_type(ip: str) -> tuple:
    """Retorna (tipo: Público/Privado/Inválido, protocolo: IPv4/IPv6)."""
    try:
        ip_obj = ipaddress.ip_address(ip.strip())
        kind = "Privado" if ip_obj.is_private else "Público"
    except ValueError:
        kind = "Inválido"
    proto = "IPv6" if ":" in ip else "IPv4"
    return kind, proto


def get_latency(ip: str):
    """Mede a latência via ping. Sem shell=True (anti-injeção): a lista de
    argumentos só passa depois de validado por ipaddress."""
    if not is_valid_ip(ip):
        return None
    flag = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = ["ping", flag, "1", ip.strip()]
    try:
        start = time.time()
        subprocess.run(cmd, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=10, check=True)
        return round((time.time() - start) * 1000)
    except Exception:
        return None


def get_mac_address(ip: str):
    """Obtém o MAC via ARP (só funciona na rede local)."""
    if not is_valid_ip(ip):
        return None
    ip = ip.strip()
    if platform.system().lower() == "windows":
        cmd = ["arp", "-a", ip]
    else:
        cmd = ["arp", "-n", ip]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL,
                                      timeout=10).decode(errors="replace")
        for line in out.splitlines():
            if ip in line:
                return line.split()[-1]
    except Exception:
        return None
    return None


def fetch_ipwho(ip: str):
    """Consulta a API ipwho.is (HTTPS) para informações do IP."""
    try:
        r = requests.get(f"https://ipwho.is/{ip.strip()}?lang=pt-BR", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def fetch_rdap(ip: str):
    """Consulta dados RDAP/WHOIS via ipwhois."""
    try:
        return IPWhois(ip.strip()).lookup_rdap()
    except Exception:
        return None


def _asn_int(value):
    """Normaliza o ASN para int (a API devolve '13335' como string)."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def detect_vpn_dns(ip: str) -> str:
    """Detecta VPN ou DNS público via ASN (ipwho.is com fallback RDAP)."""
    info = fetch_ipwho(ip)
    if info:
        if _asn_int(info.get("asn")) in DNS_ASNS:
            return "DNS público"
        blob = f"{info.get('org', '')} {info.get('isp', '')}".lower()
        if "vpn" in blob:
            return "VPN detectada"

    rdap = fetch_rdap(ip)  # fallback (paridade com o script original)
    if rdap:
        if _asn_int(rdap.get("asn")) in DNS_ASNS:
            return "DNS público"
        if "vpn" in str(rdap).lower():
            return "VPN detectada"
    return "Não identificado como VPN/DNS"
