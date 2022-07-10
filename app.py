import math

from flask import Flask, request
from flask_restful import Resource, Api
from models import OperacaoJuroComposto
from models import Operacoes
from models import OperacaoTaxaNominal
from models import OperacaoTaxaEfetiva
from models import OperacaoTaxaJurosReal
from models import FatorAcumulacaoCapital
from models import DescontoSimples
from models import DescontoComposto
from models import SistemaPrestacaoConstante
import numpy

app = Flask(__name__)
api = Api(app)


class JuroComposto(Resource):
    def get(self, juroscompostos):
        juros_compostos = OperacaoJuroComposto.query.filter_by(juroscompostos=juroscompostos).first()
        try:
            response = {
                'juroscompostos': juros_compostos.juroscompostos,
                'capital': juros_compostos.capital,
                'taxa': juros_compostos.taxa,
                'tempo': juros_compostos.tempo
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'Juros não encontrado'
            }
        return response

    def put(self, juroscompostos):
        juros_compostos = OperacaoJuroComposto.query.filter_by(juroscompostos=juroscompostos).first()
        dados = request.json
        if 'juroscompostos' in dados:
            juros_compostos.juroscompostos = dados['juroscompostos']

        if 'capital' in dados:
            juros_compostos.capital = dados['capital']

        if 'taxa' in dados:
            juros_compostos.taxa = dados['taxa']

        if 'tempo' in dados:
            juros_compostos.taxa = dados['tempo']

        juros_compostos.save()
        response = {
            'id': juros_compostos.id,
            'juroscompostos': juros_compostos.juroscompostos,
            'capital': juros_compostos.capital,
            'taxa': juros_compostos.taxa,
            'tempo': juros_compostos.tempo
        }

        return response

    def delete(self, juroscompostos):
        juroscompostos = OperacaoJuroComposto.query.filter_by(id=juroscompostos).first()
        mensagem = 'Juros {} excluidos com sucesso'.format(juroscompostos)
        juroscompostos.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaJurosCompostos(Resource):

    def get(self):
        juros_compostos = OperacaoJuroComposto.query.all()
        response = [{
            'id': i.id,
            'juroscompostos': i.juroscompostos,
            'capital': i.capital,
            'taxa': i.taxa,
            'tempo': i.tempo
        } for i in juros_compostos]
        return response

    def post(self):
        dados = request.json
        # calcular o Juros
        if dados['capital'] and dados['taxa'] and dados['tempo'] > 0:
            juros_compostos = OperacaoJuroComposto(
                id=dados['id'],
                juroscompostos=dados['capital'] * pow(1 + dados['taxa'] / 100, dados['tempo']),
                capital=dados['capital'],
                taxa=dados['taxa'],
                tempo=dados['tempo']
            )
        # calcular a taxa
        if dados['juroscompostos'] and dados['capital'] and dados['tempo'] > 0:
            juros_compostos = OperacaoJuroComposto(
                id=dados['id'],
                juroscompostos=dados['juroscompostos'],
                capital=dados['capital'],
                taxa=numpy.sqrt(dados['juroscompostos'] / dados['capital']) - 1,
                tempo=dados['tempo']
            )
        # calcular o capital
        if dados['juroscompostos'] and dados['taxa'] and dados['tempo'] > 0:
            juros_compostos = OperacaoJuroComposto(
                id=dados['id'],
                juroscompostos=dados['juroscompostos'],
                capital=dados['juroscompostos'] / (1 + dados['taxa'] / 100) ^ dados['tempo'],
                taxa=dados['taxa'],
                tempo=dados['tempo']
            )
        # calcular o tempo
        if dados['juroscompostos'] and dados['capital'] and dados['taxa'] > 0:
            juros_compostos = OperacaoJuroComposto(
                id=dados['id'],
                juroscompostos=dados['juroscompostos'],
                capital=dados['capital'],
                taxa=dados['taxa'],
                tempo=numpy.log(dados['juroscompostos'] / dados['capital']) / numpy.log(1 + dados['taxa'] / 100)
            )
        juros_compostos.save()
        response = {
            'id': juros_compostos.id,
            'juroscompostos': juros_compostos.juroscompostos,
            'capital': juros_compostos.capital,
            'taxa': juros_compostos.taxa,
            'tempo': juros_compostos.tempo
        }
        return response


