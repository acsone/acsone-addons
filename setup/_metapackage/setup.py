import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-acsone-acsone-addons",
    description="Meta package for acsone-acsone-addons Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-account_analytic_invoice_note',
        'odoo8-addon-account_analytic_project_id',
        'odoo8-addon-account_auto_installer',
        'odoo8-addon-account_invoice_analytic_quick_view',
        'odoo8-addon-account_invoice_send_proforma',
        'odoo8-addon-analytic_code',
        'odoo8-addon-asynchronous_batch_mailings',
        'odoo8-addon-asynchronous_batch_mailings_unique_campaign',
        'odoo8-addon-distribution_list',
        'odoo8-addon-easy_debug_backend',
        'odoo8-addon-easy_debug_frontend',
        'odoo8-addon-email_separator',
        'odoo8-addon-event_mass_mailing',
        'odoo8-addon-event_multiple_registration',
        'odoo8-addon-global_resource_leave',
        'odoo8-addon-hr_contract_signature',
        'odoo8-addon-hr_contract_wage_type',
        'odoo8-addon-hr_employee_current_contract',
        'odoo8-addon-hr_holidays_usability',
        'odoo8-addon-hr_timesheet_cost_contract',
        'odoo8-addon-hr_timesheet_details_report',
        'odoo8-addon-hr_timesheet_previous_month_filter',
        'odoo8-addon-hr_timesheet_project_access_restriction',
        'odoo8-addon-hr_timesheet_sheet_invoice_approved',
        'odoo8-addon-hr_timesheet_sheet_usability',
        'odoo8-addon-hr_utilization',
        'odoo8-addon-html_widget_embedded_picture',
        'odoo8-addon-mail_html_widget_template',
        'odoo8-addon-mass_mailing_distribution_list',
        'odoo8-addon-multi_company_consolidation',
        'odoo8-addon-project_code',
        'odoo8-addon-readonly_bypass',
        'odoo8-addon-resource_calendar_half_day',
        'odoo8-addon-resource_calendar_multi_week',
        'odoo8-addon-service_logger',
        'odoo8-addon-settings_improvement',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
