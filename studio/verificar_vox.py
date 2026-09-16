"""verificar_vox.py — confere se o pipeline do repositório tem tudo que a
variante Vox usa, ANTES de gastar minutos de render. Rode na pasta do
pablo_episodio.py:  python verificar_vox.py"""
import inspect, os, sys
sys.path.insert(0, os.getcwd())
erros = []
try:
    import pablo_audio as pa, pablo_montador as pm, pablo_cine as cine
    import pablo_cenarios as cen, pablo_ambientes as amb, pablo_fx as fx
    from pablo_guru_v2 import PabloGuru, Perguntadora, PALETA
except Exception as e:
    sys.exit(f"FALHA ao importar os módulos do Pablo Guru: {e}")
for mod, nomes in ((pa, ["narrar", "lip_sync", "trilha_ambiente"]),
                   (pm, ["extrair_frame", "gerar_capa", "gerar_metadados"]),
                   (cine, ["motor", "respirar", "lip_sync_absoluto", "vida_facial",
                           "trilha_temporal", "spotlight", "vinheta", "batida", "overlay_cor"]),
                   (cen, ["dims", "montar"]), (amb, ["atelie", "cantinho", "animar"]),
                   (fx, ["poeira_dourada", "particulas_aceitacao"])):
    for n in nomes:
        if not hasattr(mod, n):
            erros.append(f"{mod.__name__}.{n} não existe")
if "db" not in inspect.signature(pa.trilha_ambiente).parameters:
    erros.append("pablo_audio.trilha_ambiente não aceita db=")
p = PabloGuru()
for a in ("tronco", "adereco", "cabeca", "olho_e", "olho_d", "repouso", "expressao"):
    if not hasattr(p, a):
        erros.append(f"PabloGuru.{a} não existe")
fonte = inspect.getsource(cine.vida_facial)
if "stretch(fator" in fonte:
    print("AVISO: vida_facial ainda usa piscada RELATIVA (bug do olho esbugalhado). "
          "Veja LEIA-ME_VOX.md, seção 'Olho absoluto'.")
if erros:
    print("INCOMPATÍVEL:"); [print(" -", e) for e in erros]; sys.exit(1)
print("OK — o pipeline tem tudo que a variante Vox usa.")