class Operacao(Resource):
    def get(self, jurossimples):
        juros_simples = Operacoes.query.filter_by(jurossimples=jurossimples).first()
        try:
            response = {
                'jurossimples': juros_simples.jurossimples,
                'capital': juros_simples.capital,
                'taxa': juros_simples.taxa,
                'tempo': juros_simples.tempo
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'Juros não encontrado'
            }
        return response

    def put(self, jurossimples):
        juros_simples = Operacoes.query.filter_by(jurossimples=jurossimples).first()
        dados = request.json
        if 'jurossimples' in dados:
            juros_simples.jurossimples = dados['jurossimples']

        if 'capital' in dados:
            juros_simples.capital = dados['capital']

        if 'taxa' in dados:
            juros_simples.taxa = dados['taxa']

        if 'tempo' in dados:
            juros_simples.taxa = dados['tempo']

        juros_simples.save()
        response = {
            'id': juros_simples.id,
            'jurossimples': juros_simples.jurossimples,
            'capital': juros_simples.capital,
            'taxa': juros_simples.taxa,
            'tempo': juros_simples.tempo
        }

        return response

    def delete(self, id):
        jurossimples = Operacoes.query.filter_by(id=id).first()
        mensagem = 'Juros {} excluidos com sucesso'.format(jurossimples)
        jurossimples.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaOperacoes(Resource):

    def get(self):
        juros_simples = Operacoes.query.all()
        response = [{
            'id': i.id,
            'jurossimples': i.jurossimples,
            'capital': i.capital,
            'taxa': i.taxa,
            'tempo': i.tempo
        } for i in juros_simples]
        return response

    # J = C * i * t

    def post(self):
        dados = request.json
        # calcular o Juros
        if dados['capital'] and dados['taxa'] and dados['tempo'] > 0:
            juros_simples = Operacoes(
                id=dados['id'],
                jurossimples=dados['capital'] * (dados['taxa'] / 100) * dados['tempo'],
                capital=dados['capital'],
                taxa=dados['taxa'],
                tempo=dados['tempo']
            )
        # calcular a taxa
        if dados['jurossimples'] and dados['capital'] and dados['tempo'] > 0:
            juros_simples = Operacoes(
                id=dados['id'],
                jurossimples=dados['jurossimples'],
                capital=dados['capital'],
                taxa=dados['jurossimples'] / dados['capital'] * dados['tempo'],
                tempo=dados['tempo']
            )
        # calcular o capital
        if dados['jurossimples'] and dados['taxa'] and dados['tempo'] > 0:
            juros_simples = Operacoes(
                id=dados['id'],
                jurossimples=dados['jurossimples'],
                capital=dados['jurossimples'] / dados['tempo'] * (dados['taxa'] / 100),
                taxa=dados['taxa'],
                tempo=dados['tempo']
            )
        # calcular o tempo
        if dados['jurossimples'] and dados['capital'] and dados['taxa'] > 0:
            juros_simples = Operacoes(
                id=dados['id'],
                jurossimples=dados['jurossimples'],
                capital=dados['capital'],
                taxa=dados['taxa'],
                tempo=dados['jurossimples'] / dados['capital'] * (dados['taxa'] / 100)
            )
        juros_simples.save()
        response = {
            'id': juros_simples.id,
            'jurossimples': juros_simples.jurossimples,
            'capital': juros_simples.capital,
            'taxa': juros_simples.taxa,
            'tempo': juros_simples.tempo
        }
        return response


