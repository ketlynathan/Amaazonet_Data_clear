import streamlit as st
import pandas as pd
import time
from datetime import date

from app.analysis.ordens_servico import carregar_ordens_servico_df

# ======================================================
# CONFIG
# ======================================================
COL_NUMERO = "numero"
COL_STATUS = "status"
COL_ESTADO = "dados_endereco_instalacao.estado"
COL_USUARIO = "usuario_fechamento.name"

# ======================================================
# SESSION STATE (INICIALIZAÇÃO OBRIGATÓRIA)
# ======================================================
if "df_os" not in st.session_state:
    st.session_state.df_os = pd.DataFrame()

if "os_carregadas" not in st.session_state:
    st.session_state.os_carregadas = False

# ======================================================
# CACHE POR CONTA
# ======================================================
@st.cache_data(ttl=300)
def carregar_df_por_conta(conta, data_inicio, data_fim):
    inicio = time.perf_counter()

    df = carregar_ordens_servico_df(
        conta=conta,
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_data="data_termino_executado",
    )

    tempo = round(time.perf_counter() - inicio, 2)
    return df, tempo

# ======================================================
# FUNÇÕES AUXILIARES
# ======================================================
def badge(online):
    return "🟢 Online" if online else "🔴 Offline"

def busca_excel(df, texto):
    if not texto:
        return df

    texto = texto.lower()

    return df[
        df.astype(str)
        .apply(lambda col: col.str.lower().str.contains(texto, na=False))
        .any(axis=1)
    ]

def contar_status(df, valores):
    if COL_STATUS not in df.columns:
        return 0

    return (
        df[COL_STATUS]
        .astype(str)
        .str.upper()
        .isin(valores)
        .sum()
    )

