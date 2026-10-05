"""Testes do IP-Intelligence-Tool."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ip_analyzer import identify_ip_type, is_valid_ip


def test_valid_and_invalid_ips():
    assert is_valid_ip("1.1.1.1")
    assert is_valid_ip("::1")
    assert not is_valid_ip("999.1.1.1")
    assert not is_valid_ip("banana")
    # injeção de comando deve ser rejeitada na validação
    assert not is_valid_ip("1.1.1.1; rm -rf /")
    assert not is_valid_ip("127.0.0.1 && curl evil")


def test_ip_type():
    assert identify_ip_type("192.168.0.10") == ("Privado", "IPv4")
    assert identify_ip_type("1.1.1.1") == ("Público", "IPv4")
    assert identify_ip_type("2001:4860:4860::8888")[0] == "Público"
    assert identify_ip_type("invalido")[0] == "Inválido"


def test_latency_rejects_invalid_without_shell():
    from src.ip_analyzer import get_latency, get_mac_address
    # sem shell=True: IP inválido nunca chega ao subprocesso
    assert get_latency("1.1.1.1; echo pwned") is None
    assert get_mac_address("$(whoami)") is None


def test_live_api_optional():
    """Smoke test ao vivo (pula se a rede estiver indisponível)."""
    from src.ip_analyzer import fetch_ipwho
    info = fetch_ipwho("1.1.1.1")
    if info is None:
        print("  (API indisponível — pulado)")
        return
    assert info.get("success", True) is not False
    assert "ip" in info


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"✅ {fn.__name__}")
    print(f"\n{len(fns)} testes passaram.")