# calcular taxa nominal e taxa efetiva

class TaxaNominal(Resource):
    def get(self, taxanominal):
        taxa_nominal = OperacaoTaxaNominal.query.filter_by(taxanominal=taxanominal).first()
        try:
            response = {
                'taxanominal': taxa_nominal.taxa,
                'valor_emprestimo': taxa_nominal.valor_emprestimo,
                'valor_quitacao': taxa_nominal.valor_quitacao
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'Taxa não encontrada'
            }
        return response

    def put(self, taxanominal):
        taxa_nominal = OperacaoTaxaNominal.query.filter_by(taxanominal=taxanominal).first()
        dados = request.json
        if 'valor_emprestimo' in dados:
            taxa_nominal.valor_emprestimo = dados['valor_emprestimo']

        if 'valor_quitacao' in dados:
            taxa_nominal.valor_quitacao = dados['valor_quitacao']

        if 'taxa' in dados:
            taxa_nominal.taxa = dados['taxa']

        taxa_nominal.save()
        response = {
            'id': taxa_nominal.id,
            'valor_emprestimo': taxa_nominal.valor_emprestimo,
            'valor_quitacao': taxa_nominal.valor_quitacao,
            'taxa': taxa_nominal.taxa
        }

        return response

    def delete(self, taxanominal):
        taxa_nominal = OperacaoJuroComposto.query.filter_by(id=taxanominal).first()
        mensagem = 'Juros {} excluidos com sucesso'.format(taxa_nominal)
        taxa_nominal.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaTaxaNominal(Resource):

    def get(self):
        taxa_nominal = OperacaoTaxaNominal.query.all()
        response = [{
            'id': i.id,
            'valor_emprestimo': i.valor_emprestimo,
            'valor_quitacao': i.valor_quitacao,
            'taxa': i.taxa
        } for i in taxa_nominal]
        return response

    # taxa nominal = Juros (valor quitacao - valor emprestimo) / valor emprestimo

    def post(self):
        dados = request.json
        # calcular a taxa
        if dados['valor_emprestimo'] and dados['valor_quitacao'] > 0:
            taxa_nominal = OperacaoTaxaNominal(
                id=dados['id'],
                taxa=(dados['valor_quitacao'] - dados['valor_emprestimo']) / dados['valor_emprestimo'],
                valor_emprestimo=dados['valor_emprestimo'],
                valor_quitacao=dados['valor_quitacao']
            )
        # calcular o valor da quitação
        if dados['valor_emprestimo'] and dados['taxa'] > 0:
            taxa_nominal = OperacaoTaxaNominal(
                id=dados['id'],
                taxa=dados['taxa'],
                valor_emprestimo=dados['valor_emprestimo'],
                valor_quitacao=(dados['valor_emprestimo'] * dados['taxa']) + dados['valor_emprestimo']
            )
        # calcular o valor emprestimo
        # if dados['valor_emprestimo'] and dados['taxa'] > 0:
        #    juros_simples = Operacoes(
        #        id=dados['id'],
        #        taxa=dados['taxa'],
        #        valor_emprestimo=(dados['valor_quitacao'] * dados['taxa']) + dados['valor_emprestimo'],
        #        valor_quitacao=dados['valor_quitacao']
        #    )

        taxa_nominal.save()
        response = {
            'id': taxa_nominal.id,
            'valor_emprestimo': taxa_nominal.valor_emprestimo,
            'valor_quitacao': taxa_nominal.valor_quitacao,
            'taxa': taxa_nominal.taxa
        }
        return response


