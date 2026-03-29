import dash
from dash import dcc, html, Input, Output, State  # لاحظ إضافة State هنا
import pandas as pd
import plotly.express as px

# 1. تحميل البيانات (تأكد أن ملف CSV موجود في نفس الفولدر)
try:
    df = pd.read_csv('business_sales.csv')
except FileNotFoundError:
    print("❌ Error: business_sales.csv not found! Run business_maker.py first.")

app = dash.Dash(__name__)

# 2. تصميم واجهة المستخدم (Layout)
app.layout = html.Div([
    html.H1("🏬 Business Performance Dashboard | لوحة أداء المحلات", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'padding': '20px'}),
    
    # قسم التحكم (Dropdown + Download Button)
    html.Div([
        html.Label("Select Branch | اختر الفرع:", style={'fontWeight': 'bold', 'fontSize': '18px'}),
        dcc.Dropdown(
            id='branch-dropdown',
            # إضافة خيار "كل الفروع"
            options=[{'label': 'All Branches | كل الفروع', 'value': 'All'}] + \
                    [{'label': b, 'value': b} for b in df['Branch'].unique()],
            value='All',
            clearable=False,
            style={'marginBottom': '10px'}
        ),
        
        # زرار الـ Download (الهدية/الكادو للعميل)
        html.Div([
            html.Button("📥 Download Data Report | تحميل تقرير البيانات", id="btn-download", 
                        style={
                            'margin': '10px', 'padding': '12px 25px', 
                            'backgroundColor': '#27ae60', 'color': 'white', 
                            'border': 'none', 'borderRadius': '8px', 
                            'cursor': 'pointer', 'fontSize': '16px',
                            'fontWeight': 'bold'
                        }),
            dcc.Download(id="download-dataframe-csv"),
        ], style={'textAlign': 'center'}),

    ], style={'width': '50%', 'margin': 'auto', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '15px', 'boxShadow': '0px 4px 15px rgba(0,0,0,0.1)'}),

    # كروت الإحصائيات (Summary Cards)
    html.Div(id='stats-container', style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '30px'}),

    # الرسوم البيانية
    html.Div([
        html.Div([dcc.Graph(id='sales-bar-chart')], style={'width': '49%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='profit-pie-chart')], style={'width': '49%', 'display': 'inline-block'})
    ], style={'padding': '10px'})

], style={'backgroundColor': '#f0f2f5', 'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', 'minHeight': '100vh'})

# ---------------------------------------------------------
# 3. الربط التفاعلي (Callbacks)

# أ- تحديث البيانات والرسوم البيانية بناءً على اختيار الفرع
@app.callback(
    [Output('stats-container', 'children'),
     Output('sales-bar-chart', 'figure'),
     Output('profit-pie-chart', 'figure')],
    [Input('branch-dropdown', 'value')]
)
def update_dashboard(selected_branch):
    # حالة اختيار "كل الفروع"
    if selected_branch == 'All':
        filtered_df = df
        title_suffix = "All Branches"
    else:
        filtered_df = df[df['Branch'] == selected_branch]
        title_suffix = f"Branch: {selected_branch}"
    
    # حساب الأرقام للكروت
    total_sales = f"${filtered_df['Total_Sales'].sum():,.0f}"
    total_profit = f"${filtered_df['Profit'].sum():,.0f}"
    
    cards = [
        html.Div([
            html.H3("Total Sales", style={'margin': '0', 'fontSize': '18px', 'color': '#7f8c8d'}), 
            html.H2(total_sales, style={'margin': '10px 0', 'color': '#2980b9'})
        ], style={'padding': '20px', 'boxShadow': '2px 2px 10px #ddd', 'borderRadius': '12px', 'backgroundColor': 'white', 'textAlign': 'center', 'width': '30%'}),
        
        html.Div([
            html.H3("Total Profit", style={'margin': '0', 'fontSize': '18px', 'color': '#7f8c8d'}), 
            html.H2(total_profit, style={'margin': '10px 0', 'color': '#27ae60'})
        ], style={'padding': '20px', 'boxShadow': '2px 2px 10px #ddd', 'borderRadius': '12px', 'backgroundColor': 'white', 'textAlign': 'center', 'width': '30%'})
    ]
    
    # رسم المبيعات
 # 1. تجميع البيانات وترتيبها من الكبير للصغير (عشان الرسمة تبقى احترافية)
    sales_data = filtered_df.groupby('Product')['Total_Sales'].sum().reset_index()
    sales_data = sales_data.sort_values(by='Total_Sales', ascending=False) 

    # 2. رسم الأعمدة (مع إضافة الأرقام فوق كل عمود)
    fig_bar = px.bar(
        sales_data, 
        x='Product', 
        y='Total_Sales', 
        title=f"Sales by Product - {title_suffix}", 
        color='Product',
        text_auto='.2s', # دي اللي هتكتب الرقم (مثلاً 120K) فوق العمود
        template='plotly_white'
    )
    
    # رسم الأرباح
    fig_pie = px.pie(
        filtered_df, values='Profit', names='Product', 
        title=f"Profit Distribution - {title_suffix}",
        hole=0.4 # جعلها Donut Chart لشكل أحدث
    )
    
    return cards, fig_bar, fig_pie

# ب- تفعيل زرار التحميل (Download Functionality)
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download", "n_clicks"),
    State("branch-dropdown", "value"), # يأخذ الحالة الحالية للفرع المختار
    prevent_initial_call=True,
)
def download_report(n_clicks, selected_branch):
    if selected_branch == 'All':
        export_df = df
        filename = "Global_Sales_Report.csv"
    else:
        export_df = df[df['Branch'] == selected_branch]
        filename = f"{selected_branch}_Sales_Report.csv"
    
    return dcc.send_data_frame(export_df.to_csv, filename, index=False)

if __name__ == '__main__':
    # تشغيل السيرفر على بورت 8051 لتجنب أي تعارض
    app.run(debug=True, port=8051)