@echo off
echo Running integration tests against the application...
echo.

python -m pytest test_auth.py test_users.py test_finance.py test_receipt_generation.py test_dashboard.py test_profile.py -v

echo.
echo Tests completed!
