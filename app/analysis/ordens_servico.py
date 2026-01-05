import pandas as pd
from datetime import date
from app.hubsoft.factory import get_hubsoft_client


def carregar_ordens_servico_df(
    conta: str,
    data_inicio: date,
    data_fim: date,
    tipo_data: str = "data_cadastro",
    itens_por_pagina: int = 100,
    max_paginas: int = 50,  # 🔴 LIMITE DE SEGURANÇA
) -> pd.DataFrame:
    client = get_hubsoft_client(conta)

    pagina = 1
    todas_ordens = []

    while pagina <= max_paginas:
        payload = {
            "pagina": pagina,
            "itens_por_pagina": itens_por_pagina,
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
            "tipo_data": tipo_data,
        }

        data = client.get(
            "integracao/ordem_servico/todos",
            params=payload,
        )

        if not isinstance(data, dict):
            break

        ordens = data.get("ordens_servico", [])

        if not ordens:
            break

        todas_ordens.extend(ordens)
        pagina += 1

    if not todas_ordens:
        return pd.DataFrame()

    return pd.json_normalize(todas_ordens)
