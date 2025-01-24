from flask import request


def verify_recaptcha(recaptcha_response):
    secret_key = '6LeVnaEqAAAAAOO8kuULpYFF5wPBbt5svPX8NKvv'
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    
    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    
    response = request.post(verify_url, data=data)
    result = response.json()
    
    return result.get('success', False)