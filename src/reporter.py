"""Relatório de análise de um IP."""
import json

from .geomap import map_from_ipwho
from .ip_analyzer import (
    detect_vpn_dns,
    fetch_ipwho,
    fetch_rdap,
    get_latency,
    get_mac_address,
    identify_ip_type,
    is_valid_ip,
)


def print_section(title: str):
    print(f"\n{'─' * 40}\n  {title}\n{'─' * 40}")


def display_dict(data, label: str = "API"):
    if not data:
        print(f"  ⚠️ Sem dados de {label}")
        return
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"  {k.upper()}:\n{json.dumps(v, indent=4, ensure_ascii=False)}")
        elif isinstance(v, list):
            print(f"  {k.upper()}: {', '.join(str(i) for i in v[:5])}")
        else:
            print(f"  {k.upper()}: {v}")


def run_analysis(ip: str, make_map: bool = False, map_out: str = "mapa_ip.html"):
    ip = ip.strip()
    print(f"\n🔍 Analisando: {ip}")

    if not is_valid_ip(ip):
        print("  ❌ IP inválido — informe um IPv4 ou IPv6 válido (ex.: 1.1.1.1)")
        return False

    kind, proto = identify_ip_type(ip)
    print(f"  Tipo: {kind} | Protocolo: {proto}")

    latency = get_latency(ip)
    print(f"  Latência: {latency} ms" if latency is not None
          else "  Latência: Indisponível")

    mac = get_mac_address(ip)
    print(f"  MAC: {mac}" if mac else
          "  MAC: Não disponível (fora da rede local)")

    print_section("🛰️ Detecção VPN/DNS")
    print(f"  {detect_vpn_dns(ip)}")

    print_section("📡 Dados via ipwho.is")
    info = fetch_ipwho(ip)
    display_dict(info, "ipwho.is")

    if info and "latitude" in info:
        lat, lon = info["latitude"], info["longitude"]
        print(f"\n🗺️  Mapa: https://www.google.com/maps?q={lat},{lon}")

    print_section("📚 Dados via RDAP")
    display_dict(fetch_rdap(ip), "RDAP")

    if make_map:
        out = map_from_ipwho(info, map_out) if info else None
        if out:
            print(f"\n🗺️  Mapa HTML gerado: {out}")
        else:
            print("\n⚠️ Sem coordenadas para gerar o mapa.")

    return True


if __name__ == "__main__":
    from .main import cli
    cli()
