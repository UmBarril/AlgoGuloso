import copy
from dataclasses import dataclass, field
from manim import *

# 09/06/22
# Esse código implementa o Algorítmo Guloso (Greedy Algorithm)
# https://en.wikipedia.org/wiki/Greedy_algorithm
# 
# Esse algoritmo foi ensinado nas aulas de Matemática Discreta do curso de
# Licenciatura em Ciência da Computação na UFPB

@dataclass
class Vertice:
    numero: int
    conexoes: list[Any, int] = field(default_factory=list)
    conexoes_possiveis: list[Any, int] = field(default_factory=list)

    def adicionar_aresta(self, vert, peso: int):
        self.conexoes.append((vert, peso))
    
    def adicionar_possivel_aresta(self, vert, peso):
        self.conexoes_possiveis.append((vert, peso))

    def __key(self):
        return (self.numero, "Vertice")
    
    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Vertice):
            return self.__key() == __o.__key()
        return NotImplemented

class AlgoGuloso(Scene):
    DEBUG = False

    def construct(self):
        # Esses vertices aparecerão no resultado, quer estejam conectados a outros ou não
        vertices = [1,2,3,4,5,6,7,8,9]     

        # As arestas guardam 3 dados: 
        # ID do vertice A, ID do vértice B e o peso da aresta. Ou seja: [(vertA, vertB, peso), ...]
        # Quão maior for o peso da aresta, mais o algoritmo evitará passar por ele! 
        arestas = [
            (1,2,255),(2,3,100),(3,1,200),(3,4,100),(5,6,50),(6,1,60),(6,2,90),(7,2,100),(8,1,100),(8,3,50),
            (9,8,200) # 9 -> vertice A | 8 -> vertice B | 200 -> dificuldade/peso da aresta
        ]

        # Esse é o ID do vertice em que o algoritmo vai começar.
        # Não deve fazer diferença visualmente resultado final, 
        # mas essa informação é importante para o algoritmo começar
        inicio = 1

        grafo_custo_min, peso_total = self.criar_grafo_de_custo_minimo(vertices, arestas, inicio)
        print(peso_total)

        self.play(Create(grafo_custo_min))
        self.wait(5)

    def procurar_caminho_mais_curto_recursivo(
            self,
            vertices_conectados: list[Vertice]
        ):
        """Procura o caminho com menor peso e realiza a conexao com os dois vertices"""

        # encontrar a conexao com menor peso
        menor_peso = sys.maxsize
        conexao_escolhida = None
        for vertice in vertices_conectados:
            for conexao in vertice.conexoes_possiveis:
                vert_conexao: Vertice
                vert_conexao, peso = conexao
                # vertices que já tem conexões não podem ser conectados novamente 
                # se não fecha circuito
                if vert_conexao in vertices_conectados:
                    continue
                if peso < menor_peso:
                    menor_peso = peso
                    conexao_escolhida = (vertice, vert_conexao)
            
        # se não há nenhum vertice para se conectar, terminar
        if conexao_escolhida is None:
            return

        # realizar a conexao
        vert_a, vert_b = conexao_escolhida
        vert_a.adicionar_aresta(vert_b, menor_peso)
        vert_b.adicionar_aresta(vert_a, menor_peso)

        # adicionando o novo vertice a lista de conectados
        vertices_conectados.append(vert_b)
 
        # continuar a fazer isso até que acabe com os vertices
        return self.procurar_caminho_mais_curto_recursivo(vertices_conectados)

    def comecar_procura_do_caminho_mais_curto(self, inicio: int, grafo: dict[int, Vertice]):
        """ Inicia o processo recursivo de procura e definição dos caminhos mais curtos"""
        grafo_cpy = copy.deepcopy(grafo)
        vertice_inicial = grafo_cpy[inicio]
        vertices_conectados = [vertice_inicial]
        self.procurar_caminho_mais_curto_recursivo(vertices_conectados)
        return grafo_cpy

    def criar_grafo_de_custo_minimo(self, vertices, arestas, inicio) -> tuple[Graph, int]:
        """ Retorna um grafo de custo mínimo a a partir de outro (seus vertices e arestas).
            \n Também retorna o valor somado do peso de todas as suas arestas """

        vertices_do_grafo = {v: Vertice(v) for v in vertices}
        for a in arestas:
            vertice_a, vertice_b, peso = a
            if peso < 0 or peso > 255:
                msg = "O peso de uma das arestas do grafo não pode ser maior que 100 ou menor que 0"
                raise Exception(msg)

            vert_a_obj = vertices_do_grafo[vertice_a]
            vert_b_obj = vertices_do_grafo[vertice_b]
            vert_a_obj.adicionar_possivel_aresta(vert_b_obj, peso)
            vert_b_obj.adicionar_possivel_aresta(vert_a_obj, peso)

        grafo_custo_minimo = self.comecar_procura_do_caminho_mais_curto(inicio, vertices_do_grafo)

        if self.DEBUG:
            for k, v in grafo_custo_minimo.items():
                conexoes = [c[0].numero for c in v.conexoes]
                print(f"numero {k}: {conexoes}")

        arestas_grafo_min_com_peso = self.extrair_arestas_de_dicionario_de_vertices(grafo_custo_minimo)
        arestas_grafo_min = [(a[0], a[1]) for a in arestas_grafo_min_com_peso]

        # contar o peso total de todas as arestas
        peso_total = 0
        for aresta in arestas_grafo_min_com_peso:
            peso = aresta[2]
            peso_total += peso

        # definir cores das arestas
        arestas_originais_sem_peso = [(a[0], a[1]) for a in arestas]
        config_arestas = {aresta: {"stroke_color": WHITE} for aresta in arestas_originais_sem_peso}
        # para as arestas conectadas, colocar VERMELHO
        for aresta in list(arestas_grafo_min):
            config_arestas[aresta] = {"stroke_color": RED}

        if self.DEBUG:
            print(config_arestas, end="\n\n")
            print(arestas_grafo_min)
            print(arestas_originais_sem_peso)

        # depois de ter gerado o grafo, finalmente retornar o objeto da animação(Graph MObject) 
        mobject_graph = Graph(vertices, arestas_originais_sem_peso, labels=True,
                    layout="kamada_kawai", layout_scale=3, edge_config=config_arestas)
        return (mobject_graph, peso_total)
    
    def extrair_arestas_de_dicionario_de_vertices(self, vertices: dict):
        arestas = set()
        for v in vertices.values():
            for conexao in v.conexoes:
                vert_conectado, peso = conexao
                arestas.add((v.numero, vert_conectado.numero, peso))
        return arestas