# Gerenciador de Portfólio de Ativos

## 📖 Sobre o Projeto

Este projeto, desenvolvido para a disciplina de Estruturas de Dados e Algoritmos I, é uma aplicação interativa para gerenciamento de um portfólio de ações. A ferramenta permite ao usuário comprar e vender ativos, acompanhar o desempenho da carteira em tempo real e realizar análises técnicas básicas, tudo através de um dashboard web construído com Streamlit.

O grande diferencial deste projeto é a sua fundação: toda a gestão dos ativos da carteira é implementada com uma **Tabela Hash com Encadeamento Separado**, uma estrutura de dados criada do zero em Python.

-----

## A Estrutura de Dados no Coração do Sistema

O núcleo do gerenciador de portfólio é a forma como os ativos são armazenados e acessados. Para essa finalidade, foi implementada uma Tabela Hash , que utiliza o método de **Encadeamento Separado** para lidar com colisões.

### Tabela Hash com Encadeamento Separado (`TabelaHashEncadeada`)

Conforme o arquivo `estruturas_dados.py`, a estrutura principal é a `TabelaHashEncadeada`.

  * **Como funciona?** A tabela é, na essência, um array de `slots`. Para adicionar um ativo (par `chave:valor`, onde a chave é o ticker do ativo, ex: "PETR4.SA"), uma função de hash calcula um índice para esse array. O ativo é então inserido nesse `slot`.
  * **E se dois ativos caírem no mesmo `slot` (colisão)?** É aqui que o encadeamento entra. Cada `slot` da tabela não armazena um único item, mas sim a cabeça (ponteiro `head`) de uma **Lista Encadeada Simples**.

### Lista Encadeada Simples (`ListaEncadeadaSimples`)

Esta é a estrutura auxiliar que resolve as colisões.

  * Quando uma colisão ocorre, o novo ativo não substitui o antigo. Em vez disso, ele é adicionado como um novo nó no final da lista encadeada que já existe naquele `slot` da tabela.
  * Para otimizar a inserção e torná-la uma operação de complexidade **O(1)**, a lista encadeada foi implementada com um ponteiro para a cauda (`tail`), permitindo a adição de novos elementos sem a necessidade de percorrer a lista inteira.

Essa abordagem garante que as operações de busca (`get`), inserção (`put`) e remoção (`delete`) de ativos na carteira sejam, em média, extremamente eficientes, o que é ideal para uma aplicação que precisa manipular dados de forma ágil.

-----

## Funcionalidades da Aplicação

O projeto é dividido em três arquivos principais que trabalham em conjunto.

### 1\. `portifolio_manager.py`

Este é o cérebro da aplicação. A classe `PortfolioManager` encapsula toda a lógica de negócio:

  * **Controle de Saldo:** Gerencia o saldo disponível para compras.
  * **Comprar Ativos (`comprar`):** Ao comprar um ativo, o sistema verifica se ele já existe na Tabela Hash. Se sim, recalcula o preço médio; se não, insere um novo ativo.
  * **Vender Ativos (`vender`):** Realiza a venda, atualiza o saldo, calcula o lucro/prejuízo da operação e remove o ativo da Tabela Hash se a quantidade zerar.
  * **Atualização de Preços (`atualizar_precos`):** Conecta-se à API do `yfinance` para buscar as cotações mais recentes de todos os ativos da carteira, atualizando o valor total e o desempenho de cada um.
  * **Análise de Dados (`FerramentasDeAnalise`):** Uma classe auxiliar que calcula importantes indicadores técnicos para os ativos da carteira, como:
      * **RSI (Índice de Força Relativa):** Indica se um ativo está sobrecomprado ou sobrevendido.
      * **Volatilidade:** Mede o risco de um ativo com base na variação de seus retornos.
      * **Beta:** Compara a volatilidade do ativo com a do mercado (Ibovespa).

### 2\. `dashboard.py`

Este arquivo usa a biblioteca **Streamlit** para criar uma interface web interativa e amigável.

  * **Dashboard Principal:** Exibe um resumo financeiro com o saldo em conta, o valor total do portfólio e o lucro já realizado com vendas.
  * **Composição da Carteira:** Um gráfico de rosca mostra a distribuição percentual do valor de cada ativo na carteira.
  * **Minha Carteira de Ativos:** Uma tabela detalhada mostra todos os ativos, suas quantidades, preço médio, preço atual e os indicadores de análise (RSI, Volatilidade, Beta). A tabela utiliza cores para destacar o RSI (verde para sobrevendido, vermelho para sobrecomprado).
  * **Registrar Compra e Venda:** Formulários intuitivos que permitem ao usuário inserir o ticker do ativo e a quantidade para realizar uma operação. É possível buscar ativos por setor para facilitar a escolha.
  * **Análise Gráfica:** Uma seção dedicada a exibir um gráfico de candlestick interativo para qualquer ativo, permitindo a análise de seu histórico de preços com diferentes períodos e intervalos.

### 3\. `estruturas_dados.py`

A fundação do projeto, contendo as classes `NoHash`, `ListaEncadeadaSimples` e `TabelaHashEncadeada` que foram implementadas do zero para este trabalho.

-----

## 🛠️ Como Executar o Projeto

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  **Instale as dependências:**
    Certifique-se de ter o Python instalado e instale as bibliotecas necessárias.

    ```bash
    pip install streamlit pandas yfinance plotly numpy
    ```

3.  **Execute a aplicação:**
    No seu terminal, navegue até a pasta do projeto e execute o seguinte comando:

    ```bash
    streamlit run dashboard.py
    ```

4.  **Acesse o Dashboard:**
    Abra o seu navegador e acesse o endereço `http://localhost:8501` que aparecerá no terminal.
