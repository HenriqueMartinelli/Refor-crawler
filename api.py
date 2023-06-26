import psutil
import subprocess
from subprocess import PIPE
from flask import Flask, request
from src.api.db_imports import *

app = Flask(__name__)

@app.route("/")
def padrao():
    return "<h1>Funcionando<h1>"
    # return '<select id="CDYN_53" name="CC" data-testtoolid="cmbCAER" size="1" class="COMBOFIXSelectEdit" style="width:400px;" tabindex="1"><option value="RJ47990">RJ47990 - CFC PRINCESA LTDA</option><option value="RJ61810">RJ61810 - CFC PRINCESA LTDA</option></select>' 


## percorre e se for horario inicia, verifica a cada segundo
@app.route('/rj/agendamentos', methods=['POST'])
def get_agendamentos():
    try:
        content = get_content_json(["caer", "usuarios", "senhas", "veiculo", "categoria", "tentativas", "horarios", "locais", "datas", "protocolos"])
        result_convert = convert_data(content['datas'], content['locais'])
        content['datas'], content['locais'] = result_convert[0], result_convert[1]
        content['crawler'] = 'set_pratical_exam'
        content['id'] = send_banco(content)
        id_argumentos = send_argumentos(content)

        run_work(id_argumentos=id_argumentos, id_robo=content['id'])

        return {
            "sucesso" : True,
            "agendamentos" : content
            }

    except Exception as erro: 
        print(f"Algo está errado: {erro}")
    except:
        return error() 


@app.route('/rj/jobpratica/', methods=['GET']) 
#//FILTRO POR DATA // CAER SEM FILTRO RETORNA TUDO
def get_jobpratica():
    try:
        content = get_content_args(["data", "caer"])
        result_convert = convert_data(content['datas'], localizacoes=None)
        content['data'] =  result_convert[0]
        responseJson = get_Alljobs(data =content.get('data'), caer=content.get("caer"))
        
        return {
            "agendamento": responseJson,
            "sucesso": True
        }
    except:
        return error()


@app.route('/rj/provapratica/<id>', methods=['GET'])
def get_marcacao(id):
    try:
        responseJson = get_agendamento(id)
        return responseJson
    except:
        return error() 


@app.route('/rj/provapratica/', methods=['DELETE'])
def deleta_marcacao():
    ## deletar aluno da marcacao
    content = get_content_args(["id", "renach"])
    responseJson = get_banco(id=content['id'], renach=content['renach'])
    id_argumentos = send_argumentos(responseJson)
    responseJson['crawler'] = 'verify_pratical_exame'

    id_argumentos = send_argumentos(responseJson)
    run_work(id_argumentos=id_argumentos, id_robo=responseJson['id'])

    try:
        return {
            "agendamento" : responseJson
        }
    except:
        return error() 


@app.route('/rj/jobpratica/<id>', methods=['DELETE'])
#REMOVE DA FILA O JOB DE MARCAÇÃO DE PROVA
def remove_job(id):
    try:
        responseJson = get_banco(id)
        pid = responseJson.get('pid')
        killtree(pid)

        return {
                "sucesso": True
                }
    except:
        return error() 


################### UTILS ####################### 
#### 

def run_work(id_argumentos, id_robo):
    
    id_encoded = str(id_argumentos)
    process = subprocess.Popen([f"python3 main.py {id_encoded} >> {id_encoded}.log 2>> {id_encoded}.log"], shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    pid = process.pid
    return update_pid(id=id_robo, pid=pid)



def killtree(pid, including_parent=True):
    parent = psutil.Process(pid)
    childrens = list()
    try:
        for child in parent.children(recursive=True):
            childrens.append(f"child: {str(child)}")
            child.kill()

        if including_parent:
            parent.kill()
    except (psutil.NoSuchProcess):
        pass

    return childrens


def convert_data(datas, localizacoes):
    datas_list = list()
    localizacao_list = list()
    for data in datas:
        data_split = data.split('-')
        y, m, d = data_split[0], data_split[1], data_split[2]
        data = f'{d}/{m}/{y}'
        datas_list.append(data)
    
    if localizacoes is None:
        return datas_list

    for localizacao in localizacoes:
        local = localizacao.encode("latin1").decode("unicode_escape")
        localizacao_list.append(local)
    return [datas_list, localizacao_list]


def get_content_args(required_fields):
    content = request.args
    content = content.to_dict()
    if not content.get('caer'):
        content.update({'caer': None})

    validate_content(content, required_fields)
    return content


def get_content_json(required_fields):
    content = request.json
    validate_content(content, required_fields)
    return content


def validate_content(content, required_fields):
    for field in required_fields:
        if field not in content:
            print(f"Requisição inválida; Campo: {field} não está no agendamento")
            raise ("Requisição inválida.")


def error(msg="Erro desconhecido ao processar requisição."):
    return {
        "sucesso" : False,
        "msg": msg
    }


def invalid_request():
    return error("Requisição inválida.")


def ok():
    return {
        "sucesso" : True
    }
