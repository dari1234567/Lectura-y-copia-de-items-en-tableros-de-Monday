import json
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .functions import build_column_values, get_email_values, read_main_item, update_item, clear_email_columns

# Create your views here.
@csrf_exempt
def test(request):
    
    if request.method != 'POST':
        return HttpResponseBadRequest("Error: solo se aceptan peticiones POST")

    try:
        body = json.loads(request.body.decode("utf-8"))
        item_id = body['payload']['inboundFieldValues']['itemId']
        board_id = body['payload']['inboundFieldValues']['boardId']
    except (KeyError, json.JSONDecodeError) as e:
        return HttpResponseBadRequest(f"Invalid request body: {str(e)}")

    
    column_ids, ids_items_linked = read_main_item(item_id)
    
    clear_email_columns(item_id, board_id, column_ids)

    
    emails, valores = get_email_values(ids_items_linked)

   
    column_values_payload = build_column_values(emails, valores, column_ids)

    
    update_item(item_id, board_id, column_values_payload)

    return JsonResponse({"status": "success", "item_id": item_id})


def health(request):
    return HttpResponse("OK")