class TaxaEfetiva(Resource):
    def get(self, taxaefetiva):
        taxa_efetiva = OperacaoTaxaEfetiva.query.filter_by(taxaefetiva=taxaefetiva).first()
        try:
            response = {
                'taxa_efetiva': taxa_efetiva.taxa_efetiva,
                'taxa_nominal': taxa_efetiva.taxa_nominal,
                'quantidade_periodos': taxa_efetiva.quantidade_periodos
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'Taxa não encontrada'
            }
        return response

    def put(self, taxaefetiva):
        taxa_efetiva = OperacaoTaxaEfetiva.query.filter_by(taxaefetiva=taxaefetiva).first()
        dados = request.json
        if 'taxa_efetiva' in dados:
            taxa_efetiva.taxa_efetiva = dados['taxa_efetiva']

        if 'taxa_nominal' in dados:
            taxa_efetiva.taxa_nominal = dados['taxa_nominal']

        if 'quantidade_periodos' in dados:
            taxa_efetiva.quantidade_periodos = dados['quantidade_periodos']

        taxa_efetiva.save()
        response = {
            'id': taxa_efetiva.id,
            'taxa_efetiva': taxa_efetiva.taxa_efetiva,
            'taxa_nominal': taxa_efetiva.taxa_nominal,
            'quantidade_periodos': taxa_efetiva.quantidade_periodos
        }

        return response

    def delete(self, taxaefetiva):
        taxa_efetiva = OperacaoJuroComposto.query.filter_by(id=taxaefetiva).first()
        mensagem = 'Taxa efetiva {} excluida com sucesso'.format(taxa_efetiva)
        taxa_efetiva.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaTaxaEfetiva(Resource):

    def get(self):
        taxa_efetiva = OperacaoTaxaEfetiva.query.all()
        response = [{
            'id': i.id,
            'taxa_nominal': i.taxa_nominal,
            'taxa_efetiva': i.taxa_efetiva,
            'quantidade_periodos': i.quantidade_periodos
        } for i in taxa_efetiva]
        return response

    # Tendo em mente a taxa de juros declarada, utilize a seguinte fórmula: r = (1 + i/n)^n – 1, \\\
    # em que r é a taxa de juros efetiva, i, a nominal, e n, a quantidade de períodos compostos no período de um ano.
    def post(self):
        dados = request.json
        # calcular a taxa
        if dados['taxa_nominal'] and dados['quantidade_periodos'] > 0:
            taxa_efetiva = OperacaoTaxaEfetiva(
                id=dados['id'],
                taxa_efetiva=pow(1 + dados['taxa_nominal'] / dados['quantidade_periodos'],
                                 dados['quantidade_periodos']) - 1,
                taxa_nominal=dados['taxa_nominal'],
                quantidade_periodos=dados['quantidade_periodos']
            )

        taxa_efetiva.save()
        response = {
            'id': taxa_efetiva.id,
            'taxa_efetiva': taxa_efetiva.taxa_efetiva,
            'taxa_nominal': taxa_efetiva.taxa_nominal,
            'quantidade_periodos': taxa_efetiva.quantidade_periodos
        }
        return response


