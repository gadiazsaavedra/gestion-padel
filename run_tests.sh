#!/bin/bash

echo "🧪 Ejecutando Tests Automatizados..."

# Tests básicos
echo "📋 Tests unitarios..."
pytest stock_ventas/test_models.py -v

# Tests de views
echo "🌐 Tests de views..."
pytest stock_ventas/test_views.py -v

# Tests con coverage
echo "📊 Tests con coverage..."
pytest --cov=stock_ventas --cov-report=html --cov-report=term

# Tests de integración
echo "🔗 Tests de integración..."
pytest -m integration -v

echo "✅ Tests completados!"
echo "📊 Reporte de coverage en: htmlcov/index.html"