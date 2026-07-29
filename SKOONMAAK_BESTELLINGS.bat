@echo off
echo.
echo  SVS Stock - Vee Toets-Bestellings Uit
echo  =======================================
echo.
echo  Dit sal ALLE bestellings uitvee.
echo  Produkte en salonne bly ongeskonde.
echo.
pause
python "%~dp0db\clear_orders.py"
echo.
pause
