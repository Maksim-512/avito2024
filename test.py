import requests


# 1. Проверка доступности сервера
def test_ping():
    url = 'http://localhost:5000/api/ping'
    response = requests.get(url)

    assert response.status_code == 200
    assert response.json() == 'ok'


# 2. Получение списка тендеров
def test_list_tenders():
    url = 'http://localhost:5000/api/tenders'
    response = requests.get(url)
    assert isinstance(response.json(), list)


# 3. Создание нового тендера
def test_create_new_tender():
    url = 'http://localhost:5000/api/tenders/new'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "name": "Ten tender",
        "description": "Описание тендера",
        "serviceType": "Delivery",
        "organizationId": "650e8400-e29b-41d4-a716-446655440000",
        "creatorUsername": "test_user"
    }

    response = requests.post(url, json=data, headers=headers)

    assert response.status_code == 200
    assert response.json()['name'] == data['name']
    assert response.json()['description'] == data['description']
    assert response.json()['serviceType'] == data['serviceType']


# 4. Получить тендеры пользователя
def test_list_user_tenders():
    url = 'http://localhost:5000/api/tenders/my'
    data = {
        'username': "test_user"
    }

    response = requests.get(url, params=data)

    assert isinstance(response.json(), list)


# 5. Получение текущего статуса тендера
def test_get_tender_status():
    tender_id = "4e5bfd48-f60c-4fa2-9f33-eb10fe6fdb85"
    data = {
        'username': "test_user"
    }

    url = f'http://localhost:5000/api/tenders/{tender_id}/status'
    response = requests.get(url, params=data)
    result = {'status': 'Created'}

    assert response.status_code == 200
    assert response.json() == result


# 6. Изменение статуса тендера
def test_update_tender_status():
    tender_id = "13caa10d-229e-4238-a1a2-e56dbb329dca"
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "status": "Published"
    }

    url = f"http://localhost:5000/api/tenders/{tender_id}/status?username=test_user"

    response = requests.put(url, json=data, headers=headers)
    result = {"status": "Published"}

    print(response.status_code)
    print(response.json())

    assert response.status_code == 200
    assert response.json() == result


# 7. Редактирование тендера
def test_edit_tender():
    headers = {
        'Content-Type': 'application/json',
    }
    tender_id = "4e5bfd48-f60c-4fa2-9f33-eb10fe6fdb85"
    data = {
        'username': "test_user",
        'name': "Новый тендер",
        'description': "Обновленное описание",
        'serviceType': 'Construction'
    }
    url = f'http://localhost:5000/api/tenders/{tender_id}/edit?username=test_user'
    response = requests.patch(url, json=data, headers=headers)
    result = {
        'id': tender_id,
        'name': 'Новый тендер',
        'description': 'Обновленное описание',
        'status': 'Created',
        'serviceType': 'Construction',
        'version': 1
    }

    assert response.status_code == 200
    assert response.json() == result


# 8. Откат версии тендера
def test_rollback_tender():
    headers = {
        'Content-Type': 'application/json',
    }
    tender_id = "4e5bfd48-f60c-4fa2-9f33-eb10fe6fdb85"
    version = 1
    url = f'http://localhost:5000/api/tenders/{tender_id}/rollback/{version}'
    response = requests.put(url, headers=headers)
    assert response.status_code == 200
    assert response.json()['version'] == 0


# 9. Создание нового предложения
def test_creating_new_bid():
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "name": "New Bid",
        "description": "Test description",
        "tender_id": "4e5bfd48-f60c-4fa2-9f33-eb10fe6fdb85",
        "author_type": "Organization",
        "author_id": "8e5bfd58-f50c-2fa2-9f23-eb10fe6fdb45"
    }

    url = 'http://localhost:5000/api/bids/new'
    response = requests.put(url, json=data, headers=headers)

    assert response.status_code == 200
    assert response.json()['name'] == "New Bid"


# 10. Получение списка ваших предложений
def test_list_user_bids():
    username = 'test_user'

    url = f'http://localhost:5000/api/bids/my?username={username}'
    response = requests.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)


# 11. Получение списка предложений для тендера
def test_list_bids_for_tender():
    tender_id = "4e5bfd48-f60c-4fa2-9f33-eb10fe6fdb85"

    url = f'http://localhost:5000/api/bids/{tender_id}/list'
    response = requests.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)


# 12. Получение текущего статуса предложения
def test_update_bid_status():
    headers = {
        'Content-Type': 'application/json',
    }
    bid_id = "4r5bfd48-f32c-4fa2-9g33-eb12fe6fdb85"

    url = f'http://localhost:5000/api/bids/{bid_id}/status?status=Published'
    response = requests.put(url, headers=headers)

    assert response.status_code == 200
    assert response.json()['status'] == 'Published'


# 13. Изменение статуса предложения
def test_edit_bid():
    headers = {
        'Content-Type': 'application/json',
    }

    bid_id = "4r5bfd48-f32c-4fa2-9g33-eb12fe6fdb85"
    data = {
        "name": "Updated Bid",
        "description": "Updated description"
    }
    url = f'http://localhost:5000/api/bids/{bid_id}/edit'
    response = requests.put(url, json=data, headers=headers)

    assert response.status_code == 200
    assert response.json()['name'] == "Updated Bid"


# 14. Редактирование предложения
def test_submit_bid_decision():
    headers = {
        'Content-Type': 'application/json',
    }
    bid_id = "4r5bfd48-f32c-4fa2-9g33-eb12fe6fdb85"

    url = f'http://localhost:5000/api/bids/{bid_id}/submit_decision?decision=Approved'
    response = requests.put(url, headers=headers)

    assert response.status_code == 200
    assert response.json()['decision'] == 'Approved'


# 15. Отправка решения по предложению
def test_subm_bid_decision():
    headers = {
        'Content-Type': 'application/json',
    }
    bid_id = "4r5bfd48-f32c-4fa2-9g33-eb12fe6fdb85"

    url = f'http://localhost:5000/api/bids/{bid_id}/submit_decision?description=Approved&username=test_user'

    response = requests.put(url, headers=headers)
    assert response.status_code == 200
    assert response.json()['decision'] == 'Approved'

    url_new = f'http://localhost:5000/api/bids/{bid_id}/submit_decision?description=WrongDecision&username=test_user'

    response = requests.put(url_new, headers=headers)

    assert response.status_code == 400


if __name__ == '__main__':
    test_ping()
