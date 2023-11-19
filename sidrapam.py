# ****** NOTA IMPORTANTE
# Nas primeiras semanas de Maio, o IBGE alterou a certificação de segurança de acesso ao SIDRA e com isso, 
# o uso do sidrapyficou bastante prejudicado. Atualmente o desenvolvedor do sidrapy - Alan Taranti, 
# colocou algumas modificações no código para resolver temporariamente o problema, porém, para não 
# atrapalhar as aulas, criei essa solução simples para os exercícios de extração de dados do SIDRA
# use com cautela.
#
# Extração de dados do SIDRA
# Este arquivo python é usado como material de referência para obter quantitativos de produção de uma cultura 
# (exemplo: café) em uma cidade (exemplo: Garça SP). Veja notebooks de exemplo
#
# ALB @ UFF 2023
# este script extrai dados da tabela 5457 do SIDRA com base nos códigos de produtos e de cidades, passados como argumentos

import ssl
import requests
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        #ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.check_hostname = False
        ctx.set_ciphers("AES128-SHA256")
        #ctx.options |= 0x4   # <-- the key part here, OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def get_pam(municipios,cod_municipios,produtos,cod_produtos,**kwargs):
    '''
    Esta função extrai do SIDRA os valores de área plantada, área colhida, quantidade colhida e rendimento
    de produtos e cidades da tabela 5457 de lavouras permanentes e temporárias do PAM - SIDRA - IBGE
    Você deve entrar com os dados na forma de um array. Por exemplo:

            municipios = ['Altinópolis','Batatais','Cajuru']
            codigos_mun = ['3501004','3505906','3509403']

            produtos = ['Café (em grão) Total']
            codigos_prod = ['40139']

            get_pam(municipios,codigos_mun,produtos,codigos_prod)

    Nos argumentos, se verbose=True, algumas informações serão mostradas.
    '''
    verbose = kwargs.get('verbose',False)

    producao_mun = pd.DataFrame()
    data = pd.DataFrame()

    for jj,cod_mun in enumerate(cod_municipios):
        for ii,cod_produto in enumerate(cod_produtos):
            if verbose:
                print(f'Município {cod_mun} cultura {cod_produto}')

            sidraurl = 'https://sidra.ibge.gov.br/geratabela?format=xlsx&name=tabela5457.xlsx&terr=N&rank=-&query=t/5457/n6/' \
                    + cod_mun +'/v/8331,216,214,112/p/all/c782/' \
                    + cod_produto +'/l/c782%2Bt,,p%2Bv'
            with requests.session() as s:
                s.mount("https://", TLSAdapter())
                rawdata = None
                while rawdata is None:
                    try:
                        rawdata = pd.read_excel(s.get(sidraurl, verify=False).content, skiprows=4, header=None)
                    except Exception as e:
                        print(f'Erro ao baixar dados para {cod_produto}: {e}')

            rawdata = rawdata.iloc[:-1,:] # limpa a última linha

            extract = []
            for i in range(0, len(rawdata), 4):
                ano = rawdata.iloc[i,0]
                aplan = rawdata.iloc[i, 2]
                acolh = rawdata.iloc[i+1, 2]
                qtdecol = rawdata.iloc[i+2, 2]
                rend = rawdata.iloc[i+3, 2]
                extract.append({'Ano':ano,'A.Plantada':aplan,'A.Colhida':acolh,
                            'QtdeColhida':qtdecol,'Rendimento':rend})
                
            data = pd.DataFrame(extract)
            data['Ano'] = pd.to_numeric(data.loc[:,'Ano'], errors='coerce', downcast='integer')
            data['A.Plantada'] = pd.to_numeric(data.loc[:,'A.Plantada'], errors='coerce')
            data['A.Colhida'] = pd.to_numeric(data.loc[:,'A.Colhida'], errors='coerce')
            data['QtdeColhida'] = pd.to_numeric(data.loc[:,'QtdeColhida'], errors='coerce')
            data['Rendimento'] = pd.to_numeric(data.loc[:,'Rendimento'], errors='coerce')            

            data['Produto'] = produtos[ii]
            data['Cod.Produto'] = cod_produto
            data['Municipio'] = municipios[jj]
            data['Cod.Municipio'] = cod_mun

            producao_mun = pd.concat([producao_mun,data],ignore_index=True)

    return producao_mun
    
