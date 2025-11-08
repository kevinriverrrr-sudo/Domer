"""
Модуль для работы с PayPal API и проверки карт
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
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {"grant_type": "client_credentials"}
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                return self.access_token
            else:
                print(f"Ошибка получения токена: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Исключение при получении токена: {e}")
            return None
    
    def create_order(self, amount: str = CHECK_AMOUNT) -> Optional[Dict]:
        """
        Создание заказа в PayPal
        """
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            return None
        
        try:
            url = f"{self.base_url}/v2/checkout/orders"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": CURRENCY_CODE,
                        "value": amount
                    }
                }]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Ошибка создания заказа: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Исключение при создании заказа: {e}")
            return None
    
    def check_card(self, card_number: str, exp_month: str, exp_year: str, cvv: str) -> Tuple[str, str, Dict]:
        """
        Проверка карты через PayPal API
        
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
                    return "❌ ERROR", "Не удалось получить токен доступа к PayPal API", {}
            
            # Создаем заказ
            order = self.create_order()
            if not order:
                return "❌ ERROR", "Не удалось создать заказ", {}
            
            order_id = order.get('id')
            
            # Пытаемся захватить платеж с картой
            url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            payment_source = {
                "card": {
                    "number": card_number,
                    "expiry": f"{exp_year}-{exp_month}",
                    "security_code": cvv
                }
            }
            
            payload = {
                "payment_source": payment_source
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response_data = response.json()
            
            # Анализируем ответ
            status = response_data.get('status', 'UNKNOWN')
            
            # Получаем информацию о карте
            card_info = {}
            if 'payment_source' in response_data:
                card_info = response_data['payment_source'].get('card', {})
            
            # Получаем информацию о захвате платежа
            capture_info = {}
            if 'purchase_units' in response_data and len(response_data['purchase_units']) > 0:
                payments = response_data['purchase_units'][0].get('payments', {})
                if 'captures' in payments and len(payments['captures']) > 0:
                    capture_info = payments['captures'][0]
            
            # Определяем статус карты
            if status == "COMPLETED":
                capture_status = capture_info.get('status', 'UNKNOWN')
                
                if capture_status == "COMPLETED":
                    result_status = "✅ LIVE"
                    result_msg = "Карта валидна и активна"
                elif capture_status == "DECLINED":
                    result_status = "⚠️ DECLINED"
                    result_msg = "Карта валидна, но платеж отклонен"
                else:
                    result_status = f"⚠️ {capture_status}"
                    result_msg = f"Статус: {capture_status}"
            
            elif status == "PAYER_ACTION_REQUIRED":
                result_status = "🔐 3DS"
                result_msg = "Требуется 3D Secure аутентификация"
            
            elif 'error' in response_data or 'message' in response_data:
                error_msg = response_data.get('message', response_data.get('error', 'Unknown error'))
                result_status = "❌ DEAD"
                result_msg = f"Карта невалидна: {error_msg}"
            
            else:
                result_status = "❓ UNKNOWN"
                result_msg = f"Неизвестный статус: {status}"
            
            return result_status, result_msg, response_data
            
        except requests.exceptions.Timeout:
            return "⏱️ TIMEOUT", "Превышено время ожидания ответа", {}
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
            print(f"Ошибка парсинга: {e}")
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
