from django.urls import path

from . import views


app_name = "production"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dashboard/pdf/", views.dashboard_pdf, name="dashboard_pdf"),
    path("dashboard/excel/", views.dashboard_excel, name="dashboard_excel"),
    path("reports/", views.report_list, name="report_list"),
    path("reports/pdf/", views.report_list_pdf, name="report_list_pdf"),
    path("reports/excel/", views.report_list_excel, name="report_list_excel"),
    path("reports/hub/", views.reports_hub, name="reports_hub"),
    path("reports/executive/", views.executive_report, name="executive_report"),
    path("reports/executive/pdf/", views.executive_report_pdf, name="executive_report_pdf"),
    path("reports/executive/excel/", views.executive_report_excel, name="executive_report_excel"),
    path("reports/operations/", views.operations_report, name="operations_report"),
    path("reports/operations/pdf/", views.operations_report_pdf, name="operations_report_pdf"),
    path("reports/operations/excel/", views.operations_report_excel, name="operations_report_excel"),
    path("reports/planning/", views.planning_report, name="planning_report"),
    path("reports/planning/pdf/", views.planning_report_pdf, name="planning_report_pdf"),
    path("reports/planning/excel/", views.planning_report_excel, name="planning_report_excel"),
    path("reports/sales/", views.sales_report, name="sales_report"),
    path("reports/sales/pdf/", views.sales_report_pdf, name="sales_report_pdf"),
    path("reports/sales/excel/", views.sales_report_excel, name="sales_report_excel"),
    path("reports/daily/", views.daily_report, name="daily_report"),
    path("reports/daily/pdf/", views.daily_report_pdf, name="daily_report_pdf"),
    path("reports/daily/excel/", views.daily_report_excel, name="daily_report_excel"),
    path("reports/comparison/", views.comparison_report, name="comparison_report"),
    path("reports/comparison/pdf/", views.comparison_report_pdf, name="comparison_report_pdf"),
    path("reports/comparison/excel/", views.comparison_report_excel, name="comparison_report_excel"),
    path("reports/new/", views.report_create, name="report_create"),
    path("reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("reports/<int:pk>/edit/", views.report_update, name="report_update"),
    path("reports/<int:pk>/delete/", views.report_delete, name="report_delete"),
    path("reports/<int:pk>/pdf/", views.report_detail_pdf, name="report_detail_pdf"),
    path("reports/<int:pk>/excel/", views.report_detail_excel, name="report_detail_excel"),
    path("setup/", views.setup_master_data, name="setup"),
]
