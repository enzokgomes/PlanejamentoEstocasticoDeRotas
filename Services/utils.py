import pandas as pd

def get_value(df, condition, column, default=0):
    filtered = df[condition]
    return filtered[column].values[0] if not filtered.empty else default

def aplicar_de_para(df, de_para, colunas):
    for coluna in colunas:
        if coluna in df.index.names:
            # Se o índice for um MultiIndex, aplica o mapeamento nas colunas especificadas
            if isinstance(df.index, pd.MultiIndex):
                # Mapeamento usando as colunas 1 e 0 (em vez de 'De' e 'Para')
                mapping = dict(zip(de_para.iloc[:, 1], de_para.iloc[:, 0]))  # Coluna 1 é 'Para', Coluna 0 é 'De'
                df.index = df.index.set_levels(
                    df.index.levels[df.index.names.index(coluna)].map(lambda x: mapping.get(x, x)),
                    level=coluna
                )
            else:
                # Se for um índice simples, aplica diretamente no índice
                mapping = dict(zip(de_para.iloc[:, 1], de_para.iloc[:, 0]))  # Coluna 1 é 'Para', Coluna 0 é 'De'
                df.index = df.index.map(lambda x: mapping.get(x, x))
    return df

def create_pivot_dataframe(data, indices, columns, values):
    """Helper function to create a pivoted DataFrame."""
    df = pd.DataFrame(data, columns=indices + columns + [values])
    return df.pivot_table(index=indices, columns=columns[0], values=values)