class TaxaJurosReal(Resource):
    def get(self, taxajurosreal):
        taxa_real = OperacaoTaxaEfetiva.query.filter_by(taxajurosreal=taxajurosreal).first()
        try:
            response = {
                'taxa_real': taxa_real.taxa_real,
                'taxa_nominal': taxa_real.taxa_nominal,
                'inflacao_periodo': taxa_real.inflacao_periodo
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'Taxa não encontrada'
            }
        return response

    def put(self, taxaefetiva):
        taxa_real = OperacaoTaxaEfetiva.query.filter_by(taxaefetiva=taxaefetiva).first()
        dados = request.json
        if 'taxa_real' in dados:
            taxa_real.taxa_real = dados['taxa_real']

        if 'taxa_nominal' in dados:
            taxa_real.taxa_nominal = dados['taxa_nominal']

        if 'inflacao_periodo' in dados:
            taxa_real.inflacao_periodo = dados['inflacao_periodo']

        taxa_real.save()
        response = {
            'id': taxa_real.id,
            'taxa_efetiva': taxa_real.taxa_real,
            'taxa_nominal': taxa_real.taxa_nominal,
            'quantidade_periodos': taxa_real.inflacao_periodo
        }

        return response

    def delete(self, taxareal):
        taxa_real = OperacaoJuroComposto.query.filter_by(id=taxareal).first()
        mensagem = 'Taxa efetiva {} excluida com sucesso'.format(taxa_real)
        taxa_real.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaTaxaReal(Resource):

    def get(self):
        taxa_real = OperacaoTaxaJurosReal.query.all()
        response = [{
            'id': i.id,
            'taxa_nominal': i.taxa_nominal,
            'taxa_real': i.taxa_real,
            'inflacao_periodo': i.inflacao_periodo
        } for i in taxa_real]
        return response

    # taxa de juros real
    # (1 + in) = (1 + r) × (1 + j)
    # in: taxa de juros nominal
    # r: taxa de juros real
    # j: inflação do período.
    def post(self):
        dados = request.json
        # calcular a taxa
        if dados['taxa_nominal'] and dados['inflacao_periodo'] > 0:
            taxa_real = OperacaoTaxaJurosReal(
                id=dados['id'],
                taxa_real=(1 + dados['taxa_nominal']) / (1 + dados['inflacao_periodo']) - 1,
                taxa_nominal=dados['taxa_nominal'],
                inflacao_periodo=dados['inflacao_periodo']
            )

        taxa_real.save()
        response = {
            'id': taxa_real.id,
            'taxa_real': taxa_real.taxa_real,
            'taxa_nominal': taxa_real.taxa_nominal,
            'inflacao_periodo': taxa_real.inflacao_periodo
        }
        return response


class FormacaoCapital(Resource):
    def get(self, fatoracumulado):
        fator_acumulado = FatorAcumulacaoCapital.query.filter_by(fatoracumulado=fatoracumulado).first()
        try:
            response = {
                'fator_acumulado': fator_acumulado.fator_acumulado,
                'taxa': fator_acumulado.taxa,
                'tempo': fator_acumulado.tempo,
                'montante_composto': fator_acumulado.montante_composto
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'fator acumulado não encontrada'
            }
        return response

    def put(self, fatoracumulado):
        fator_acumulado = FatorAcumulacaoCapital.query.filter_by(fatoracumulado=fatoracumulado).first()
        dados = request.json
        if 'fator_acumulado' in dados:
            fator_acumulado.fator_acumulado = dados['fator_acumulado']

        if 'taxa' in dados:
            fator_acumulado.taxa = dados['taxa']

        if 'tempo' in dados:
            fator_acumulado.tempo = dados['tempo']

        if 'montante_composto' in dados:
            fator_acumulado.montante_composto = dados['montante_composto']

        fator_acumulado.save()
        response = {
            'id': fator_acumulado.id,
            'fator_acumulado': fator_acumulado.fator_acumulado,
            'taxa': fator_acumulado.taxa,
            'tempo': fator_acumulado.tempo,
            'montante_composto': fator_acumulado.montante_composto
        }

        return response

    def delete(self, fatoracumulado):
        fator_acumulado = OperacaoJuroComposto.query.filter_by(id=fatoracumulado).first()
        mensagem = 'fator acumulado {} excluido com sucesso'.format(fator_acumulado)
        fator_acumulado.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaFormacaoCapital(Resource):

    def get(self):
        fator_acumulado = FatorAcumulacaoCapital.query.all()
        response = [{
            'id': i.id,
            'fator_acumulado': i.fator_acumulado,
            'taxa': i.taxa,
            'tempo': i.tempo,
            'montante_composto': i.montante_composto
        } for i in fator_acumulado]
        return response

    # P=S(1+i)**−n
    # S = montante composto
    def post(self):
        dados = request.json
        if dados['taxa'] and dados['tempo'] > 0:
            fator_acumulado = FatorAcumulacaoCapital(
                id=dados['id'],
                fator_acumulado=(1 + dados['montante_composto']) / (1 + dados['inflacao_periodo']) - 1,
                taxa=dados['taxa_nominal'],
                tempo=dados['inflacao_periodo'],
                montante_composto=dados['montante_composto']
            )

        fator_acumulado.save()
        response = {
            'id': fator_acumulado.id,
            'fator_acumulado': fator_acumulado.fator_acumulado,
            'taxa': fator_acumulado.taxa,
            'tempo': fator_acumulado.tempo,
            'montante_composto': fator_acumulado.montante_composto
        }
        return response


