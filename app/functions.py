import requests
import json
import time 

def monday_request(query):
    token = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQ5MTU0MDEyOSwiYWFpIjoxMSwidWlkIjo3NDAxNTYzNCwiaWFkIjoiMjAyNS0wMy0yN1QwODo0OTowOS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjY0MzQxODcsInJnbiI6ImV1YzEifQ.wtmLhuMPG6YntJW8BYk_MOrte0_ObWrTcZdLyAY4duE"
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization" : token, "API-Version" : "2023-10"}
    data = {"query" : query}
    #print(f"query en monday_request = {query}")
    r = requests.post(url=apiUrl, json=data, headers=headers)
    # print(f"r en monday_request = {r}")

    # print(f"resultado consulta en monday_request = {r.json()}")
    if "errors" in r.json():
        try:
            print(f"entro en error_code")
            # int(error_message.split()[-2]) + 1
            if r.json()["error_code"] == 'ComplexityException':
                print(f"entro en complexity error")
                seconds_to_wait = int(r.json()["errors"][0].split()[-2])+1
                print(f"Complexity budget exhausted, waiting {seconds_to_wait}seg")
                
                time.sleep(seconds_to_wait+1)
                # print(f"query en return Complexity budget exhausted = {query}")
                return monday_request(query,token)
            else:
                print(f"ERROR EN MONDAY REQUEST = {r.json()}")
                return f"ERROR{r.json()}"
            
            
        except:
            print(f"ERROR EN MONDAY REQUEST = {r.json()}")
            return f"ERROR{r.json()}"
    # print(f"r.json() despues condiciones errores= {r.json()}")
    
    return r.json()

def read_main_item(item_id):
    query_lectura = '''
        query {
        items (ids: %s) {
            name
            column_values{
            id
            type
                    text
            column{
                title
            }
            ... on BoardRelationValue{
                
                linked_items{
                name
                id
                }
                linked_item_ids
            }
            }
        }
        }
        '''%(item_id)

    response = monday_request(query_lectura)

    print(f"response = {json.dumps(response, indent=2)}")
    
    ids_items_linked = {}
    column_ids = {}
    items = response["data"]["items"]


    # print(f"items: {items}")

    for item in items:
        column_values = item["column_values"]
        # print(f"column_values: {column_values}")
        
        for column in column_values:
            title = column["column"]["title"]
            col_id = column["id"]
            if title in ['Email Clientes', 'Email Comercial']:
                column_ids[title] = col_id
            if column["type"] == "board_relation":
                # print(f"column: {column}")
                column_title = column["column"]["title"]
                linked_ids = column["linked_item_ids"]
                
                if linked_ids:
                    ids_items_linked[column_title] = linked_ids[0]
                    
                    
    return column_ids, ids_items_linked



def get_email_values(ids_items_linked):
    
    emails = {}
    valores = []

    for title, item_id in ids_items_linked.items():
        query = '''
        query {
        items (ids: %s) {
            name
            column_values{
            id
            type
            text
            column{
                title
            }
            ... on EmailValue{
                text
                email
            }
            }
        }
        }
        '''%(item_id)
        
        response = monday_request(query)
        
        # print(f"response = {json.dumps(response, indent=2)}")
        
        items = response["data"]["items"]
        
        for item in items:
            column_values = item["column_values"]
            
            for column in column_values:
            
            # print(f"column: {column}")
                if column["type"] == "email":
                    email_text = column["text"]
                    emails[title] = email_text
                    value = {
                        "email": column['email'],
                        "text": column['text']
                    }
                    # print(f"value = {value}") 
                    
                    valores.append(value)
                    
    return emails, valores

def build_column_values(emails, valores, column_ids):
    column_values_payload = {}

    for key, email_text in emails.items():
        if key == "Clientes":
            column_title = "Email Clientes"
        elif key == "Comercial":
            column_title = "Email Comercial"
        else:
            continue

        col_id = column_ids[column_title]

        value = next((v for v in valores if v["text"] == email_text), None)
        if value:
            column_values_payload[col_id] = value
    
    return column_values_payload

def update_item(item_id, board_id, column_values_payload):
    column_values_payload1 = json.dumps(column_values_payload)
    print(column_values_payload1)


    mutation = '''
        mutation {
        change_multiple_column_values (item_id: %s, board_id: %s, column_values: %s) {
            id
        }
        }
        '''%(item_id,board_id, json.dumps(column_values_payload1))

    print(f"mutation = {mutation}")

    respuesta = monday_request(mutation)
    print(f"respuesta = {respuesta}")
    
def clear_email_columns(item_id, board_id, column_ids):
    columns_to_clear = {}
    
    for title in ['Email Clientes', 'Email Comercial']:
        col_id = column_ids.get(title)
        if col_id:
            columns_to_clear[col_id] = {"email": "", "text": ""}

    payload = json.dumps(columns_to_clear)

    mutation = '''
        mutation {
        change_multiple_column_values (item_id: %s, board_id: %s, column_values: %s) {
            id
        }
        }
    ''' % (item_id, board_id, json.dumps(payload))

    print("Mutación de limpieza:", mutation)

    response = monday_request(mutation)
    print("Respuesta al limpiar columnas:", response)