# ======================================================
# TELA
# ======================================================
def render_ordens_servico():
    st.title("🛠️ Ordens de Serviço")

    # =============================
    # SIDEBAR
    # =============================
    with st.sidebar:
        st.subheader("🔎 Filtros de Carga (API)")

        contas = st.multiselect(
            "Contas",
            ["amazonet", "mania"],
            default=["amazonet"],
        )

        data_inicio = st.date_input(
            "Data início",
            value=date.today().replace(day=1),
        )

        data_fim = st.date_input(
            "Data fim",
            value=date.today(),
        )

        estados = st.multiselect(
            "Estado",
            ["AM", "PA"],
            default=["AM", "PA"],
        )

        if st.button("🔄 Recarregar APIs"):
            st.cache_data.clear()
            st.session_state.df_os = pd.DataFrame()
            st.session_state.os_carregadas = False
            st.success("Cache limpo")
            st.rerun()

        buscar = st.button("📊 Buscar ordens")

    # =============================
    # VALIDAÇÕES
    # =============================
    if buscar:
        if not contas:
            st.error("Selecione ao menos uma conta")
            return

        if data_inicio > data_fim:
            st.error("Data início maior que data fim")
            return

        dados = []
        status_api = {}

        with st.spinner("🔄 Carregando ordens das APIs..."):
            for conta in contas:
                try:
                    df, tempo = carregar_df_por_conta(
                        conta,
                        data_inicio,
                        data_fim,
                    )

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

        st.session_state.df_os = pd.concat(dados, ignore_index=True)
        st.session_state.os_carregadas = True
        st.session_state.status_api = status_api

    # =============================
    # SE AINDA NÃO CARREGOU
    # =============================
    if not st.session_state.os_carregadas:
        st.info("Selecione os filtros e clique em **📊 Buscar ordens**")
        return

    # =============================
    # DF BASE (NUNCA ALTERAR)
    # =============================
    df = st.session_state.df_os.copy()

    # =============================
    # STATUS DAS APIS
    # =============================
    st.subheader("🔌 Status das APIs")

    cols = st.columns(len(st.session_state.status_api))
    for col, (conta, info) in zip(cols, st.session_state.status_api.items()):
        with col:
            st.markdown(f"**{conta.upper()}**")
            st.markdown(badge(info["online"]))
            st.caption(f"⏱️ {info['tempo']}s")
            st.caption(f"📦 {info['qtd']}")

    # =============================
    # FILTROS LOCAIS (SEM API)
    # =============================
    st.subheader("🎯 Filtros locais (Excel style)")

    # Estado
    if COL_ESTADO in df.columns:
        df = df[
            df[COL_ESTADO]
            .astype(str)
            .str.upper()
            .isin(estados)
        ]

    # Busca global
    busca = st.text_input(
        "🔍 Buscar em toda a tabela",
        placeholder="Número da OS, cliente, técnico...",
    )
    df = busca_excel(df, busca)

    # Usuário fechamento
    if COL_USUARIO in df.columns:
        usuarios = (
            df[COL_USUARIO]
            .dropna()
            .astype(str)
            .sort_values()
            .unique()
            .tolist()
        )

        busca_usuario = st.text_input(
            "👤 Buscar usuário de fechamento",
            placeholder="Ex: Edinelson, MAO, STM...",
        )

        if busca_usuario:
            usuarios_filtrados = [
                u for u in usuarios
                if busca_usuario.lower() in u.lower()
            ]
        else:
            usuarios_filtrados = usuarios

        usuarios_selecionados = st.multiselect(
            "Selecionar usuários",
            usuarios_filtrados,
        )

        if usuarios_selecionados:
            df = df[df[COL_USUARIO].isin(usuarios_selecionados)]

    # =============================
    # MÉTRICAS
    # =============================
    st.subheader("📊 Indicadores")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total", len(df))
    c2.metric("✅ Fechadas", contar_status(df, ["FECHADA", "CONCLUIDA"]))
    c3.metric("⏳ Pendentes", contar_status(df, ["ABERTA", "PENDENTE"]))
    c4.metric("❌ Canceladas", contar_status(df, ["CANCELADA"]))

    # =============================
    # TABELA
    # =============================
    st.subheader("📋 Ordens de Serviço")

    st.dataframe(
        df.sort_values(COL_NUMERO, ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    # =============================
    # EXPORTAÇÃO
    # =============================
    st.download_button(
        "⬇️ Exportar CSV",
        df.to_csv(index=False),
        file_name="ordens_servico.csv",
        mime="text/csv",
    )

from app.analysis.ordens_servico import carregar_ordens_servico_df

# ======================================================
# CONFIG
# ======================================================
COL_NUMERO = "numero"
COL_STATUS = "status"
COL_ESTADO = "dados_endereco_instalacao.estado"
COL_USUARIO = "usuario_fechamento.name"

# ======================================================
# SESSION STATE (INICIALIZAÇÃO OBRIGATÓRIA)
# ======================================================
if "df_os" not in st.session_state:
    st.session_state.df_os = pd.DataFrame()

if "os_carregadas" not in st.session_state:
    st.session_state.os_carregadas = False

# ======================================================
# CACHE POR CONTA
# ======================================================
@st.cache_data(ttl=300)
def carregar_df_por_conta(conta, data_inicio, data_fim):
    inicio = time.perf_counter()

    df = carregar_ordens_servico_df(
        conta=conta,
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_data = "data_termino_executado"
        
    )

    tempo = round(time.perf_counter() - inicio, 2)
    return df, tempo

# ======================================================
# FUNÇÕES AUXILIARES
# ======================================================
def badge(online):
    return "🟢 Online" if online else "🔴 Offline"

def busca_excel(df, texto):
    if not texto:
        return df

    texto = texto.lower()

    return df[
        df.astype(str)
        .apply(lambda col: col.str.lower().str.contains(texto, na=False))
        .any(axis=1)
    ]

def contar_status(df, valores):
    if COL_STATUS not in df.columns:
        return 0

    return (
        df[COL_STATUS]
        .astype(str)
        .str.upper()
        .isin(valores)
        .sum()
    )

# ======================================================
# TELA
# ======================================================
def render_ordens_servico():
    st.title("🛠️ Ordens de Serviço")

    # =============================
    # SIDEBAR
    # =============================
    with st.sidebar:
        st.subheader("🔎 Filtros de Carga (API)")

        contas = st.multiselect(
            "Contas",
            ["amazonet", "mania"],
            default=["amazonet"],
        )

        data_inicio = st.date_input(
            "Data início",
            value=date.today().replace(day=1),
        )


        st.success(f"{len(df)} ordens encontradas")
        st.dataframe(df, use_container_width=True)


        data_fim = st.date_input(
            "Data fim",
            value=date.today(),
        )

        estados = st.multiselect(
            "Estado",
            ["AM", "PA"],
            default=["AM", "PA"],
        )

        if st.button("🔄 Recarregar APIs"):
            st.cache_data.clear()
            st.session_state.df_os = pd.DataFrame()
            st.session_state.os_carregadas = False
            st.success("Cache limpo")
            st.rerun()

        buscar = st.button("📊 Buscar ordens")

    # =============================
    # VALIDAÇÕES
    # =============================
    if buscar:
        if not contas:
            st.error("Selecione ao menos uma conta")
            return

        if data_inicio > data_fim:
            st.error("Data início maior que data fim")
            return

        dados = []
        status_api = {}

        with st.spinner("🔄 Carregando ordens das APIs..."):
            for conta in contas:
                try:
                    df, tempo = carregar_df_por_conta(
                        conta,
                        data_inicio,
                        data_fim,
                    )

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

        st.session_state.df_os = pd.concat(dados, ignore_index=True)
        st.session_state.os_carregadas = True
        st.session_state.status_api = status_api

    # =============================
    # SE AINDA NÃO CARREGOU
    # =============================
    if not st.session_state.os_carregadas:
        st.info("Selecione os filtros e clique em **📊 Buscar ordens**")
        return

    # =============================
    # DF BASE (NUNCA ALTERAR)
    # =============================
    df = st.session_state.df_os.copy()

    # =============================
    # STATUS DAS APIS
    # =============================
    st.subheader("🔌 Status das APIs")

    cols = st.columns(len(st.session_state.status_api))
    for col, (conta, info) in zip(cols, st.session_state.status_api.items()):
        with col:
            st.markdown(f"**{conta.upper()}**")
            st.markdown(badge(info["online"]))
            st.caption(f"⏱️ {info['tempo']}s")
            st.caption(f"📦 {info['qtd']}")

    # =============================
    # FILTROS LOCAIS (SEM API)
    # =============================
    st.subheader("🎯 Filtros locais (Excel style)")

    # Estado
    if COL_ESTADO in df.columns:
        df = df[
            df[COL_ESTADO]
            .astype(str)
            .str.upper()
            .isin(estados)
        ]

    # Busca global
    busca = st.text_input(
        "🔍 Buscar em toda a tabela",
        placeholder="Número da OS, cliente, técnico...",
    )
    df = busca_excel(df, busca)

    # Usuário fechamento
    if COL_USUARIO in df.columns:
        usuarios = (
            df[COL_USUARIO]
            .dropna()
            .astype(str)
            .sort_values()
            .unique()
            .tolist()
        )

        busca_usuario = st.text_input(
            "👤 Buscar usuário de fechamento",
            placeholder="Ex: Edinelson, MAO, STM...",
        )

        if busca_usuario:
            usuarios_filtrados = [
                u for u in usuarios
                if busca_usuario.lower() in u.lower()
            ]
        else:
            usuarios_filtrados = usuarios

        usuarios_selecionados = st.multiselect(
            "Selecionar usuários",
            usuarios_filtrados,
        )

        if usuarios_selecionados:
            df = df[df[COL_USUARIO].isin(usuarios_selecionados)]

    # =============================
    # MÉTRICAS
    # =============================
    st.subheader("📊 Indicadores")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total", len(df))
    c2.metric("✅ Fechadas", contar_status(df, ["FECHADA", "CONCLUIDA"]))
    c3.metric("⏳ Pendentes", contar_status(df, ["ABERTA", "PENDENTE"]))
    c4.metric("❌ Canceladas", contar_status(df, ["CANCELADA"]))

    # =============================
    # TABELA
    # =============================
    st.subheader("📋 Ordens de Serviço")

    st.dataframe(
        df.sort_values(COL_NUMERO, ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    # =============================
    # EXPORTAÇÃO
    # =============================
    st.download_button(
        "⬇️ Exportar CSV",
        df.to_csv(index=False),
        file_name="ordens_servico.csv",
        mime="text/csv",
    )