class CalculoDescSimples(Resource):
    def get(self, descontosimples):
        desconto_simples = DescontoSimples.query.filter_by(descontosimples=descontosimples).first()
        try:
            response = {
                'desconto_simples': desconto_simples.desconto_simples,
                'montante': desconto_simples.montante,
                'taxa': desconto_simples.taxa,
                'tempo': desconto_simples.tempo,
                'valor_atual': desconto_simples.valor_atual
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'fator acumulado não encontrada'
            }
        return response

    def put(self, descontosimples):
        desconto_simples = DescontoSimples.query.filter_by(descontosimples=descontosimples).first()
        dados = request.json
        if 'desconto_simples' in dados:
            desconto_simples.desconto_simples = dados['desconto_simples']

        if 'montante' in dados:
            desconto_simples.montante = dados['montante']

        if 'taxa' in dados:
            desconto_simples.taxa = dados['taxa']

        if 'tempo' in dados:
            desconto_simples.tempo = dados['tempo']

        if 'valor_atual' in dados:
            desconto_simples.valor_atual = dados['valor_atual']

        desconto_simples.save()
        response = {
            'id': desconto_simples.id,
            'desconto_simples': desconto_simples.desconto_simples,
            'montante': desconto_simples.montante,
            'taxa': desconto_simples.taxa,
            'tempo': desconto_simples.tempo,
            'valor_atual': desconto_simples.valor_atual
        }

        return response

    def delete(self, descontosimples):
        desconto_simples = DescontoSimples.query.filter_by(id=descontosimples).first()
        mensagem = 'fator acumulado {} excluido com sucesso'.format(desconto_simples)
        desconto_simples.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaDescontoSimples(Resource):

    def get(self):
        desconto_simples = DescontoSimples.query.all()
        response = [{
            'id': i.id,
            'desconto_simples': i.desconto_simples,
            'montante': i.montante,
            'taxa': i.taxa,
            'tempo': i.tempo,
            'valor_atual': i.valor_atual
        } for i in desconto_simples]
        return response

    # Dr = A . i . t          A = N / (1 + i.t)
    #
    # Onde:
    #
    # Dr = desconto racional
    #
    # N = valor nominal
    #
    # i = taxa
    #
    # t = tempo
    #
    # A = valor atual
    def post(self):
        dados = request.json
        if dados['taxa'] and dados['tempo'] and dados['montante'] > 0:
            desconto_simples = DescontoSimples(
                id=dados['id'],
                desconto_simples=(dados['montante'] * (dados['taxa'] / 100) * dados['tempo']),
                montante=dados['montante'],
                taxa=dados['taxa'],
                tempo=dados['tempo'],
                valor_atual=dados['montante'] / (1 + (dados['taxa'] / 100) * dados['tempo'])
            )

        desconto_simples.save()
        response = {
            'id': desconto_simples.id,
            'desconto_simples': desconto_simples.desconto_simples,
            'montante': desconto_simples.montante,
            'taxa': desconto_simples.taxa,
            'tempo': desconto_simples.tempo,
            'valor_atual': desconto_simples.valor_atual
        }
        return response


