import streamlit as st
import pandas as pd
<<<<<<< HEAD
import time
=======
>>>>>>> dev

from app.analysis.usuarios import carregar_usuarios_df


<<<<<<< HEAD
# ======================================================
# CONFIG
# ======================================================
COL_NOME = "name"


# ======================================================
# CACHE POR CONTA
# ======================================================
@st.cache_data(ttl=600)
def carregar_df_por_conta(conta: str):
    inicio = time.perf_counter()
    df = carregar_usuarios_df(conta)
    tempo = round(time.perf_counter() - inicio, 2)
    return df, tempo


# ======================================================
# FUNÇÕES
# ======================================================
def busca_excel(df, texto):
    if not texto:
        return df
    return df[df[COL_NOME].str.contains(texto, case=False, na=False)]


def contar_tag(df, tag):
    return df[COL_NOME].str.contains(tag, case=False, na=False).sum()


def badge(status):
    return "🟢 Online" if status else "🔴 Offline"


# ======================================================
# TELA
# ======================================================
def render_usuarios():
    st.title("👤 Usuários")

    # =============================
    # SIDEBAR
    # =============================
    with st.sidebar:
        st.subheader("⚙️ Contas")

        contas = st.multiselect(
            "Selecione as contas",
            ["amazonet", "mania"],
            default=["amazonet"],
        )

        busca = st.text_input(
            "🔍 Buscar (Excel)",
            placeholder="Ex: TEC, MAO, STM, Edinelson...",
        )

        if st.button("🔄 Recarregar APIs"):
            st.cache_data.clear()
            st.success("Cache limpo com sucesso")
            st.rerun()

    if not contas:
        st.warning("Selecione ao menos uma conta")
        return

    # =============================
    # CARREGAMENTO APIs
    # =============================
    dados = []
    status_api = {}

    with st.spinner("🔄 Carregando dados das APIs..."):
        for conta in contas:
            try:
                df, tempo = carregar_df_por_conta(conta)

                online = not df.empty
                status_api[conta] = {
                    "online": online,
                    "tempo": tempo,
                    "qtd": len(df),
                }

                if online:
                    df["conta"] = conta.upper()
                    dados.append(df)

            except Exception as e:
                status_api[conta] = {
                    "online": False,
                    "tempo": None,
                    "qtd": 0,
                }
                st.error(f"Erro na API {conta}")
                st.exception(e)

    if not dados:
        st.error("Nenhuma API retornou dados")
        return

    df = pd.concat(dados, ignore_index=True)

    # =============================
    # STATUS DAS APIS (CLICÁVEL)
    # =============================
    st.subheader("🔌 Status das APIs")

    colunas = st.columns(len(status_api))
    for col, (conta, info) in zip(colunas, status_api.items()):
        with col:
            if st.button(
                f"{badge(info['online'])}\n{conta.upper()}",
                key=f"btn_{conta}",
            ):
                st.session_state["filtro_conta"] = conta.upper()

            st.caption(f"⏱️ {info['tempo']}s")
            st.caption(f"👥 {info['qtd']} usuários")

    # =============================
    # FILTRO POR CONTA (CLICK CARD)
    # =============================
    if "filtro_conta" in st.session_state:
        df = df[df["conta"] == st.session_state["filtro_conta"]]
        st.info(f"Filtro ativo: {st.session_state['filtro_conta']}")

        if st.button("❌ Limpar filtro de conta"):
            del st.session_state["filtro_conta"]
            st.rerun()

    # =============================
    # BUSCA EXCEL
    # =============================
    df = busca_excel(df, busca)

    # =============================
    # MÉTRICAS
    # =============================
    st.subheader("📊 Indicadores")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total", len(df))
    c2.metric("👷 Técnicos", contar_tag(df, "TEC"))
    c3.metric("🧪 Qualidade", contar_tag(df, "QLD"))
    c4.metric("💼 Comercial", contar_tag(df, "CMRC"))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("🔁 Fidelização", contar_tag(df, "FIDL"))
    c6.metric("🛒 Compras", contar_tag(df, "COMPRAS"))
    c7.metric("🧰 Suporte Técnico", contar_tag(df, "STT"))
    c8.metric("💰 Financeiro", contar_tag(df, "FIN"))

    c9, c10, c11 = st.columns(3)
    c9.metric("🤝 Terceirizados", contar_tag(df, "TERC"))
    c10.metric("📍 AM (MAO)", contar_tag(df, "MAO"))
    c11.metric("📍 PA (STM)", contar_tag(df, "STM"))

    st.subheader("📋 Lista de Usuários")

    if df.empty:
        st.warning("Nenhum usuário encontrado após os filtros aplicados.")
    else:
        st.dataframe(
            df.sort_values(COL_NOME),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(f"Mostrando {len(df)} usuários")

        st.download_button(
            "⬇️ Exportar usuários (CSV)",
            df.to_csv(index=False),
            file_name="usuarios_filtrados.csv",
            mime="text/csv",
        )

=======
@st.cache_data(ttl=600)
def carregar_df(conta: str) -> pd.DataFrame:
    return carregar_usuarios_df(conta)


def render_usuarios():
    st.title("👤 Usuários")

    conta = st.selectbox(
        "Conta",
        ["mania", "amazonet"],
        index=0,
    )

    try:
        with st.spinner("Carregando usuários..."):
            df = carregar_df(conta)

    except Exception as e:
        st.error("❌ Erro ao carregar usuários")
        st.exception(e)
        return

    if df.empty:
        st.warning("Nenhum usuário encontrado")
        return

    st.success(f"{len(df)} usuários carregados")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
>>>>>>> dev
