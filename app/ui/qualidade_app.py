import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.ordens_servico import carregar_ordens_servico_df
from app.ui.components.navigation import botao_voltar_home

# ======================================================
# CONSTANTES DE COLUNAS
# ======================================================
COL_STATUS = "status"
COL_TECNICO = "usuario_fechamento.name"
COL_ESTADO = "dados_endereco_instalacao.estado"
COL_TIPO = "tipo"
COL_EXECUTOR_TIPO = "executor_tipo"

STATUS_FINALIZADO = "Finalizado"
STATUS_PENDENTE = "Pendente"

STATUS_MONITORADOS = [STATUS_FINALIZADO, STATUS_PENDENTE]

# ======================================================
# GRUPOS DE TIPO
# ======================================================
GRUPO_INSTALACAO = [
    "INSTALAÇÃO (R$ 49,90) - VALOR OBRIGATÓRIO: R$ 49.90",
    "INSTALAÇÃO (R$ 100,00) - VALOR OBRIGATÓRIO: R$ 100.00",
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

GRUPO_POS_SUPORTE = [
    "PÓS-SUPORTE",
    "POS-SUPORTE",
    "AMZ QUALIDADE - PÓS SUPORTE",
]

# ======================================================
# FUNÇÕES AUXILIARES
# ======================================================
def contar_por_grupo(df: pd.DataFrame, tipos: list[str]) -> tuple[int, int]:
    if df.empty or COL_TIPO not in df.columns:
        return 0, 0

    total = df[df[COL_TIPO].isin(tipos)].shape[0]
    pendentes = df[
        (df[COL_TIPO].isin(tipos)) &
        (df[COL_STATUS] == STATUS_PENDENTE)
    ].shape[0]

    return total, pendentes


def classificar_executor(df: pd.DataFrame) -> pd.DataFrame:
    """
    TERCEIRIZADOS se nome contiver:
    TEC_TERC | TEC_LOBATOS | TEC_LL
    """
    df = df.copy()
    df[COL_EXECUTOR_TIPO] = "CAMPO"

    if COL_TECNICO in df.columns:
        df.loc[
            df[COL_TECNICO].str.contains(
                r"TEC_TERC|TEC_LOBATOS|TEC_LL",
                case=False,
                na=False,
                regex=True
            ),
            COL_EXECUTOR_TIPO
        ] = "TERCEIRIZADOS"

    return df


def gerar_link_auditoria(row: pd.Series) -> str:
    cliente_id = row.get("dados_cliente.Id_cliente")

    if not cliente_id:
        return ""

    if row.get("conta") == "amazonet":
        return f"https://amazonet.hubsoft.com.br/cliente/editar/{cliente_id}/servico"

    if row.get("conta") == "mania":
        return f"https://mania.hubsoft.com.br/cliente/editar/{cliente_id}/servico"

    return ""


# ======================================================
# APP
# ======================================================
def render_qualidade():
    botao_voltar_home()
    st.title("📊 Análise de Qualidade")

    st.session_state.setdefault("df_os", pd.DataFrame())
    st.session_state.setdefault("carregado", False)

    # ======================================================
    # SIDEBAR
    # ======================================================
    with st.sidebar:
        st.subheader("🔎 Filtros base")

        contas = st.multiselect(
            "Contas",
            ["mania", "amazonet"],
            default=["mania", "amazonet"],
        )

        hoje = date.today()
        data_inicio = st.date_input("Data início", hoje - timedelta(days=7))
        data_fim = st.date_input("Data fim", hoje)

        carregar = st.button("📥 Carregar ordens")

    # ======================================================
    # CARREGAMENTO
    # ======================================================
    if carregar:
        if not contas:
            st.warning("Selecione ao menos uma conta.")
            return

        dfs = []

        with st.spinner("🔄 Carregando ordens..."):
            for conta in contas:
                df_conta = carregar_ordens_servico_df(
                    conta=conta,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )

                if df_conta is not None and not df_conta.empty:
                    df_conta["conta"] = conta
                    dfs.append(df_conta)

        if not dfs:
            st.warning("Nenhuma ordem encontrada.")
            return

        df_final = pd.concat(dfs, ignore_index=True)
        df_final = classificar_executor(df_final)
        df_final["link_auditoria"] = df_final.apply(gerar_link_auditoria, axis=1)

        st.session_state["df_os"] = df_final
        st.session_state["carregado"] = True

    if not st.session_state["carregado"]:
        st.info("Selecione os filtros e clique em **📥 Carregar ordens**.")
        return

    df_base = st.session_state["df_os"].copy()
    st.success(f"✅ {len(df_base)} ordens carregadas.")

    # ======================================================
    # FILTROS
    # ======================================================
    st.subheader("🎯 Filtros de Qualidade")
    c1, c2, c3 = st.columns(3)

    with c1:
        status_opcoes = sorted(df_base[COL_STATUS].dropna().unique())

        status_default = [
            s for s in STATUS_MONITORADOS
            if s in status_opcoes
        ]

        status_sel = st.multiselect(
            "Status",
            status_opcoes,
            default=status_default,
)


        tecnico_sel = st.multiselect(
            "Técnico",
            sorted(df_base[COL_TECNICO].dropna().unique()),
        )
        if tecnico_sel:
            df_base = df_base[df_base[COL_TECNICO].isin(tecnico_sel)]

    with c2:
        tipo_sel = st.multiselect(
            "Tipo",
            sorted(df_base[COL_TIPO].dropna().unique()),
        )
        if tipo_sel:
            df_base = df_base[df_base[COL_TIPO].isin(tipo_sel)]

        executor_sel = st.multiselect(
            "Executor",
            ["CAMPO", "TERCEIRIZADOS"],
            default=["CAMPO", "TERCEIRIZADOS"],
        )
        df_base = df_base[df_base[COL_EXECUTOR_TIPO].isin(executor_sel)]

    with c3:
        estado_sel = st.multiselect(
            "Estado",
            sorted(df_base[COL_ESTADO].dropna().unique()),
        )
        if estado_sel:
            df_base = df_base[df_base[COL_ESTADO].isin(estado_sel)]

    # ======================================================
    # KPIs
    # ======================================================
    st.subheader("📌 Visão Geral – Qualidade")
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    k1.metric("INSTALAÇÃO", *contar_por_grupo(df_base, GRUPO_INSTALACAO))
    k2.metric("MDE.", *contar_por_grupo(df_base, GRUPO_MDE))
    k3.metric("NCs.", *contar_por_grupo(df_base, GRUPO_NAO_CONFORMIDADE))
    k4.metric("PÓS-VENDA", *contar_por_grupo(df_base, GRUPO_POS_VENDA))
    k5.metric("PÓS-SUPORTE", *contar_por_grupo(df_base, GRUPO_POS_SUPORTE))

    k6.metric("TOTAL", len(df_base))

    # ======================================================
    # TABELA FINAL ENXUTA
    # ======================================================
    st.divider()
    st.subheader("📋 Ordens para Auditoria")

    COLUNAS_EXIBIR = {
        "dados_cliente.Id_cliente": "ID Cliente",
        "dados_cliente.codigo_cliente": "Código Cliente",
        "numero": "OS",
        "cliente": "Cliente",
        "tipo": "Tipo",
        "status": "Status",
        "descricao_fechamento": "Descrição",
        "data_termino_executado": "Execução",
        "data_cadastro": "Cadastro",
        "usuario_fechamento.name": "Técnico",
        "executor_tipo": "Executor",
        "conta": "Conta",
        "link_auditoria": "Auditar",
    }

    colunas_existentes = [
        col for col in COLUNAS_EXIBIR.keys()
        if col in df_base.columns
    ]

    df_exibir = (
        df_base[colunas_existentes]
        .rename(columns=COLUNAS_EXIBIR)
    )

    st.dataframe(
    df_exibir,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Auditar": st.column_config.LinkColumn(
            label="Auditar",
            help="Abrir cliente no HubSoft",
            display_text="🔍 Auditar",
        ),
        "Execução": st.column_config.DatetimeColumn(
            format="DD/MM/YYYY HH:mm",
        ),
        "Cadastro": st.column_config.DatetimeColumn(
            format="DD/MM/YYYY HH:mm",
        ),
    },
)


