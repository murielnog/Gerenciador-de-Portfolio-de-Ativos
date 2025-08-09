import pandas as pd 
import yfinance as yf
import numpy as np
from estruturas_dados import TabelaHashEncadeada

class PortfolioManager:

    def __init__(self, saldo_inicial=10000.0):
        self.ativos = TabelaHashEncadeada()
        self.saldo = float(saldo_inicial)
        self.lucro_vendas = 0.0
        self.analisador = FerramentasDeAnalise()

    def comprar(self, codigo, quantidade, preco_compra):
        custo_total = quantidade * preco_compra
        if custo_total > self.saldo:
            print(f"ERRO: Saldo insuficiente.")
            return False

        self.saldo -= custo_total
        dados_acao = self.ativos.get(codigo)

        if dados_acao is None:
            novo_ativo = {
                "quantidade": quantidade,
                "preco_medio": preco_compra,
                "valor_total": custo_total
            
            }
            self.ativos.put(codigo, novo_ativo)
            # Acessa o novo ativo para adicionar a transação
            dados_acao = self.ativos.get(codigo)

        else:
            # Já possui o ativo, apenas recalcula o preço médio
            qtd_antiga, preco_medio_antigo = dados_acao["quantidade"], dados_acao["preco_medio"]
            nova_qtd_total = qtd_antiga + quantidade
            novo_preco_medio = ((qtd_antiga * preco_medio_antigo) + (quantidade * preco_compra)) / nova_qtd_total
            dados_acao["quantidade"] = nova_qtd_total
            dados_acao["preco_medio"] = novo_preco_medio

            preco_recente = dados_acao.get('preco_atual', preco_compra)
            dados_acao['valor_total'] = nova_qtd_total * preco_recente

        # Adiciona a transação de compra ao histórico do ativo
        
        self.ativos.put(codigo, dados_acao) # Garante que a atualização seja salva

        print(f"SUCESSO: Compra de {quantidade} de {codigo} registrada.")
        return True

    def vender(self, codigo, quantidade, preco_venda):
        dados_acao = self.ativos.get(codigo)

        if dados_acao is None or dados_acao["quantidade"] < quantidade:
            print(f"ERRO: Venda inválida.")
            return False

        # Lógica de venda...
        valor_venda = quantidade * preco_venda
        self.saldo += valor_venda
        self.lucro_vendas += (preco_venda - dados_acao["preco_medio"]) * quantidade
        dados_acao["quantidade"] -= quantidade

        # Adiciona a transação de venda ao histórico do ativo
        dados_acao["historico"].append('Venda', quantidade, preco_venda)

        if dados_acao["quantidade"] == 0:
            self.ativos.delete(codigo)
        else:
            self.ativos.put(codigo, dados_acao)

        print(f"SUCESSO: Venda de {quantidade} de {codigo} registrada.")
        return True


    def atualizar_precos(self):
        """Busca os preços atuais de mercado para todos os ativos na carteira."""
        print("\nBuscando cotações de mercado...")
        todos_ativos = self.ativos.get_all_items()
        if not todos_ativos:
            print("Carteira vazia, nada para atualizar.")
            return

        tickers = [ativo[0] for ativo in todos_ativos]
        try:
            dados_yf = yf.download(tickers, period="1d", interval="15m", progress=False, multi_level_index=False)['Close']
            
            for codigo, dados in todos_ativos:
                preco_atual = dados_yf[codigo].iloc[-1] if len(tickers) > 1 else dados_yf.iloc[-1]
                if pd.notna(preco_atual):
                    dados['preco_atual'] = preco_atual
                    dados['valor_total'] = dados['quantidade'] * preco_atual
                    dados['lucro_prejuizo_%'] = ((preco_atual / dados['preco_medio']) - 1) * 100
                    self.ativos.put(codigo, dados)
            print("Preços atualizados com sucesso.")
        except Exception as e:
            print(f"ERRO ao buscar dados da API yfinance: {e}")

    def get_distribuicao_por_ativo(self):
        """
        Prepara os dados para o gráfico de pizza. Agora é mais robusto,
        calculando um valor de fallback se o 'valor_total' não estiver presente.
        """
        todos_ativos = self.ativos.get_all_items()
        if not todos_ativos:
            return [], []

        labels = []
        valores = []

        for codigo, dados in todos_ativos:
            # Tenta pegar o valor_total (baseado no preço de mercado mais recente)
            valor_do_ativo = dados.get('valor_total')

            # Se 'valor_total' não existir (preços ainda não atualizados),
            # calcula o valor baseado no custo (preço médio).
            if valor_do_ativo is None:
                valor_do_ativo = dados.get('quantidade', 0) * dados.get('preco_medio', 0)

            # Apenas inclui ativos com valor maior que zero no gráfico
            if valor_do_ativo > 0:
                labels.append(codigo)
                valores.append(valor_do_ativo)
            
        return labels, valores

    #Funções para acompanhar o portifolio direto do terminal, sem o dashboard
    def mostrar_portfolio(self):
        """Exibe o estado atual do portfólio no console."""
        print("\n" + "="*40)
        print("           ESTADO ATUAL DO PORTFÓLIO")
        print("="*40)
        print(f"Saldo em Conta: R$ {self.saldo:.2f}")
        
        portfolio_items = self.ativos.get_all_items()
        
        if not portfolio_items:
            print("A carteira de ativos está vazia.")
            valor_total_carteira = 0
        else:
            df_data = []
            valor_total_carteira = 0
            for codigo, dados in portfolio_items:
                valor_total_ativo = dados.get('valor_total', dados['quantidade'] * dados['preco_medio'])
                valor_total_carteira += valor_total_ativo
                df_data.append({
                    "Ação": codigo,
                    "Qtd": dados['quantidade'],
                    "Preço Médio": f"R$ {dados['preco_medio']:.2f}",
                    "Preço Atual": f"R$ {dados.get('preco_atual', 0):.2f}",
                    "Valor Total": f"R$ {valor_total_ativo:.2f}",
                    "Desempenho": f"{dados.get('lucro_prejuizo_%', 0):.2f}%"
                })
            df = pd.DataFrame(df_data)
            print(df.to_string(index=False))

        print(f"\nValor Total do Portfólio: R$ {valor_total_carteira:.2f}")
        print(f"Lucro/Prejuízo Realizado com Vendas: R$ {self.lucro_vendas:.2f}")
        patrimonio_total = self.saldo + valor_total_carteira
        print(f"Patrimônio Total (Saldo + Portfólio): R$ {patrimonio_total:.2f}")
        print("="*40 + "\n")

    

