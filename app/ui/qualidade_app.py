import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.metabase_service import carregar_fechamento_metabase
from app.ui.auditoria_app import render_auditoria
from app.ui.components.navigation import botao_voltar_home

# ======================================================
# UNIDADES (AM / PA)
# ======================================================
UNIDADES = {
    "PA": [
        "Santarém", "Alenquer", "Marabá", "Prainha", "Monte Alegre",
        "Óbidos", "Oriximiná", "Belterra", "Mojuí dos Campos",
        "Itaituba", "Curuá", "Uruará", "Alter do Chão",
    ],
    "AM": [
        "Manaus", "Presidente Figueiredo", "Manacapuru",
        "Rio Preto da Eva", "Iranduba", "Parintins", "Itacoatiara",
    ],
}

# ======================================================
# CONSTANTES
# ======================================================
COL_TIPO = "tipo_ordem_servico"
COL_EXECUTOR = "executor_tipo"

# ======================================================
# GRUPOS DE OS
# ======================================================
GRUPO_INSTALACAO = [
    "INSTALAÇÃO (R$ 49,90)",
    "INSTALAÇÃO (R$ 100,00)",
    "INSTALAÇÃO GRÁTIS",
    "INSTALAÇÃO PJ",
]

GRUPO_MDE = [
    "MUDANÇA DE ENDEREÇO - R$ 100,00",
    "MUDANÇA DE ENDEREÇO - R$ 50,00",
    "MUDANÇA DE ENDEREÇO",
]

GRUPO_NAO_CONFORMIDADE = [
    "NAO_CONFORMIDADES",
    "AMZ QUALIDADE - NÃO CONFORMIDADES",
]

GRUPO_POS_VENDA = [
    "AMZ QUALIDADE - PÓS VENDA (INSTALAÇÃO)",
    "MANIA QUALIDADE - PÓS VENDA (INSTALAÇÃO)",
]

# ======================================================
# FUNÇÕES AUXILIARES
# ======================================================
def normalizar_cidade(valor: str) -> str:
    return valor.strip().title() if valor else ""


def mapear_estado(cidade: str) -> str:
    cidade = normalizar_cidade(cidade)
    for uf, cidades in UNIDADES.items():
        if cidade in map(str.title, cidades):
            return uf
    return "OUTROS"


def contar_por_grupo(df: pd.DataFrame, tipos: list[str]) -> int:
    if df.empty or COL_TIPO not in df.columns:
        return 0
    return df[df[COL_TIPO].isin(tipos)].shape[0]


