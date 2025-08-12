import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import time
import numpy as np
from portifolio_manager import PortfolioManager


@st.cache_data(ttl=300)
def buscar_dados_historicos(ticker, periodo, intervalo):
    try:
        dados = yf.Ticker(ticker).history(period=periodo, interval=intervalo)
        if dados.empty:
            st.warning(f"Não foram encontrados dados para '{ticker}' com os parâmetros selecionados.")
            return None
        return dados
    except Exception as e:
        st.error(f"Erro ao buscar dados da API: {e}")
        return None

def exibir_grafico_candlestick(ticker, periodo, intervalo):
    df = buscar_dados_historicos(ticker, periodo, intervalo)
    if df is None or df.empty:
        st.warning(f"Não há dados disponíveis para exibir o gráfico de '{ticker}'.")
        return
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candlestick"
    ))
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["Volume"],
        name="Volume",
        marker_color="lightblue",
        yaxis="y2",
        opacity=0.5
    ))
    fig.update_layout(
        title=f'Gráfico Interativo - {ticker} ({periodo}, {intervalo})',
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
            showspikes=True,
            spikemode="across",
            spikecolor="grey",
            spikesnap="cursor"
        ),
        yaxis=dict(
            title="Preço",
            side="right",
            showspikes=True,
            spikecolor="grey",
            spikemode="across",
            spikesnap="cursor"
        ),
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="left",
            position=0.0,
            showgrid=False,
            range=[0, df["Volume"].max() * 4],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        hovermode="x unified",
        margin=dict(t=50, b=40, l=40, r=40)
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(layout="wide")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = PortfolioManager()

    #Para testar as funcionalidades da carteira, adiciona-se previamente alguns ativos ao portifólio agora:
    if st.button("Adicionar alguns ativos a carteira automaticamente", key="add_ativos", use_container_width=True):
        compras_ticker = ["PETR4.SA", "AAPL","BBAS3.SA"]
        for ticker in compras_ticker:
            info_compra = yf.Ticker(ticker).info
            preco_compra_atual = info_compra.get('currentPrice')
            st.session_state.portfolio.comprar(ticker, 10, preco_compra_atual)

    

    st.title("Gerenciador de Portfólio")
    st.header("Resumo Financeiro")

    col11, col12 = st.columns(2)

    with col11:
        st.metric("Saldo em Conta", f"R$ {st.session_state.portfolio.saldo:.2f}")
        portfolio_items = st.session_state.portfolio.ativos.get_all_items()
        valor_total_carteira = sum(item[1].get('valor_total', 0) for item in portfolio_items)

        st.metric("Valor do Portfólio", f"R$ {valor_total_carteira:.2f}")

        lucro_vendas = st.session_state.portfolio.lucro_vendas
        cor_lucro = "normal" if lucro_vendas >= 0 else "inverse"
        st.metric("Lucro/Prejuízo Realizado", f"R$ {lucro_vendas:.2f}", delta_color=cor_lucro)
    
    with col12:
        st.text("Composição da Carteira por Ativo")
        labels, valores = st.session_state.portfolio.get_distribuicao_por_ativo()
        
        if not labels:
            st.info("A carteira está vazia. Compre ativos para ver a composição.")
        else:
            # Cria a figura do gráfico de pizza/rosca
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=valores, 
                hole=.3, # Cria o buraco no meio (gráfico de rosca)
                pull=[0.05 if i == np.argmax(valores) else 0 for i in range(len(valores))] # Destaca a maior fatia
            )])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                showlegend=False,
                margin=dict(t=0, b=0, l=0, r=0)
            )
            fig.update_layout(
    width=350,  # Largura em pixels
    height=300  # Altura em pixels
)
            fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),  # Remove margens do gráfico
    # Altura menor
    )
            st.plotly_chart(fig, use_container_width=True)

    st.header("Minha Carteira de Ativos")
    if not portfolio_items:
        st.info("Seu portfólio está vazio. Vá para a página 'Mercado de Ações' para começar a investir.")
    else:
        df_data = []
        with st.spinner("Calculando indicadores de análise..."):
            for codigo, dados in portfolio_items:
                analisador = st.session_state.portfolio.analisador
                volatilidade = analisador.calcular_volatilidade(codigo)
                rsi = analisador.calcular_rsi(codigo)
                beta = analisador.calcular_beta(codigo)
                infos = yf.Ticker(codigo).info
                df_data.append({
                    "Empresa": infos.get("shortName", None),
                    "Ação": codigo,
                    "Quantidade": dados['quantidade'],
                    "Preço Médio (R$)": dados['preco_medio'],
                    "Preço Atual (R$)": infos.get("currentPrice", None),
                    "Desempenho (%)": dados.get('lucro_prejuizo_%', 0),
                    "RSI (14d)":  rsi,
                    "Volatilidade (60d)": volatilidade,
                    "Beta (1a)": beta if beta is not None else infos.get("beta", None),
                })
        df_portfolio = pd.DataFrame(df_data)
        def colorir_rsi(val):
            if isinstance(val, str) and val != "N/A":
                rsi_val = float(val)
                if rsi_val > 70: return 'background-color: #ffadad'
                if rsi_val < 30: return 'background-color: #a0e8a0'
            return ''
        st.dataframe(df_portfolio.style.format({
                         'Preço Médio (R$)': 'R$ {:,.2f}',
                         'Preço Atual (R$)': 'R$ {:,.2f}',
                         'Valor Total (R$)': 'R$ {:,.2f}',
                         'Desempenho (%)': '{:.2f}%',
                         'RSI (14d)': '{:.2f}',
                         'Volatilidade (60d)': '{:.2f}%',
                         'Beta (1a)': '{:.2f}'
                     }, na_rep="N/A") 
                     .map(colorir_rsi, subset=['RSI (14d)']),
                     use_container_width=True)

        if st.button("Atualizar Preços da Carteira", key="btn_atualizar_main"):
            with st.spinner("Buscando cotações..."):
                st.session_state.portfolio.atualizar_precos()
            st.rerun()

    col21,col22 = st.columns(2)
    ACOES_POR_SETOR = {
        "Financeiro": ["ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "SANB11.SA", "BPAC11.SA"],
        "Varejo": ["MGLU3.SA", "LREN3.SA", "BHIA3.SA", "AMER3.SA", "PETZ3.SA"],
        "Energia e Matérias-Primas": ["PETR4.SA", "VALE3.SA", "SUZB3.SA", "ELET3.SA", "PRIO3.SA"],
        "Saúde": ["RADL3.SA", "HAPV3.SA", "FLRY3.SA", "RDOR3.SA", "AALR3.SA"],
        "Tecnologia": ["TOTS3.SA", "LWSA3.SA", "CASH3.SA", "SQIA3.SA", "ZENV4.SA"]
    }
    with col21:
        st.header("Registrar Compra")
        usar_setores = st.checkbox("Buscar ativo por setor", key="compra_por_setor")
        with st.form("compra_form"):
            if usar_setores:
                setor_selecionado = st.selectbox("Selecione um Setor", list(ACOES_POR_SETOR.keys()))
                if setor_selecionado:
                    acoes_do_setor = ACOES_POR_SETOR[setor_selecionado]
                    compra_ticker = st.selectbox("Selecione o Ativo para Comprar", acoes_do_setor)
                else:
                    compra_ticker = st.text_input("Insira o código do ativo (ex: PETR4.SA)").upper()
            else:
                compra_ticker = st.text_input("Insira o código do ativo (ex: PETR4.SA)").upper()

            compra_qtd = st.number_input("Quantidade", min_value=1, step=1)
            compra_submitted = st.form_submit_button("Confirmar Compra")

            if compra_submitted:
                with st.spinner(f"Buscando cotação atual para {compra_ticker}..."):
                    try:
                        info_compra = yf.Ticker(compra_ticker).info
                        preco_compra_atual = info_compra.get('currentPrice')

                        if preco_compra_atual:
                            st.session_state.portfolio.comprar(compra_ticker, compra_qtd, preco_compra_atual)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Não foi possível obter o preço atual para {compra_ticker}. Verifique o código.")
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao buscar dados para {compra_ticker}: Ticker inválido ou falha na conexão.")
    with col22:    
        st.header("Registrar Venda")
        with st.form("venda_form"):
            lista_tickers = [item[0] for item in portfolio_items] if portfolio_items else []
            venda_ticker = st.selectbox("Selecione o Ativo para Vender", lista_tickers, key="venda_ticker_select")
            venda_qtd = st.number_input("Quantidade a Vender", min_value=1, step=1)
            preco_venda_atual = 0
            if venda_ticker:
                try:
                    dados_venda = yf.Ticker(venda_ticker).info
                    preco_venda_atual = dados_venda.get('currentPrice', 0)
                    st.info(f"Preço de mercado atual para {venda_ticker}: R$ {preco_venda_atual:.2f}")
                    for codigo, dados in portfolio_items:
                        if codigo == venda_ticker:
                            st.info(f"Preço médio pago por ação: R$ {dados['preco_medio']}")
                except Exception:
                    st.warning("Não foi possível obter o preço de mercado atual.")
            venda_submitted = st.form_submit_button("Executar Venda")
            if venda_submitted:
                if st.session_state.portfolio.vender(venda_ticker, venda_qtd, preco_venda_atual):
                    st.success(f"Venda de {venda_qtd} de {venda_ticker} registrada!")
                    time.sleep(1)
                    st.rerun()

    st.header("Análise Gráfica de Ativos")
    lista_tickers = [item[0] for item in portfolio_items] if portfolio_items else []
    col31, col32, col33 = st.columns(3)
    with col31:
        ticker_selecionado = st.text_input("Insira o código do ativo")
        if lista_tickers:
            dos_ativos = st.checkbox("Selecionar Ativo da Carteira")
            if dos_ativos:
                lista_ativos = st.selectbox("Selecionar Ativo", lista_tickers)
                ticker_selecionado = lista_ativos
    with col32:
        periodo_selecionado = st.selectbox(
            "Selecione o Período",
            ["1d", "5d","1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=0
        )
    with col33:
        intervalo_selecionado = st.selectbox(
            "Selecione o Intervalo",
            ["30m", "60m","1d", "1wk", "1mo"],
            index=0
        )
    if ticker_selecionado:
        exibir_grafico_candlestick(
            ticker=ticker_selecionado,
            periodo=periodo_selecionado,
            intervalo=intervalo_selecionado
        )
