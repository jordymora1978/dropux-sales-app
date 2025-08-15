#!/bin/bash

echo "🔍 Verificando deployment de DROPUX..."
echo ""

# Backend en Railway
echo "📡 Backend (Railway):"
curl -s https://web-production-ae7da.up.railway.app/health | grep -q "healthy" && echo "✅ Backend funcionando" || echo "❌ Backend no responde"

# Test de CORS
echo ""
echo "🔐 Test CORS:"
response=$(curl -s -X OPTIONS "https://web-production-ae7da.up.railway.app/auth/login" \
  -H "Origin: https://sales.dropux.co" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -I | grep "Access-Control-Allow-Origin")

if [[ $response == *"sales.dropux.co"* ]]; then
  echo "✅ CORS configurado correctamente"
else
  echo "❌ Problema con CORS"
fi

# Frontend en Vercel
echo ""
echo "🎨 Frontend (Vercel):"
curl -s https://sales.dropux.co | grep -q "Drapify" && echo "✅ Frontend cargando" || echo "❌ Frontend no responde"

echo ""
echo "📝 Resumen:"
echo "- Backend URL: https://web-production-ae7da.up.railway.app"
echo "- Frontend URL: https://sales.dropux.co"
echo "- API configurada en frontend para usar Railway domain"
echo ""
echo "✨ Si todos los checks son ✅, el sistema está funcionando!"