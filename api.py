import psutil
from flask import Flask, request
from main import main
from src.crawlers.verify_pratical_exam_category import verify_pratical_exame
from src.crawlers.set_pratical_exam import set_pratical_exam
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
        content = get_content_json(["caer", "usuarios", "senhas", "veiculo", "categoria", "tentativas", "horarios", "locais", "datas", "protocolos", "sucesso", "cancelado", "cadastro"])
        content['datas'] = convert_date(content['datas'])
        content['id'] = send_banco(content)
        main(set_pratical_exam, content)

        return {
            "sucesso" : True,
            "agendamentos" : content
            }

    except Exception as e: 
        print(e)
    except:
        return error() 

@app.route('/rj/jobpratica/', methods=['GET']) 
#//FILTRO POR DATA // CAER SEM FILTRO RETORNA TUDO
def get_jobpratica():
    try:
        content = get_content_args(["data", "caer"])
        content['data'] =  convert_date([content['data']])[0]
        responseJson = get_Alljobs(data =content.get('data'), caer=content.get("caer"))
        
        return {
            "agendamento": responseJson,
            "sucesso": True
        }
    except:
        return error()


@app.route('/rj/provapratica/<id>', methods=['GET'])
def get_marcacao(id):
    responseJson = get_agendamento(id)
    
    try:
        return {
            "agendamento" : responseJson
        }
    except:
        return error() 

#### pegar renach e id_pratics 
#### cancela so agendamento
@app.route('/rj/provapratica/<id>', methods=['DELETE'])
def deleta_marcacao(id):
    ## deletar aluno da marcacao
    responseJson = get_banco(id)
    main(verify_pratical_exame, responseJson)

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
        childrens = killtree(pid)

        return {
                "process": childrens,
                "method": "kill",
                "sucesso": True
                }
    except:
        return error() 

################### UTILS ####################### 
#### https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output
def killtree(pid, including_parent=True):
    parent = psutil.Process(pid)
    childrens = list()
    try:
        for child in parent.children(recursive=True):
            childrens.append(f"child: {str(child)}")
            child.kill()
    except (psutil.NoSuchProcess):
        pass

    if including_parent:
        parent.kill()

    return childrens


def convert_date(datas):
    datas_list = list()
    for data in datas:
        data_split = data.split('-')
        y, m, d = data_split[0], data_split[1], data_split[2]
        data = f'{d}/{m}/{y}'
        datas_list.append(data)
    return datas_list

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
