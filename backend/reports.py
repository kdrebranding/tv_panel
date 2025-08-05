"""
TV Panel Advanced Reports & Analytics Module
Generuje zaawansowane raporty, analizy i wykresy dla systemu zarządzania IPTV.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import json
import os
from io import BytesIO
import base64
from pydantic import BaseModel
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Router for reports
router = APIRouter(prefix="/api/reports", tags=["Reports"])

# Models
class ReportRequest(BaseModel):
    report_type: str  # "monthly", "quarterly", "yearly", "custom"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    format: str = "json"  # "json", "csv", "pdf", "excel"

class AnalyticsData(BaseModel):
    labels: List[str]
    values: List[int]
    colors: Optional[List[str]] = None

class DashboardMetrics(BaseModel):
    total_clients: int
    active_clients: int
    expired_clients: int
    expiring_soon: int
    revenue_trend: List[Dict]
    client_growth: List[Dict]
    panel_distribution: AnalyticsData
    app_distribution: AnalyticsData
    expiry_timeline: List[Dict]
    retention_rate: float
    churn_rate: float

# Set style for plots
plt.style.use('dark_background')
sns.set_palette("husl")

class ReportsGenerator:
    
    @staticmethod
    async def get_dashboard_metrics() -> DashboardMetrics:
        """Generate comprehensive dashboard metrics"""
        
        # Basic counts
        total_clients = await db.clients.count_documents({})
        active_clients = await db.clients.count_documents({"status": "active"})
        expired_clients = await db.clients.count_documents({"status": "expired"})
        expiring_soon = await db.clients.count_documents({"status": "expiring_soon"})
        
        # Revenue trend (last 12 months) - assuming 30 PLN per month per client
        revenue_trend = []
        for i in range(12, 0, -1):
            month_date = datetime.now() - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            monthly_active = await db.clients.count_documents({
                "created_at": {"$lte": month_end},
                "$or": [
                    {"expires_date": {"$gte": month_start}},
                    {"expires_date": None}
                ]
            })
            
            revenue_trend.append({
                "month": month_date.strftime("%m/%Y"),
                "revenue": monthly_active * 30,  # 30 PLN per client
                "clients": monthly_active
            })
        
        # Client growth (last 12 months)
        client_growth = []
        cumulative_clients = 0
        
        for i in range(12, 0, -1):
            month_date = datetime.now() - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            new_clients = await db.clients.count_documents({
                "created_at": {
                    "$gte": month_start,
                    "$lte": month_end
                }
            })
            
            cumulative_clients += new_clients
            client_growth.append({
                "month": month_date.strftime("%m/%Y"),
                "new_clients": new_clients,
                "total_clients": cumulative_clients
            })
        
        # Panel distribution
        panels = await db.panels.find().to_list(None)
        panel_data = []
        panel_labels = []
        
        for panel in panels:
            count = await db.clients.count_documents({"panel_id": panel["id"]})
            panel_labels.append(panel["name"])
            panel_data.append(count)
        
        # App distribution
        apps = await db.apps.find().to_list(None)
        app_data = []
        app_labels = []
        
        for app in apps:
            count = await db.clients.count_documents({"app_id": app["id"]})
            app_labels.append(app["name"])
            app_data.append(count)
        
        # Expiry timeline (next 30 days)
        expiry_timeline = []
        today = datetime.now().date()
        
        for i in range(30):
            check_date = today + timedelta(days=i)
            expiring_count = await db.clients.count_documents({
                "expires_date": {
                    "$gte": datetime.combine(check_date, datetime.min.time()),
                    "$lt": datetime.combine(check_date + timedelta(days=1), datetime.min.time())
                }
            })
            
            expiry_timeline.append({
                "date": check_date.strftime("%d/%m"),
                "expiring": expiring_count
            })
        
        # Retention and churn rates
        # Calculate based on clients from 3 months ago
        three_months_ago = datetime.now() - timedelta(days=90)
        clients_3_months_ago = await db.clients.count_documents({
            "created_at": {"$lte": three_months_ago}
        })
        
        still_active = await db.clients.count_documents({
            "created_at": {"$lte": three_months_ago},
            "status": {"$in": ["active", "expiring_soon"]}
        })
        
        retention_rate = (still_active / clients_3_months_ago * 100) if clients_3_months_ago > 0 else 0
        churn_rate = 100 - retention_rate
        
        return DashboardMetrics(
            total_clients=total_clients,
            active_clients=active_clients,
            expired_clients=expired_clients,
            expiring_soon=expiring_soon,
            revenue_trend=revenue_trend,
            client_growth=client_growth,
            panel_distribution=AnalyticsData(labels=panel_labels, values=panel_data),
            app_distribution=AnalyticsData(labels=app_labels, values=app_data),
            expiry_timeline=expiry_timeline,
            retention_rate=round(retention_rate, 2),
            churn_rate=round(churn_rate, 2)
        )
    
    @staticmethod
    async def generate_monthly_report(year: int, month: int) -> Dict:
        """Generate detailed monthly report"""
        
        # Date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # New clients this month
        new_clients = await db.clients.find({
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # Expired clients this month
        expired_clients = await db.clients.find({
            "expires_date": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # Revenue calculation (assuming 30 PLN per client)
        active_clients_count = len(new_clients) - len(expired_clients)
        estimated_revenue = active_clients_count * 30
        
        # Top panels and apps
        panel_stats = defaultdict(int)
        app_stats = defaultdict(int)
        
        for client in new_clients:
            if client.get('panel_id'):
                panel = await db.panels.find_one({"id": client['panel_id']})
                if panel:
                    panel_stats[panel['name']] += 1
            
            if client.get('app_id'):
                app = await db.apps.find_one({"id": client['app_id']})
                if app:
                    app_stats[app['name']] += 1
        
        # Client satisfaction metrics (based on retention)
        total_clients_start = await db.clients.count_documents({
            "created_at": {"$lte": start_date}
        })
        
        still_active = await db.clients.count_documents({
            "created_at": {"$lte": start_date},
            "expires_date": {"$gte": end_date}
        })
        
        retention_rate = (still_active / total_clients_start * 100) if total_clients_start > 0 else 0
        
        return {
            "period": f"{month:02d}/{year}",
            "summary": {
                "new_clients": len(new_clients),
                "expired_clients": len(expired_clients),
                "net_growth": len(new_clients) - len(expired_clients),
                "estimated_revenue": estimated_revenue,
                "retention_rate": round(retention_rate, 2)
            },
            "top_panels": dict(sorted(panel_stats.items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_apps": dict(sorted(app_stats.items(), key=lambda x: x[1], reverse=True)[:5]),
            "new_clients_details": [
                {
                    "name": client.get('name'),
                    "created_at": client.get('created_at').strftime("%d/%m/%Y"),
                    "expires_date": client.get('expires_date').strftime("%d/%m/%Y") if client.get('expires_date') else None,
                    "panel": client.get('panel_name'),
                    "app": client.get('app_name')
                }
                for client in new_clients[:10]  # Top 10 new clients
            ]
        }
    
    @staticmethod
    async def generate_chart(chart_type: str, data: Dict) -> str:
        """Generate chart and return base64 encoded image"""
        
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        
        if chart_type == "revenue_trend":
            months = [item["month"] for item in data["revenue_trend"]]
            revenues = [item["revenue"] for item in data["revenue_trend"]]
            
            plt.plot(months, revenues, marker='o', linewidth=2, markersize=6, color='#00ff88')
            plt.title('Trend Przychodów (12 miesięcy)', fontsize=16, color='white')
            plt.xlabel('Miesiąc', color='white')
            plt.ylabel('Przychód (PLN)', color='white')
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            plt.grid(True, alpha=0.3)
            
        elif chart_type == "client_growth":
            months = [item["month"] for item in data["client_growth"]]
            new_clients = [item["new_clients"] for item in data["client_growth"]]
            total_clients = [item["total_clients"] for item in data["client_growth"]]
            
            plt.bar(months, new_clients, alpha=0.7, label='Nowi klienci', color='#00ff88')
            plt.plot(months, total_clients, marker='o', color='#ff6b6b', linewidth=2, label='Łącznie klientów')
            plt.title('Wzrost Klientów (12 miesięcy)', fontsize=16, color='white')
            plt.xlabel('Miesiąc', color='white')
            plt.ylabel('Liczba klientów', color='white')
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
        elif chart_type == "panel_distribution":
            labels = data["panel_distribution"]["labels"]
            sizes = data["panel_distribution"]["values"]
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
            
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)])
            plt.title('Rozkład Paneli IPTV', fontsize=16, color='white')
            
        elif chart_type == "app_distribution":
            labels = data["app_distribution"]["labels"]
            sizes = data["app_distribution"]["values"]
            colors = ['#a55eea', '#26de81', '#fc5c65', '#fed330', '#45aaf2']
            
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)])
            plt.title('Rozkład Aplikacji IPTV', fontsize=16, color='white')
            
        elif chart_type == "expiry_timeline":
            dates = [item["date"] for item in data["expiry_timeline"]]
            expiring = [item["expiring"] for item in data["expiry_timeline"]]
            
            plt.bar(dates, expiring, color='#ff6b6b', alpha=0.8)
            plt.title('Harmonogram Wygasających Licencji (30 dni)', fontsize=16, color='white')
            plt.xlabel('Data', color='white')
            plt.ylabel('Liczba wygasających', color='white')
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            plt.grid(True, alpha=0.3, axis='y')
        
        # Save to base64
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', facecolor='#0f0f10', edgecolor='none', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    @staticmethod
    async def export_to_csv(data: List[Dict], filename: str) -> str:
        """Export data to CSV and return filepath"""
        
        df = pd.DataFrame(data)
        filepath = f"/tmp/{filename}.csv"
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        return filepath
    
    @staticmethod
    async def generate_pdf_report(report_data: Dict, filename: str) -> str:
        """Generate PDF report and return filepath"""
        
        # This would require additional libraries like reportlab
        # For now, return a placeholder
        filepath = f"/tmp/{filename}.pdf"
        
        # Create a simple text-based report
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"TV PANEL - RAPORT\n")
            f.write(f"==================\n\n")
            f.write(f"Data wygenerowania: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write(json.dumps(report_data, indent=2, ensure_ascii=False, default=str))
        
        return filepath

# API Endpoints
@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    return await ReportsGenerator.get_dashboard_metrics()

@router.get("/monthly/{year}/{month}")
async def get_monthly_report(year: int, month: int):
    """Get detailed monthly report"""
    return await ReportsGenerator.generate_monthly_report(year, month)

@router.get("/chart/{chart_type}")
async def get_chart(chart_type: str):
    """Generate and return chart as base64 image"""
    
    # Get data for chart
    dashboard_data = await ReportsGenerator.get_dashboard_metrics()
    chart_image = await ReportsGenerator.generate_chart(chart_type, dashboard_data.dict())
    
    return {"chart": chart_image}

@router.post("/export")
async def export_report(request: ReportRequest):
    """Export report in requested format"""
    
    if request.report_type == "monthly":
        now = datetime.now()
        data = await ReportsGenerator.generate_monthly_report(now.year, now.month)
    else:
        # Default to dashboard data
        data = await ReportsGenerator.get_dashboard_metrics()
        data = data.dict()
    
    if request.format == "csv":
        # Convert to list of dicts for CSV
        if isinstance(data, dict) and "new_clients_details" in data:
            csv_data = data["new_clients_details"]
        else:
            csv_data = [data]  # Wrap single dict in list
        
        filepath = await ReportsGenerator.export_to_csv(
            csv_data, 
            f"tv_panel_report_{datetime.now().strftime('%Y%m%d')}"
        )
        
        # Read and return file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(filepath)}"}
        )
    
    elif request.format == "pdf":
        filepath = await ReportsGenerator.generate_pdf_report(
            data, 
            f"tv_panel_report_{datetime.now().strftime('%Y%m%d')}"
        )
        
        with open(filepath, 'rb') as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(filepath)}"}
        )
    
    else:  # JSON
        return data

@router.get("/analytics/retention")
async def get_retention_analytics():
    """Get detailed retention analytics"""
    
    retention_data = []
    
    # Calculate retention for last 6 months
    for i in range(6, 0, -1):
        period_start = datetime.now() - timedelta(days=30*i)
        period_end = period_start + timedelta(days=30)
        
        # Clients at start of period
        clients_start = await db.clients.count_documents({
            "created_at": {"$lte": period_start}
        })
        
        # Clients still active at end of period
        still_active = await db.clients.count_documents({
            "created_at": {"$lte": period_start},
            "expires_date": {"$gte": period_end}
        })
        
        retention_rate = (still_active / clients_start * 100) if clients_start > 0 else 0
        
        retention_data.append({
            "period": period_start.strftime("%m/%Y"),
            "clients_start": clients_start,
            "clients_retained": still_active,
            "retention_rate": round(retention_rate, 2),
            "churn_rate": round(100 - retention_rate, 2)
        })
    
    return {"retention_analytics": retention_data}

@router.get("/analytics/revenue")
async def get_revenue_analytics():
    """Get detailed revenue analytics"""
    
    # Revenue by panel
    panels = await db.panels.find().to_list(None)
    panel_revenue = []
    
    for panel in panels:
        active_clients = await db.clients.count_documents({
            "panel_id": panel["id"],
            "status": {"$in": ["active", "expiring_soon"]}
        })
        revenue = active_clients * 30  # 30 PLN per client
        
        panel_revenue.append({
            "panel_name": panel["name"],
            "active_clients": active_clients,
            "monthly_revenue": revenue
        })
    
    # Revenue forecast (next 3 months)
    revenue_forecast = []
    current_active = await db.clients.count_documents({"status": "active"})
    
    for i in range(1, 4):
        # Assume 5% monthly growth
        forecast_clients = int(current_active * (1.05 ** i))
        forecast_revenue = forecast_clients * 30
        
        future_date = datetime.now() + timedelta(days=30*i)
        revenue_forecast.append({
            "month": future_date.strftime("%m/%Y"),
            "forecast_clients": forecast_clients,
            "forecast_revenue": forecast_revenue
        })
    
    return {
        "panel_revenue": panel_revenue,
        "revenue_forecast": revenue_forecast,
        "total_monthly_revenue": sum(pr["monthly_revenue"] for pr in panel_revenue)
    }