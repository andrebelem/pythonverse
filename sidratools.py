# ****** NOTA IMPORTANTE
# Nas primeiras semanas de Maio, o IBGE alterou a certificação de segurança de acesso ao SIDRA e com isso, 
# o uso do sidrapyficou bastante prejudicado. Atualmente o desenvolvedor do sidrapy - Alan Taranti, 
# colocou algumas modificações no código para resolver temporariamente o problema, porém, para não 
# atrapalhar as aulas, criei essa solução simples para os exercícios de extração de dados do SIDRA
# use com cautela.
#
# Extração de dados do SIDRA
# Este arquivo python é usado como material de referência para obter quantitativos de produção de uma cultura 
# (exemplo: café) em uma cidade (exemplo: Garça SP). Veja o notebook de exemplo sidra_extract.ipynb.
#
# ALB @ UFF 2022

# importa o que é necessário para trabalhar aqui 
import pandas as pd
import requests
import warnings
warnings.filterwarnings('ignore')


def SIDRA2pandas(cod_mun,cod_cultura):
    ''' (1) obter dados para a cultura (veja aqui http://api.sidra.ibge.gov.br/desctabapi.aspx?c=5457). 
        por exemplo, Café é a cultura 40139
        (2) obter o código da cidade (no nosso exemplo, Garça SP é 3516705) 
        (3) usar o código para baixar os dados de produção na cidade. Note que na API, o nível de cidade é N6 (veja aqui)
        e os códigos das cidades pode ser baixado aqui 
        http://api.sidra.ibge.gov.br/desctabapi.aspx?c=5457.
        Este código só funciona para a tabela 5457
        '''
    vars = ['8331','216','214','112']
    vars_names = ['A.plantada','A.colhida','Q.colhida','Rendimento']

    data = pd.DataFrame()

    for ii,var in enumerate(vars):
        sidraurl = 'https://sidra.ibge.gov.br/geratabela?format=xlsx&name=tabela5457.xlsx&terr=N&rank=-&query=t/5457/n6/'+cod_mun+'/v/'+var+'/p/all/c782/'+cod_cultura+'/l/c782%2Bt,,p%2Bv'
        iodata = requests.get(sidraurl,verify=False)
        rawdata = pd.read_excel(iodata.content,skiprows=4,header=None)
        if ii==0:
            data['Ano'] = rawdata.iloc[:,0]

        data[vars_names[ii]] = rawdata.iloc[:,2]

    # e por último elimina a última linha
    data = data.iloc[:-1 , :]
    data2 = data.apply(pd.to_numeric, errors='coerce') # converte tudo para numeros
    data2.Ano = pd.to_datetime(data2.Ano, format='%Y') # e aproveita e converte o ano para uma data
    
    return data2
