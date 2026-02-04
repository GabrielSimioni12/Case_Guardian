import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def resolver_case():
    print("🚀 Iniciando análise...")

    # 1. Carregar Dados
    try:
        # Lendo com separador ;
        df = pd.read_csv('carteira.csv', sep=';')
        print("✅ Arquivo encontrado!")
    except Exception as e:
        print(f"❌ Erro ao abrir arquivo: {e}")
        return

    # Limpeza de colunas numéricas (evita erro de texto vs número)
    colunas_numericas = ['valor_parcela', 'valor_aquisicao_parcela', 'taxa_mensal', 'valor_pago']
    
    for col in colunas_numericas:
        if df[col].dtype == 'object': 
            df[col] = df[col].str.replace(',', '.') 
        df[col] = pd.to_numeric(df[col], errors='coerce') 

    # 2. Tipagem de Datas
    df['mes_aquisicao'] = pd.to_datetime(df['mes_aquisicao'], dayfirst=True)
    df['mes_vencimento'] = pd.to_datetime(df['mes_vencimento'], dayfirst=True)
    df['valor_pago'] = df['valor_pago'].fillna(0)
    data_focal = pd.to_datetime('2026-01-31')

    # --- ETAPA 1: Valor Presente (Bônus) ---
    df['n'] = ((df['mes_vencimento'].dt.year - data_focal.year) * 12 + 
               (df['mes_vencimento'].dt.month - data_focal.month))
    
    df['valor_presente'] = df['valor_parcela'] / ((1 + df['taxa_mensal']) ** df['n'])

    # PRINT DA ETAPA 1 (MOVIMENTADO PARA DENTRO DA FUNÇÃO)
    print("\n--- DISTRIBUIÇÃO ETAPA 1 (VALORES TOTAIS E VP) ---")
    distribuicao = df.groupby('id_convenio')[['valor_parcela', 'valor_aquisicao_parcela', 'valor_presente']].sum()
    print(distribuicao)

    # --- ETAPA 2: Taxa Média Ponderada ---
    taxa_media = (df['taxa_mensal'] * df['valor_aquisicao_parcela']).sum() / df['valor_aquisicao_parcela'].sum()
    print(f"\n📊 Taxa Média Ponderada da Carteira: {taxa_media:.4%}")

    # --- ETAPA 3: Inadimplência ---
    vencidas = df[df['mes_vencimento'] < data_focal].copy()
    
    inad_conv = vencidas.groupby('id_convenio').apply(
        lambda x: 1 - (x['valor_pago'].sum() / x['valor_parcela'].sum())
    )

    # --- ETAPA 4: Gerar Gráficos ---
    print("\n📈 Gravando gráficos...")
    
    plt.figure(figsize=(10,6))
    inad_conv.plot(kind='bar', color='firebrick')
    plt.title('Taxa de Inadimplência por Convênio')
    plt.savefig('grafico_convenio.png')
    plt.close()

    inad_safra = vencidas.groupby(vencidas['mes_aquisicao'].dt.to_period('M')).apply(
        lambda x: 1 - (x['valor_pago'].sum() / x['valor_parcela'].sum())
    )
    plt.figure(figsize=(10,6))
    inad_safra.plot(kind='line', marker='o')
    plt.title('Evolução da Inadimplência por Safra')
    plt.savefig('grafico_safra.png')
    plt.close()

    print("✅ Concluído! Verifique os arquivos .png e as tabelas acima.")

if __name__ == "__main__":
    resolver_case()