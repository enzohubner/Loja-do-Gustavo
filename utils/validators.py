import re


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password):
    """Check if password meets minimum requirements."""
    if len(password) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    
    if len(password) > 128:  # Prevent extremely long passwords
        return False, "Senha não pode exceder 128 caracteres"
    
    return True, "Senha válida"


def sanitize_string(text, max_length=None):
    """Clean and validate string input."""
    if not isinstance(text, str):
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_positive_number(value, field_name="valor"):
    """Validate that a value is a positive number."""
    try:
        num_value = float(value)
        if num_value <= 0:
            return False, f"{field_name} deve ser maior que zero"
        return True, num_value
    except (ValueError, TypeError):
        return False, f"{field_name} deve ser um número válido"


def validate_non_negative_integer(value, field_name="quantidade"):
    """Validate that a value is a non-negative integer."""
    try:
        int_value = int(value)
        if int_value < 0:
            return False, f"{field_name} não pode ser negativa"
        return True, int_value
    except (ValueError, TypeError):
        return False, f"{field_name} deve ser um número inteiro válido"