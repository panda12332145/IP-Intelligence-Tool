"""Ponto de entrada do IP-Intelligence-Tool.

Uso:
  python main.py                      # IP via prompt
  python main.py 1.1.1.1              # análise direta
  python main.py 8.8.8.8 --map        # gera mapa_ip.html
"""
import argparse

from .reporter import run_analysis


def cli(argv=None):
    p = argparse.ArgumentParser(
        description="IP Intelligence Tool — OSINT de IPs")
    p.add_argument("ip", nargs="?", help="IP alvo (IPv4/IPv6)")
    p.add_argument("--map", action="store_true",
                   help="gera mapa HTML (folium) da localização")
    p.add_argument("--out", default="mapa_ip.html",
                   help="arquivo de saída do mapa (padrão: mapa_ip.html)")
    args = p.parse_args(argv)

    ip = args.ip or input("IP para análise: ").strip()
    ok = run_analysis(ip, make_map=args.map, map_out=args.out)
    raise SystemExit(0 if ok else 1)


def main():
    cli()


if __name__ == "__main__":
    main()