class FerramentasDeAnalise:
    """
    Uma classe dedicada a fornecer ferramentas de análise técnica e quantitativa.
    Funciona de forma independente e utiliza seu próprio cache com uma tabela hash para otimização.
    """
    def __init__(self):
        # A Tabela Hash aqui funciona como um cache para dados históricos
        self.cache_dados_historicos = TabelaHashEncadeada()

    def _get_dados_historicos(self, codigo, periodo="1y"):
        """Busca dados históricos de um ativo."""
        dados = self.cache_dados_historicos.get(codigo)
        if dados is not None:
            return dados.copy()
        
        try:
            dados = yf.Ticker(codigo).history(period=periodo, interval="1d")
            if dados.empty: return None
            self.cache_dados_historicos.put(codigo, dados)
            return dados.copy()
        except Exception:
            return None

    def calcular_volatilidade(self, codigo, janela_dias=60):
        """Calcula a volatilidade anualizada para um ativo nos últimos X dias."""
        dados = self._get_dados_historicos(codigo)
        if dados is None or len(dados) < janela_dias: return None
        
        retornos = dados['Close'].pct_change(fill_method=None).tail(janela_dias)
        volatilidade_diaria = retornos.std()
        volatilidade_anualizada = volatilidade_diaria * np.sqrt(252)
        
        return volatilidade_anualizada * 100

    def calcular_rsi(self, codigo, periodo=14):
        """Calcula o Índice de Força Relativa para um ativo."""
        dados = self._get_dados_historicos(codigo)
        if dados is None or len(dados) < periodo: return None
            
        diferenca = dados['Close'].diff(1)
        ganhos = diferenca.where(diferenca > 0, 0)
        perdas = -diferenca.where(diferenca < 0, 0)
        
        media_ganhos = ganhos.rolling(window=periodo).mean()
        media_perdas = perdas.rolling(window=periodo).mean()
        
        rs = media_ganhos / media_perdas
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]

    def calcular_beta(self, codigo, janela_dias=252):
        """Calcula o Beta de um ativo em relação ao Ibovespa (^BVSP)."""
        dados_ativo = self._get_dados_historicos(codigo, periodo="2y") # Periodo maior para garantir dados
        dados_ibov = self._get_dados_historicos("^BVSP", periodo="2y")

        if dados_ativo is None or dados_ibov is None: return None

        retornos = pd.concat([dados_ativo['Close'], dados_ibov['Close']], axis=1).pct_change(fill_method=None).tail(janela_dias)
        retornos.columns = [codigo, 'IBOV']
        
        if len(retornos) < janela_dias or retornos.isnull().values.any(): return None

        covariancia = retornos.cov().iloc[0, 1]
        variancia_mercado = retornos['IBOV'].var()
        
        beta = covariancia / variancia_mercado
        return beta
    
    