def classificar_executor(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[COL_EXECUTOR] = "CAMPO"

    if "usuario_fechamento" in df.columns:

        df.loc[
            df["usuario_fechamento"].str.contains(
                r"TEC_TERC|TEC_LOBATOS|TEC_LL",
                case=False,
                na=False,
            ),
            COL_EXECUTOR,
        ] = "TERCEIRIZADOS"

    return df


def gerar_link_auditoria(row: pd.Series) -> str:
    codigo = row.get("id_cliente")
    conta = row.get("conta")

    if not codigo:
        return ""

    if conta == "amazonet":
        return f"https://amazonet.hubsoft.com.br/cliente/editar/{codigo}/servico"

    if conta == "mania":
        return f"https://mania.hubsoft.com.br/cliente/editar/{codigo}/servico"

    return ""


# ======================================================
# APP
# ======================================================
def render_qualidade():
    botao_voltar_home()
    st.title("📊 Análise de Qualidade")

    st.session_state.setdefault("df_os", pd.DataFrame())
    st.session_state.setdefault("carregado", False)


    # =========================
    # SIDEBAR
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filtros base")

        contas = st.multiselect(
            "Contas", ["mania", "amazonet"], default=["mania", "amazonet"]
        )

        hoje = date.today()
        data_inicio = st.date_input("Data início", hoje - timedelta(days=7))
        data_fim = st.date_input("Data fim", hoje)

        carregar = st.button("📥 Carregar ordens")

    # =========================
    # CARREGAMENTO
    # =========================
    if carregar:
        if not contas:
            st.warning("Selecione ao menos uma conta.")
            return

        registros: list[dict] = []

        with st.spinner("🔄 Carregando dados do Metabase..."):
            for conta in contas:
                df = carregar_fechamento_metabase(conta, data_inicio, data_fim)
                if df is None or df.empty:
                    continue

                for row in df.to_dict("records"):
                    row["conta"] = conta
                    registros.append(row)

        if not registros:
            st.warning("Nenhuma ordem encontrada.")
            return

        df_base = pd.json_normalize(registros)

        df_base["id_cliente"] = (
            df_base["id_cliente"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Normalizações
        df_base["cidade"] = df_base["cidade"].apply(normalizar_cidade)
        df_base["estado"] = df_base["cidade"].apply(mapear_estado)
        df_base["link_auditoria"] = df_base.apply(gerar_link_auditoria, axis=1)


        df_base = classificar_executor(df_base)

        st.session_state["df_os"] = df_base
        st.session_state["carregado"] = True

    if not st.session_state["carregado"]:
        return

    df_base = st.session_state["df_os"]

    # =========================
    # FILTROS
    # =========================
    st.subheader("🎯 Filtros de Qualidade")
    c1, c2, c3 = st.columns(3)

    with c1:
        exec_sel = st.multiselect(
            "Executor", ["CAMPO", "TERCEIRIZADOS"], default=["CAMPO", "TERCEIRIZADOS"]
        )
        df_base = df_base[df_base[COL_EXECUTOR].isin(exec_sel)]

    with c2:
        tipo_sel = st.multiselect(
            "Tipo OS", sorted(df_base[COL_TIPO].dropna().unique())
        )
        if tipo_sel:
            df_base = df_base[df_base[COL_TIPO].isin(tipo_sel)]

    with c3:
        estado_sel = st.multiselect(
            "Estado", sorted(df_base["estado"].dropna().unique())
        )
        if estado_sel:
            df_base = df_base[df_base["estado"].isin(estado_sel)]

    # =========================
    # KPIs
    # =========================
    st.subheader("📌 Visão Geral – Qualidade")
    k1, k2, k3, k4, k5 = st.columns(5)

    i = contar_por_grupo(df_base, GRUPO_INSTALACAO)
    m = contar_por_grupo(df_base, GRUPO_MDE)
    n = contar_por_grupo(df_base, GRUPO_NAO_CONFORMIDADE)
    p = contar_por_grupo(df_base, GRUPO_POS_VENDA)

    k1.metric("INSTALAÇÃO", i)
    k2.metric("MDE", m)
    k3.metric("NCs", n)
    k4.metric("PÓS-VENDA", p)
    k5.metric("TOTAL", i + m + n + p)

    # =========================
    # TABELA
    # =========================
    st.divider()
    st.subheader("📋 Ordens para Auditoria")

    COLUNAS = {
        "codigo_cliente": "Código Cliente",
        "nome_cliente": "Cliente",
        "tipo_ordem_servico": "Tipo OS",
        "usuario_abertura": "Usuário Abertura",
        "usuario_fechamento": "Usuário Fechamento",
        "motivo_fechamento": "Motivo",
        "executor_tipo": "Executor",
        "cidade": "Cidade",
        "estado": "UF",
        "conta": "Conta",
        "id_cliente": "ID Cliente",
        "link_auditoria": "Auditar",
    }

    df_view = df_base[list(COLUNAS.keys())].rename(columns=COLUNAS)
    df_view["Selecionar"] = False

    editado = st.data_editor(
        df_view,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Selecionar": st.column_config.CheckboxColumn("Auditar"),
            "Auditar": st.column_config.LinkColumn("Abrir"),
        },
    )

    if "df_base_auditoria" in st.session_state:
        st.divider()
        render_auditoria()


    




