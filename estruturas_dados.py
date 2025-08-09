class NoHash:
    """Nó para a lista encadeada, armazena o par {chave-valor}."""
    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor
        self.next = None

class ListaEncadeadaSimples:
    """Lista encadeada com ponteiros head e tail."""
    def __init__(self):
        self.head = None
        self.tail = None # Adicionado o ponteiro tail

    def put(self, chave, valor):
        """Adiciona ou atualiza um nó na lista. O append é O(1)."""
        # Primeiro, verifica se a chave já existe para apenas atualizar o valor
        no_atual = self.head
        while no_atual:
            if no_atual.chave == chave:
                no_atual.valor = valor
                return
            no_atual = no_atual.next
        
        # Se a chave não existe, adiciona um novo nó no final
        novo_no = NoHash(chave, valor)
        
        if self.head is None:
            # Se a lista está vazia, head e tail apontam para o novo nó
            self.head = novo_no
            self.tail = novo_no
        else:
            # Lógica otimizada para O(1) usando o tail
            self.tail.next = novo_no
            self.tail = novo_no # Atualiza o tail para ser o novo nó

    def get(self, chave):
        """Busca um valor pela chave na lista."""
        no_atual = self.head
        while no_atual:
            if no_atual.chave == chave:
                return no_atual.valor
            no_atual = no_atual.next
        return None
    
    def delete(self, chave):
        """Deleta um nó pela chave, tratando o tail corretamente."""
        if not self.head:
            return False # Lista vazia
        
        # Caso 1: O nó a ser deletado é o head
        if self.head.chave == chave:
            self.head = self.head.next
            # Se a lista ficou vazia, atualiza o tail também
            if self.head is None:
                self.tail = None
            return True

        # Caso 2: O nó está no meio ou no fim da lista
        no_atual = self.head
        while no_atual.next:
            if no_atual.next.chave == chave:
                # Se o nó a ser deletado é o tail
                if no_atual.next == self.tail:
                    self.tail = no_atual # O nó atual se torna o novo tail
                
                # Remove a referência ao nó
                no_atual.next = no_atual.next.next
                return True
            no_atual = no_atual.next
            
        return False # Chave não encontrada

    def get_items(self):
        """Retorna todos os itens da lista."""
        items = []
        no_atual = self.head
        while no_atual:
            items.append((no_atual.chave, no_atual.valor))
            no_atual = no_atual.next
        return items


class TabelaHashEncadeada:
    """Implementação da Tabela Hash com Encadeamento Separado."""
    def __init__(self, tamanho=256):
        self.tamanho = tamanho
        self.slots = [ListaEncadeadaSimples() for _ in range(self.tamanho)]

    def _hash(self, chave):
        return hash(chave) % self.tamanho

    def put(self, chave, valor):
        h = self._hash(chave)
        self.slots[h].put(chave, valor)

    def get(self, chave):
        h = self._hash(chave)
        return self.slots[h].get(chave)
    
    def delete(self, chave):
        h = self._hash(chave)
        return self.slots[h].delete(chave)

    def get_all_items(self):
        """Retorna todos os itens da tabela hash."""
        todos_itens = []
        for lista in self.slots:
            todos_itens.extend(lista.get_items())
        return todos_itens

