"""Basic tests for ThreadVibe application."""

import pytest
from app import create_app
import config


@pytest.fixture
def app():
    """Create application for testing."""
    test_config = {
        "USE_MOCK_DB": True,
        "SECRET_KEY": "test-secret-key",
    }
    app = create_app(test_config)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_homepage(client):
    """Test homepage loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'ThreadVibe' in response.data


def test_products_page(client):
    """Test products page loads."""
    response = client.get('/products')
    assert response.status_code == 200


def test_login_page(client):
    """Test login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data or b'Sign in' in response.data


def test_register_page(client):
    """Test register page loads."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data


def test_cart_page(client):
    """Test cart page loads."""
    response = client.get('/cart')
    assert response.status_code == 200


def test_checkout_page(client):
    """Test checkout page loads."""
    response = client.get('/checkout')
    assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