class CalculoDescComposto(Resource):
    def get(self, descontocomposto):
        desconto_composto = DescontoComposto.query.filter_by(descontocomposto=descontocomposto).first()
        try:
            response = {
                'desconto_composto': desconto_composto.desconto_composto,
                'montante': desconto_composto.montante,
                'taxa': desconto_composto.taxa,
                'tempo': desconto_composto.tempo,
                'valor_atual': desconto_composto.valor_atual
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'fator acumulado não encontrada'
            }
        return response

    def put(self, descontocomposto):
        desconto_composto = DescontoComposto.query.filter_by(descontocomposto=descontocomposto).first()
        dados = request.json
        if 'desconto_composto' in dados:
            desconto_composto.desconto_composto = dados['desconto_composto']

        if 'montante' in dados:
            desconto_composto.montante = dados['montante']

        if 'taxa' in dados:
            desconto_composto.taxa = dados['taxa']

        if 'tempo' in dados:
            desconto_composto.tempo = dados['tempo']

        if 'valor_atual' in dados:
            desconto_composto.valor_atual = dados['valor_atual']

        desconto_composto.save()
        response = {
            'id': desconto_composto.id,
            'desconto_composto': desconto_composto.desconto_simples,
            'montante': desconto_composto.montante,
            'taxa': desconto_composto.taxa,
            'tempo': desconto_composto.tempo,
            'valor_atual': desconto_composto.valor_atual
        }

        return response

    def delete(self, descontocomposto):
        desconto_composto = DescontoComposto.query.filter_by(id=descontocomposto).first()
        mensagem = 'fator acumulado {} excluido com sucesso'.format(desconto_composto)
        desconto_composto.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaDescontoComposto(Resource):

    def get(self):
        desconto_composto = DescontoComposto.query.all()
        response = [{
            'id': i.id,
            'desconto_composto': i.desconto_composto,
            'montante': i.montante,
            'taxa': i.taxa,
            'tempo': i.tempo,
            'valor_atual': i.valor_atual
        } for i in desconto_composto]
        return response

    # DC = N . i . t        A = N . (1 – i)**t

    def post(self):
        dados = request.json
        if dados['taxa'] and dados['tempo'] and dados['montante'] > 0:
            desconto_composto = DescontoComposto(
                id=dados['id'],
                desconto_composto=dados['montante'] - (
                            dados['montante'] * (pow(1 - (dados['taxa'] / 100), dados['tempo']))),
                montante=dados['montante'],
                taxa=dados['taxa'],
                tempo=dados['tempo'],
                valor_atual=dados['montante'] * pow(1 - (dados['taxa'] / 100), dados['tempo'])
            )

        desconto_composto.save()
        response = {
            'id': desconto_composto.id,
            'desconto_composto': desconto_composto.desconto_composto,
            'montante': desconto_composto.montante,
            'taxa': desconto_composto.taxa,
            'tempo': desconto_composto.tempo,
            'valor_atual': desconto_composto.valor_atual
        }
        return response


class CalculoPrestacaoConstante(Resource):
    def get(self, prestacaoconstante):
        prestacao_constante = DescontoComposto.query.filter_by(prestacaoconstante=prestacaoconstante).first()
        try:
            response = {
                'saldo_devedor': prestacao_constante.saldo_devedor,
                'amortizacao': prestacao_constante.amortizacao,
                'taxa': prestacao_constante.taxa,
                'tempo': prestacao_constante.tempo,
                'prestacao': prestacao_constante.valor_atual
            }
        except AttributeError:
            response = {
                'status': 'error',
                'message': 'fator acumulado não encontrada'
            }
        return response

    def put(self, prestacaoconstante):
        prestacao_constante = SistemaPrestacaoConstante.query.filter_by(prestacaoconstante=prestacaoconstante).first()
        dados = request.json
        if 'saldo_devedor' in dados:
            prestacao_constante.saldo_devedor = dados['saldo_devedor']

        if 'amortizacao' in dados:
            prestacao_constante.amortizacao = dados['amortizacao']

        if 'taxa' in dados:
            prestacao_constante.taxa = dados['taxa']

        if 'tempo' in dados:
            prestacao_constante.tempo = dados['tempo']

        if 'prestacao' in dados:
            prestacao_constante.prestacao = dados['prestacao']

        prestacao_constante.save()
        response = {
            'id': prestacao_constante.id,
            'saldo_devedor': prestacao_constante.saldo_devedor,
            'amortizacao': prestacao_constante.amortizacao,
            'taxa': prestacao_constante.taxa,
            'tempo': prestacao_constante.tempo,
            'prestacao': prestacao_constante.prestacao
        }

        return response

    def delete(self, prestacaoconstante):
        prestacao_constante = SistemaPrestacaoConstante.query.filter_by(id=prestacaoconstante).first()
        mensagem = 'fator acumulado {} excluido com sucesso'.format(prestacao_constante)
        prestacao_constante.delete()
        return {'status': 'sucesso', 'mensagem': mensagem}


