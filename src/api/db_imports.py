import sqlite3
import json

def get_agendamento(id):
    try:
        agendamento = dict()
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()

        sql = f"""
            SELECT * FROM detranrj_refor_praticos_agendados WHERE id == {id};
        """

        query = cursor.execute(sql)
        for row in query:
            agendamento = {'id': row[0], 'detranrj_refor_praticos_id': row[1],'data': row[2],
                            'hora': row[3], 'local': row[4],'protocolo': row[5], 'tentativas': row[6],
                           'sucesso': row[7],'cancelado': row[8], 'cadastro': row[9] }  
        conn.close()
        if agendamento == {}:
            return {
                  "agendamento": f"Não a nada agendado com o id:{id}",
                  "sucesso": False }
        else:
            return { 
                 "agendamento": agendamento,
                 "sucesso": True}

    except Exception as erro: 
        print(f'Error ao consultar banco: {erro}')




def get_banco(id, renach=None):
    try:
        agendamento = dict()
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()
        if renach is None:
            sql = f"""
            SELECT * FROM detranrj_refor_praticos WHERE id = '{id}';
            """

        else:
            sql = f"""
        SELECT * FROM detranrj_refor_praticos WHERE id = '{id}' and protocolos like '%{renach}%';
    """

        query = cursor.execute(sql)
        for row in query:
            agendamento = {'id': row[0], 'pid': row[1],'caer': row[2], 'usuarios': row[3], 'senhas': row[4],
                        'categoria': row[5], 'veiculo': row[6], 'tentativas': row[7],'locais': row[8],
                        'datas': row[9], 'horarios': row[10], 'protocolos': row[11], 'sucesso': row[12], 'cancelado': row[13],
                        'cadastrado': row[14], 'webhook': row[15], 'log': row[16]} 

        conn.close()
        return agendamento
    
    except Exception as erro: 
        print(f'Error ao consultar banco: {erro}')



def get_Alljobs(data, caer=None):
    try:
        agendamento = list()
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()

        if caer is not None:
            sql = f"""
                    SELECT * FROM detranrj_refor_praticos WHERE datas like '%{data}%' and caer = '{caer}';
                    """

        else:
            sql = f"""
                    SELECT * FROM detranrj_refor_praticos WHERE datas like '%{data}%'
                        """
        query = cursor.execute(sql)
        for row in query:
            agendamento.append({'id': row[0], 'pid': row[1],'caer': row[2], 'usuarios': row[3], 'senhas': row[4],
                        'categoria': row[5], 'veiculo': row[6], 'tentativas': row[7],'locais': row[8],
                        'datas': row[9], 'horarios': row[10], 'protocolos': row[11], 'sucesso': row[12], 'cancelado': row[13],
                        'cadastrado': row[14], 'webhook': row[15], 'log': row[16]}) 

        conn.close()
        return agendamento

    except Exception as erro: 
        print(f'Error ao consultar banco: {erro}')



def send_banco(content):
    try:
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()
        
        sql = f'''INSERT INTO detranrj_refor_praticos (caer, usuarios, senhas, veiculo, categoria,
            tentativas, sucesso, cancelado, cadastro, locais, datas, horarios, protocolos) 
            VALUES ('{content.get('caer')}', '{json.dumps(content.get('usuarios'))}', '{json.dumps(content.get('senhas'))}', '{content.get('veiculo')}',
                    '{content.get('categoria')}', '{content.get('tentativas')}', '{content.get('sucesso')}', '{content.get('cancelado')}',
                    '{content.get('cadastro')}', '{json.dumps(content.get('locais'))}', '{json.dumps(content.get('datas'))}',
                    '{json.dumps(content.get('horarios'))}', '{json.dumps(content.get('protocolos'))}');'''
        cursor.execute(sql)
        id = cursor.lastrowid

        conn.commit()
        conn.close()
        return id 
    except Exception as erro: 
        print(f'Error ao consultar banco: {erro}')


def update_pid(pid, id):
    try:
        print(f'pid: {pid}, id: {id}')
        conn = sqlite3.connect('detran-services.s3db')

        cursor = conn.cursor()

        sql = f'''UPDATE detranrj_refor_praticos 
                    SET pid = {pid} 
                    WHERE id = {id};'''

        cursor.execute(sql)
        conn.commit()
        conn.close()
    except Exception as erro: 
        print(f'Error ao consultar banco: {erro}')



def get_argumentos(id):
    try:
        agendamento = dict()
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()

        sql = f"""
        SELECT * FROM parametros_execucao WHERE id = {id};
        """       
        print(sql)
        query = cursor.execute(sql)
        for row in query:
            agendamento = {'id': row[0], 'parametros': row[1]}

        conn.close()
        return agendamento
    
    except Exception as erro: 
        print(f'Error ao consultar banco: {erro}')


def send_argumentos(content:dict):
    try:
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()
        
        sql = f'''INSERT INTO parametros_execucao (argumentos) 
            VALUES ('{json.dumps(content)}');'''

        cursor.execute(sql)
        id = cursor.lastrowid

        conn.commit()
        conn.close()
        return id 
    except Exception as erro: 
        print(f'Error ao consultar banco: {erro}')




