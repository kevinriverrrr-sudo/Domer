"""
Улучшенный модуль для работы с PayPal API и проверки карт
На основе PayPal Server SDK паттернов
"""

import requests
import base64
import json
from typing import Dict, Tuple, Optional
from config import PAYPAL_CLIENT_ID, PAYPAL_SECRET, PAYPAL_API_BASE, CHECK_AMOUNT, CURRENCY_CODE


class PayPalChecker:
    def __init__(self):
        self.client_id = PAYPAL_CLIENT_ID
        self.secret = PAYPAL_SECRET
        self.base_url = PAYPAL_API_BASE
        self.access_token = None
        self.timeout = 15  # увеличенный timeout
    
    def get_access_token(self) -> Optional[str]:
        """
        Получение access token для PayPal API
        """
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            
            auth_string = f"{self.client_id}:{self.secret}"
            auth_bytes = auth_string.encode('utf-8')
            auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            data = {"grant_type": "client_credentials"}
            
            response = requests.post(url, headers=headers, data=data, timeout=self.timeout)
            
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                return self.access_token
            else:
                print(f"❌ Ошибка получения токена: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Исключение при получении токена: {e}")
            return None
    
    def create_order(self, amount: str = CHECK_AMOUNT, intent: str = "CAPTURE") -> Optional[Dict]:
        """
        Создание заказа в PayPal
        
        Args:
            amount: Сумма заказа
            intent: CAPTURE или AUTHORIZE
        
        Returns:
            Dict с информацией о заказе или None
        """
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            return None
        
        try:
            url = f"{self.base_url}/v2/checkout/orders"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "Prefer": "return=representation"  # Полный ответ
            }
            
            payload = {
                "intent": intent,
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": CURRENCY_CODE,
                            "value": amount
                        }
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"❌ Ошибка создания заказа: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Исключение при создании заказа: {e}")
            return None
    
    def capture_order(self, order_id: str) -> Tuple[bool, Dict]:
        """
        Capture (захват) платежа для созданного заказа
        
        Args:
            order_id: ID созданного заказа
        
        Returns:
            Tuple: (success: bool, response_data: dict)
        """
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            return False, {"error": "No access token"}
        
        try:
            url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "Prefer": "return=representation"
            }
            
            response = requests.post(url, headers=headers, json={}, timeout=self.timeout)
            response_data = response.json()
            
            if response.status_code == 201:
                return True, response_data
            else:
                print(f"⚠️ Capture failed: {response.status_code}")
                return False, response_data
                
        except Exception as e:
            print(f"❌ Исключение при capture: {e}")
            return False, {"error": str(e)}
    
    def authorize_order(self, order_id: str) -> Tuple[bool, Dict]:
        """
        Authorize (авторизация) платежа без захвата
        
        Args:
            order_id: ID созданного заказа
        
        Returns:
            Tuple: (success: bool, response_data: dict)
        """
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            return False, {"error": "No access token"}
        
        try:
            url = f"{self.base_url}/v2/checkout/orders/{order_id}/authorize"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "Prefer": "return=representation"
            }
            
            response = requests.post(url, headers=headers, json={}, timeout=self.timeout)
            response_data = response.json()
            
            if response.status_code == 201:
                return True, response_data
            else:
                print(f"⚠️ Authorize failed: {response.status_code}")
                return False, response_data
                
        except Exception as e:
            print(f"❌ Исключение при authorize: {e}")
            return False, {"error": str(e)}
    
    def capture_authorization(self, authorization_id: str, amount: Optional[str] = None, final_capture: bool = True) -> Tuple[bool, Dict]:
        """
        Захват авторизованного платежа
        
        Args:
            authorization_id: ID авторизации
            amount: Сумма для захвата (опционально)
            final_capture: Финальный захват или нет
        
        Returns:
            Tuple: (success: bool, response_data: dict)
        """
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            return False, {"error": "No access token"}
        
        try:
            url = f"{self.base_url}/v2/payments/authorizations/{authorization_id}/capture"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "Prefer": "return=representation"
            }
            
            payload = {
                "final_capture": final_capture
            }
            
            if amount:
                payload["amount"] = {
                    "currency_code": CURRENCY_CODE,
                    "value": amount
                }
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response_data = response.json()
            
            if response.status_code == 201:
                return True, response_data
            else:
                print(f"⚠️ Capture authorization failed: {response.status_code}")
                return False, response_data
                
        except Exception as e:
            print(f"❌ Исключение при capture authorization: {e}")
            return False, {"error": str(e)}
    
    def check_card(self, card_number: str, exp_month: str, exp_year: str, cvv: str) -> Tuple[str, str, Dict]:
        """
        Проверка карты через PayPal API (улучшенная версия)
        
        Args:
            card_number: Номер карты
            exp_month: Месяц истечения (MM)
            exp_year: Год истечения (YYYY)
            cvv: CVV код
        
        Returns:
            Tuple: (статус, сообщение, полные данные ответа)
        """
        try:
            # Получаем токен если его нет
            if not self.access_token:
                if not self.get_access_token():
                    return "❌ ERROR", "Не удалось получить токен доступа к PayPal API. Проверьте credentials в config.py", {}
            
            # Создаем заказ с CAPTURE intent
            order = self.create_order(CHECK_AMOUNT, "CAPTURE")
            if not order:
                return "❌ ERROR", "Не удалось создать заказ. Проверьте PayPal credentials.", {}
            
            order_id = order.get('id')
            print(f"📦 Создан заказ: {order_id}")
            
            # Пытаемся захватить платеж с картой
            url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "Prefer": "return=representation"
            }
            
            payment_source = {
                "card": {
                    "number": card_number,
                    "expiry": f"{exp_year}-{exp_month}",
                    "security_code": cvv,
                    "name": "Card Holder",
                    "billing_address": {
                        "address_line_1": "123 Main St",
                        "admin_area_2": "New York",
                        "admin_area_1": "NY",
                        "postal_code": "10001",
                        "country_code": "US"
                    }
                }
            }
            
            payload = {
                "payment_source": payment_source
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            
            # Обработка ответа
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            status_code = response.status_code
            
            # Анализируем ответ
            if status_code == 201:
                # Успешный capture
                status = response_data.get('status', 'UNKNOWN')
                
                # Получаем информацию о карте
                card_info = {}
                if 'payment_source' in response_data:
                    card_info = response_data['payment_source'].get('card', {})
                
                # Получаем информацию о захвате платежа
                capture_info = {}
                capture_status = "UNKNOWN"
                
                if 'purchase_units' in response_data and len(response_data['purchase_units']) > 0:
                    payments = response_data['purchase_units'][0].get('payments', {})
                    if 'captures' in payments and len(payments['captures']) > 0:
                        capture_info = payments['captures'][0]
                        capture_status = capture_info.get('status', 'UNKNOWN')
                
                # Определяем финальный статус
                if status == "COMPLETED" and capture_status == "COMPLETED":
                    result_status = "✅ LIVE"
                    result_msg = f"Карта валидна и активна! Платеж успешно захвачен."
                    
                    # Добавляем детали
                    if capture_info:
                        amount = capture_info.get('amount', {})
                        result_msg += f"\n💰 Сумма: {amount.get('value')} {amount.get('currency_code')}"
                    
                elif status == "COMPLETED" and capture_status == "DECLINED":
                    result_status = "⚠️ DECLINED"
                    result_msg = "Карта валидна, но платеж отклонен банком"
                    
                    # Информация о причине отклонения
                    if 'processor_response' in capture_info:
                        proc_resp = capture_info['processor_response']
                        result_msg += f"\nКод ответа: {proc_resp.get('response_code', 'N/A')}"
                        result_msg += f"\nAVS: {proc_resp.get('avs_code', 'N/A')}"
                        result_msg += f"\nCVV: {proc_resp.get('cvv_code', 'N/A')}"
                
                else:
                    result_status = f"⚠️ {status}"
                    result_msg = f"Статус заказа: {status}, Capture: {capture_status}"
            
            elif status_code == 422:
                # Ошибка валидации (невалидная карта)
                result_status = "❌ DEAD"
                
                error_details = response_data.get('details', [])
                if error_details:
                    error_msg = error_details[0].get('description', 'Unknown error')
                    result_msg = f"Карта невалидна: {error_msg}"
                else:
                    result_msg = "Карта невалидна или данные неверны"
            
            elif 'error' in response_data or 'message' in response_data:
                # Общая ошибка
                error_msg = response_data.get('message', response_data.get('error', 'Unknown error'))
                result_status = "❌ ERROR"
                result_msg = f"Ошибка PayPal: {error_msg}"
            
            else:
                result_status = "❓ UNKNOWN"
                result_msg = f"Неизвестный статус (HTTP {status_code})"
            
            return result_status, result_msg, response_data
            
        except requests.exceptions.Timeout:
            return "⏱️ TIMEOUT", "Превышено время ожидания ответа от PayPal", {}
        except requests.exceptions.RequestException as e:
            return "❌ ERROR", f"Ошибка сети: {str(e)}", {}
        except Exception as e:
            return "❌ ERROR", f"Ошибка: {str(e)}", {}
    
    def parse_card_line(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Парсинг строки с данными карты
        Форматы: 
        - 4111111111111111|12|2025|123
        - 4111111111111111|12/2025|123
        - 4111111111111111 12 2025 123
        """
        try:
            line = line.strip()
            
            # Разделители
            if '|' in line:
                parts = line.split('|')
            elif ' ' in line:
                parts = line.split()
            else:
                return None
            
            if len(parts) < 3:
                return None
            
            card_number = parts[0].strip()
            
            # Проверка месяца и года
            if len(parts) == 3:
                # Формат: card|mm/yyyy|cvv
                exp_part = parts[1].strip()
                cvv = parts[2].strip()
                
                if '/' in exp_part:
                    exp_month, exp_year = exp_part.split('/')
                else:
                    return None
            elif len(parts) == 4:
                # Формат: card|mm|yyyy|cvv
                exp_month = parts[1].strip()
                exp_year = parts[2].strip()
                cvv = parts[3].strip()
            else:
                return None
            
            # Нормализация года
            if len(exp_year) == 2:
                exp_year = "20" + exp_year
            
            # Нормализация месяца
            if len(exp_month) == 1:
                exp_month = "0" + exp_month
            
            # Валидация
            if not (card_number.isdigit() and len(card_number) >= 13 and len(card_number) <= 19):
                return None
            if not (exp_month.isdigit() and 1 <= int(exp_month) <= 12):
                return None
            if not (exp_year.isdigit() and len(exp_year) == 4):
                return None
            if not (cvv.isdigit() and len(cvv) >= 3 and len(cvv) <= 4):
                return None
            
            return card_number, exp_month, exp_year, cvv
            
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return None
    
    def get_card_bin_info(self, card_number: str) -> str:
        """
        Определение типа карты по BIN
        """
        if not card_number or len(card_number) < 1:
            return "UNKNOWN"
        
        first_digit = card_number[0]
        
        if first_digit == '4':
            return "VISA"
        elif first_digit == '5':
            return "MASTERCARD"
        elif first_digit == '3':
            if len(card_number) > 1 and card_number[1] in ['4', '7']:
                return "AMEX"
            else:
                return "DINERS/JCB"
        elif first_digit == '6':
            return "DISCOVER"
        else:
            return "UNKNOWN"