class ListaPrestacaoConstante(Resource):

    def get(self):
        prestacao_constante = SistemaPrestacaoConstante.query.all()
        response = [{
            'id': i.id,
            'saldo_devedor': i.saldo_devedor,
            'amortizacao': i.amortizacao,
            'taxa': i.taxa,
            'tempo': i.tempo,
            'prestacao': i.prestacao
        } for i in prestacao_constante]
        return response

    def post(self):
        dados = request.json
        if dados['taxa'] and dados['tempo'] and dados['saldo_devedor'] > 0:
            prestacao_constante = SistemaPrestacaoConstante(
                id=dados['id'],
                saldo_devedor=dados['saldo_devedor'],
                amortizacao=dados['saldo_devedor'] / dados['tempo'],
                taxa=dados['taxa'],
                tempo=dados['tempo'],
                prestacao=(dados['saldo_devedor'] / dados['tempo']) + (dados['taxa']/100 * dados['saldo_devedor'])
            )

        prestacao_constante.save()
        response = {
            'id': prestacao_constante.id,
            'saldo_devedor': prestacao_constante.saldo_devedor,
            'amortizacao': prestacao_constante.amortizacao,
            'taxa': prestacao_constante.taxa,
            'tempo': prestacao_constante.tempo,
            'prestacao': prestacao_constante.prestacao
        }
        return response


api.add_resource(JuroComposto, '/jurocomposto/<int:juroscompostos>/')
api.add_resource(ListaJurosCompostos, '/listajuroscompostos/')
api.add_resource(Operacao, '/jurosimples/<int:id>/')
api.add_resource(ListaOperacoes, '/listajurossimples/')
api.add_resource(TaxaNominal, '/taxanominal/<int:id>/')
api.add_resource(ListaTaxaNominal, '/listataxanominal/')
api.add_resource(TaxaEfetiva, '/taxaefetiva/<int:id>/')
api.add_resource(ListaTaxaEfetiva, '/listataxaefetiva/')
api.add_resource(TaxaJurosReal, '/taxareal/<int:id>/')
api.add_resource(ListaTaxaReal, '/listataxareal/')
api.add_resource(FormacaoCapital, '/formacaocapitalac/<int:id>/')
api.add_resource(ListaFormacaoCapital, '/listaformacaocapitalac/')
api.add_resource(CalculoDescSimples, '/descontosimples/<int:id>/')
api.add_resource(ListaDescontoSimples, '/listadescontosimples/')
api.add_resource(CalculoDescComposto, '/descontocomposto/<int:descontocomposto>/')
api.add_resource(ListaDescontoComposto, '/listadescontocomposto/')
api.add_resource(CalculoPrestacaoConstante, '/prestacaoconstante/<int:prestacaoconstante>/')
api.add_resource(ListaPrestacaoConstante, '/listaprestacaoconstante/')

if __name__ == '__main__':
    app.run(debug=True)
