# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     # Tablas principales
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER,
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category TEXT, 
#             status TEXT DEFAULT 'pending',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT -- 'points' o 'commission'
#         );
#     ''')
    
#     # Datos iniciales y Reglas por defecto
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Juan Pérez', 1), ('María García', 1)")
        
#         # Reglas por defecto proporcionadas por el usuario
#         default_rules = [
#             # Postpago (Puntos)
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             # Portabilidad (Puntos)
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             # Otros (Puntos)
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             # Comisiones (Dinero)
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE PERSISTENCIA ---
# def get_sellers():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT id, name FROM sellers", conn)
#     conn.close()
#     return df

# def get_all_rules():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value, type FROM point_rules", conn)
#     conn.close()
#     return df

# # --- INTERFAZ DE USUARIO ---
# st.title("🚀 Sistema de Gestión de Ventas")

# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu)

# # --- LÓGICA DE REGISTRO DE VENTA ---
# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
    
#     sellers_df = get_sellers()
#     rules_df = get_all_rules()
    
#     # Separar reglas para la interfaz
#     point_rules = rules_df[rules_df['type'] == 'points']
#     comm_rules = rules_df[rules_df['type'] == 'commission']
    
#     with st.form("venta_form"):
#         col1, col2 = st.columns(2)
        
#         with col1:
#             seller_name = st.selectbox("Selecciona tu nombre", sellers_df['name'].tolist())
#             customer = st.text_input("Nombre del Cliente")
#             date_sale = st.date_input("Fecha de venta", datetime.now())
            
#         with col2:
#             amount = st.number_input("Monto Total de la Boleta ($)", min_value=0.0, step=100.0)
            
#         st.divider()
        
#         col_pts, col_com = st.columns(2)
        
#         with col_pts:
#             st.subheader("Productos (Puntos)")
#             selected_items = st.multiselect(
#                 "Selecciona los productos vendidos",
#                 options=point_rules['item_name'].tolist()
#             )
        
#         with col_com:
#             st.subheader("Extras (Comisión $)")
#             has_insurance = st.checkbox("Incluye Seguro")
#             has_accessory = st.checkbox("Incluye Accesorio")
            
#         # Cálculos dinámicos
#         puntos_totales = point_rules[point_rules['item_name'].isin(selected_items)]['value'].sum()
        
#         comision_total = 0
#         if has_insurance:
#             comision_total += comm_rules[comm_rules['item_name'] == 'Seguro']['value'].values[0]
#         if has_accessory:
#             comision_total += comm_rules[comm_rules['item_name'] == 'Accesorio']['value'].values[0]
            
#         st.info(f"✨ Resumen: **{int(puntos_totales)} Puntos** | **${comision_total:,.0f} en Comisiones**")
        
#         submitted = st.form_submit_button("Guardar Venta")
        
#         if submitted:
#             if not customer:
#                 st.error("Por favor ingresa el nombre del cliente.")
#             else:
#                 seller_id = int(sellers_df[sellers_df['name'] == seller_name]['id'].values[0])
#                 detalle = ", ".join(selected_items)
#                 if has_insurance: detalle += " + Seguro"
#                 if has_accessory: detalle += " + Accesorio"
                
#                 conn = get_connection()
#                 cur = conn.cursor()
#                 cur.execute('''
#                     INSERT INTO sales (date, seller_id, customer_name, total_amount, total_points, total_commission, category)
#                     VALUES (?, ?, ?, ?, ?, ?, ?)
#                 ''', (date_sale.strftime("%Y-%m-%d"), seller_id, customer, amount, puntos_totales, comision_total, detalle))
#                 conn.commit()
#                 conn.close()
#                 st.success("✅ Venta registrada correctamente.")

# # --- LÓGICA DE DASHBOARD ---
# elif choice == "Dashboard":
#     st.header("📊 Resumen de Cumplimiento")
    
#     conn = get_connection()
#     current_month = datetime.now().month
#     current_year = datetime.now().year
    
#     query = f'''
#         SELECT 
#             s.name as Vendedor,
#             COALESCE(SUM(v.total_points), 0) as Puntos_Actuales,
#             COALESCE(SUM(v.total_commission), 0) as Comisiones_CLP,
#             COALESCE(t.target_points, 0) as Meta
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{current_month:02}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {current_month} AND t.year = {current_year}
#         GROUP BY s.id
#     '''
#     df_resumen = pd.read_sql_query(query, conn)
#     conn.close()
    
#     if not df_resumen.empty:
#         for idx, row in df_resumen.iterrows():
#             with st.container(border=True):
#                 col_info, col_bar = st.columns([1, 3])
#                 with col_info:
#                     st.write(f"👤 **{row['Vendedor']}**")
#                     st.write(f"💰 Comisiones: `${row['Comisiones_CLP']:,.0f}`")
#                 with col_bar:
#                     progreso = 0
#                     meta = row['Meta']
#                     if meta > 0:
#                         progreso = min(row['Puntos_Actuales'] / meta, 1.0)
                    
#                     st.progress(progreso)
#                     st.caption(f"Progreso: {int(row['Puntos_Actuales'])} / {int(meta)} puntos ({int(progreso*100)}%)")
#     else:
#         st.info("No hay datos para mostrar en este mes.")

# # --- LÓGICA DE CONFIGURACIÓN ---
# elif choice == "Configuración":
#     st.header("⚙️ Panel de Administración")
    
#     tab1, tab2 = st.tabs(["Metas Mensuales", "Valores de Puntos y Comisiones"])
    
#     with tab1:
#         sellers_df = get_sellers()
#         month = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#         year = st.number_input("Año", value=datetime.now().year)
        
#         for idx, row in sellers_df.iterrows():
#             conn = get_connection()
#             cur = conn.cursor()
#             cur.execute("SELECT target_points FROM targets WHERE seller_id = ? AND month = ? AND year = ?", (row['id'], month, year))
#             res = cur.fetchone()
#             val_existente = res[0] if res else 0
            
#             new_target = st.number_input(f"Meta puntos para {row['name']}", value=val_existente, key=f"t_{row['id']}")
            
#             if st.button(f"Actualizar Meta {row['name']}", key=f"btn_{row['id']}"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points)
#                     VALUES (?, ?, ?, ?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET target_points = excluded.target_points
#                 ''', (row['id'], month, year, new_target))
#                 conn.commit()
#                 st.success(f"Meta de {row['name']} actualizada.")
#             conn.close()

#     with tab2:
#         st.subheader("Editar Valor de Puntos y Comisiones")
#         rules_df = get_all_rules()
        
#         for idx, row in rules_df.iterrows():
#             col_name, col_val, col_btn = st.columns([2, 1, 1])
#             with col_name:
#                 st.write(f"**{row['item_name']}** ({'Puntos' if row['type'] == 'points' else '$'})")
#             with col_val:
#                 new_val = st.number_input("Valor", value=float(row['value']), key=f"rule_{idx}", label_visibility="collapsed")
#             with col_btn:
#                 if st.button("Guardar", key=f"save_rule_{idx}"):
#                     conn = get_connection()
#                     cur = conn.cursor()
#                     cur.execute("UPDATE point_rules SET value = ? WHERE item_name = ?", (new_val, row['item_name']))
#                     conn.commit()
#                     conn.close()
#                     st.rerun()

# elif choice == "Historial":
#     st.header("📋 Historial de Ventas")
#     conn = get_connection()
#     df_sales = pd.read_sql_query('''
#         SELECT v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, 
#             v.total_amount as [Monto Boleta], v.total_points as Puntos, 
#             v.total_commission as [Comisión $], v.category as Detalle
#         FROM sales v
#         JOIN sellers s ON v.seller_id = s.id
#         ORDER BY v.id DESC
#     ''', conn)
#     conn.close()
#     st.dataframe(df_sales, use_container_width=True)



# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     # Tablas principales
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER,
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category TEXT, 
#             status TEXT DEFAULT 'approved',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT -- 'points' o 'commission'
#         );
#     ''')
    
#     # Datos iniciales y Reglas por defecto
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Vendedor de Prueba', 1)")
        
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE PERSISTENCIA ---
# def get_sellers():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT id, name FROM sellers", conn)
#     conn.close()
#     return df

# def get_stores():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT * FROM stores", conn)
#     conn.close()
#     return df

# def get_all_rules():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value, type FROM point_rules", conn)
#     conn.close()
#     return df

# # --- INTERFAZ DE USUARIO ---
# st.sidebar.title("🛠️ Panel de Control")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Ir a:", menu)

# # --- LÓGICA DE REGISTRO DE VENTA ---
# if choice == "Registrar Venta":
#     st.header("📝 Registro de Nueva Venta")
    
#     sellers_df = get_sellers()
#     rules_df = get_all_rules()
    
#     if sellers_df.empty:
#         st.warning("No hay vendedores registrados. Ve a Configuración.")
#     else:
#         point_rules = rules_df[rules_df['type'] == 'points']
#         comm_rules = rules_df[rules_df['type'] == 'commission']
        
#         with st.form("venta_form", clear_on_submit=True):
#             col1, col2 = st.columns(2)
#             with col1:
#                 seller_name = st.selectbox("Vendedor", sellers_df['name'].tolist())
#                 customer = st.text_input("Cliente")
#                 date_sale = st.date_input("Fecha", datetime.now())
#             with col2:
#                 amount = st.number_input("Monto Boleta ($)", min_value=0.0, step=500.0)
            
#             st.divider()
#             col_p, col_c = st.columns(2)
#             with col_p:
#                 st.subheader("Productos")
#                 selected_items = st.multiselect("Selecciona ítems", options=point_rules['item_name'].tolist())
#             with col_c:
#                 st.subheader("Extras")
#                 has_insurance = st.checkbox("Incluye Seguro")
#                 has_accessory = st.checkbox("Incluye Accesorio")
            
#             # Cálculos
#             puntos = point_rules[point_rules['item_name'].isin(selected_items)]['value'].sum()
#             comision = 0
#             if has_insurance: comision += comm_rules[comm_rules['item_name'] == 'Seguro']['value'].values[0]
#             if has_accessory: comision += comm_rules[comm_rules['item_name'] == 'Accesorio']['value'].values[0]
            
#             st.markdown(f"### **Resumen: {int(puntos)} pts | ${comision:,.0f} comisión**")
            
#             if st.form_submit_button("Guardar Venta"):
#                 if not customer:
#                     st.error("Ingresa el nombre del cliente.")
#                 else:
#                     seller_id = int(sellers_df[sellers_df['name'] == seller_name]['id'].values[0])
#                     detalle = ", ".join(selected_items)
#                     if has_insurance: detalle += " [+Seguro]"
#                     if has_accessory: detalle += " [+Acc]"
                    
#                     conn = get_connection()
#                     cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (date, seller_id, customer_name, total_amount, total_points, total_commission, category)
#                         VALUES (?, ?, ?, ?, ?, ?, ?)
#                     ''', (date_sale.strftime("%Y-%m-%d"), seller_id, customer, amount, puntos, comision, detalle))
#                     conn.commit()
#                     conn.close()
#                     st.success("Venta guardada.")

# # --- LÓGICA DE DASHBOARD ---
# elif choice == "Dashboard":
#     st.header("📊 Cumplimiento de Metas")
    
#     col_m, col_y = st.columns(2)
#     with col_m:
#         month = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     with col_y:
#         year = st.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query = f'''
#         SELECT 
#             s.name as Vendedor,
#             COALESCE(SUM(v.total_points), 0) as Puntos,
#             COALESCE(SUM(v.total_commission), 0) as Comision,
#             COALESCE(t.target_points, 0) as Meta
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         GROUP BY s.id
#     '''
#     df = pd.read_sql_query(query, conn)
#     conn.close()

#     if not df.empty:
#         for _, row in df.iterrows():
#             with st.container(border=True):
#                 c1, c2 = st.columns([1, 4])
#                 with c1:
#                     st.subheader(row['Vendedor'])
#                     st.metric("Comisiones", f"${row['Comision']:,.0f}")
#                 with c2:
#                     puntos = row['Puntos']
#                     meta = row['Meta']
#                     porcentaje = min(puntos / meta, 1.0) if meta > 0 else 0.0
#                     st.write(f"**Progreso de Meta:** {int(puntos)} / {int(meta)} puntos")
#                     st.progress(porcentaje)
#                     if puntos >= meta and meta > 0:
#                         st.success("🎯 ¡Meta Alcanzada!")
#     else:
#         st.info("No hay datos registrados.")

# # --- LÓGICA DE CONFIGURACIÓN ---
# elif choice == "Configuración":
#     st.header("⚙️ Administración del Sistema")
#     t1, t2, t3 = st.tabs(["Metas", "Puntos/Valores", "Personal y Tiendas"])
    
#     with t1:
#         st.subheader("Establecer Metas del Mes")
#         sellers_df = get_sellers()
#         m = st.selectbox("Mes Meta", range(1, 13), index=datetime.now().month - 1, key="ms")
#         y = st.number_input("Año Meta", value=datetime.now().year, key="ys")
        
#         for _, row in sellers_df.iterrows():
#             conn = get_connection()
#             cur = conn.cursor()
#             cur.execute("SELECT target_points FROM targets WHERE seller_id=? AND month=? AND year=?", (row['id'], m, y))
#             res = cur.fetchone()
#             val = res[0] if res else 0
            
#             new_t = st.number_input(f"Meta para {row['name']}", value=val, key=f"meta_{row['id']}")
#             if st.button(f"Guardar Meta {row['name']}", key=f"btn_meta_{row['id']}"):
#                 cur.execute("INSERT INTO targets (seller_id, month, year, target_points) VALUES (?,?,?,?) ON CONFLICT(seller_id, month, year) DO UPDATE SET target_points=excluded.target_points", (row['id'], m, y, new_t))
#                 conn.commit()
#                 st.toast(f"Meta de {row['name']} actualizada")
#             conn.close()

#     with t2:
#         st.subheader("Valores de Puntos y Comisiones")
#         rules_df = get_all_rules()
#         for i, row in rules_df.iterrows():
#             c_n, c_v, c_b = st.columns([3, 2, 1])
#             with c_n: st.write(row['item_name'])
#             with c_v: new_v = st.number_input("Valor", value=float(row['value']), key=f"v_{i}", label_visibility="collapsed")
#             with c_b:
#                 if st.button("💾", key=f"s_{i}"):
#                     conn = get_connection(); cur = conn.cursor()
#                     cur.execute("UPDATE point_rules SET value=? WHERE item_name=?", (new_v, row['item_name']))
#                     conn.commit(); conn.close(); st.rerun()

#     with t3:
#         st.subheader("Gestión de Vendedores")
#         with st.form("add_seller"):
#             new_s_name = st.text_input("Nombre del Vendedor")
#             if st.form_submit_button("Agregar Vendedor") and new_s_name:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_s_name,))
#                 conn.commit(); conn.close(); st.rerun()
        
#         sellers_df = get_sellers()
#         for _, s in sellers_df.iterrows():
#             col_s, col_d = st.columns([4, 1])
#             col_s.write(s['name'])
#             if col_d.button("🗑️", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id=?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()

# elif choice == "Historial":
#     st.header("📋 Historial de Ventas")
#     conn = get_connection()
#     df = pd.read_sql_query('''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, 
#             v.total_points as Puntos, v.total_commission as [Comisión $], v.category as Detalle
#         FROM sales v JOIN sellers s ON v.seller_id = s.id ORDER BY v.id DESC
#     ''', conn)
    
#     if not df.empty:
#         st.dataframe(df.drop(columns=['id']), use_container_width=True)
#         id_to_del = st.number_input("ID de venta para eliminar", min_value=1, step=1)
#         if st.button("Eliminar Registro Permanentemente"):
#             cur = conn.cursor()
#             cur.execute("DELETE FROM sales WHERE id=?", (id_to_del,))
#             conn.commit(); st.rerun()
#     else:
#         st.info("No hay ventas registradas.")
#     conn.close()






# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     # Tablas principales (Añadimos columnas para IMEI y Teléfono para simplificar el acceso)
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER,
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category TEXT, 
#             imei TEXT,
#             device_name TEXT,
#             phone_number TEXT,
#             status TEXT DEFAULT 'approved',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     # Datos iniciales y Reglas por defecto
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Vendedor de Prueba', 1)")
        
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE PERSISTENCIA ---
# def get_sellers():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT id, name FROM sellers", conn)
#     conn.close()
#     return df

# def get_all_rules():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value, type FROM point_rules", conn)
#     conn.close()
#     return df

# # --- INTERFAZ DE USUARIO ---
# st.sidebar.title("🛠️ Panel de Control")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Ir a:", menu)

# # --- LÓGICA DE REGISTRO DE VENTA ---
# if choice == "Registrar Venta":
#     st.header("📝 Registro de Nueva Venta")
    
#     sellers_df = get_sellers()
#     rules_df = get_all_rules()
    
#     if sellers_df.empty:
#         st.warning("No hay vendedores registrados. Ve a Configuración.")
#     else:
#         point_rules = rules_df[rules_df['type'] == 'points']
#         comm_rules = rules_df[rules_df['type'] == 'commission']
        
#         with st.form("venta_form", clear_on_submit=True):
#             col1, col2 = st.columns(2)
#             with col1:
#                 seller_name = st.selectbox("Vendedor", sellers_df['name'].tolist())
#                 customer = st.text_input("Nombre del Cliente")
#                 date_sale = st.date_input("Fecha", datetime.now())
#             with col2:
#                 amount = st.number_input("Monto Boleta ($)", min_value=0.0, step=500.0)
            
#             st.divider()
#             col_p, col_c = st.columns(2)
#             with col_p:
#                 st.subheader("Productos")
#                 selected_items = st.multiselect("Selecciona ítems", options=point_rules['item_name'].tolist())
            
#             with col_c:
#                 st.subheader("Extras")
#                 has_insurance = st.checkbox("Incluye Seguro")
#                 has_accessory = st.checkbox("Incluye Accesorio")

#             # --- SECCIÓN DINÁMICA SEGÚN SELECCIÓN ---
#             imei_val = ""
#             device_val = ""
#             phone_val = ""
            
#             # Si se selecciona algo que requiera IMEI (Equipos/Renovación)
#             if any(x in ["Equipo Prepago", "Equipo Voz", "Equipo Datos", "Renovación"] for x in selected_items):
#                 st.subheader("Detalles del Equipo")
#                 c_d1, c_d2 = st.columns(2)
#                 device_val = c_d1.text_input("Modelo del Equipo")
#                 imei_val = c_d2.text_input("IMEI (15 dígitos)")

#             # Si se selecciona algo que requiera Número (Postpago/Porta/Migra)
#             if any(x in ["Portabilidad: Pre-Post", "Portabilidad: Post-Post", "Migración", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer"] for x in selected_items):
#                 st.subheader("Detalles de Línea")
#                 phone_val = st.text_input("Número de Teléfono (Ej: 912345678)")

#             # Cálculos
#             puntos = point_rules[point_rules['item_name'].isin(selected_items)]['value'].sum()
#             comision = 0
#             if has_insurance: comision += comm_rules[comm_rules['item_name'] == 'Seguro']['value'].values[0]
#             if has_accessory: comision += comm_rules[comm_rules['item_name'] == 'Accesorio']['value'].values[0]
            
#             st.markdown(f"### **Resumen: {int(puntos)} pts | ${comision:,.0f} comisión**")
            
#             if st.form_submit_button("Guardar Venta"):
#                 if not customer:
#                     st.error("Ingresa el nombre del cliente.")
#                 else:
#                     seller_id = int(sellers_df[sellers_df['name'] == seller_name]['id'].values[0])
#                     detalle = ", ".join(selected_items)
#                     if has_insurance: detalle += " [+Seguro]"
#                     if has_accessory: detalle += " [+Acc]"
                    
#                     conn = get_connection()
#                     cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (date, seller_id, customer_name, total_amount, total_points, total_commission, category, imei, device_name, phone_number)
#                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                     ''', (date_sale.strftime("%Y-%m-%d"), seller_id, customer, amount, puntos, comision, detalle, imei_val, device_val, phone_val))
#                     conn.commit()
#                     conn.close()
#                     st.success("Venta guardada exitosamente.")

# # --- LÓGICA DE DASHBOARD ---
# elif choice == "Dashboard":
#     st.header("📊 Cumplimiento de Metas")
    
#     col_m, col_y = st.columns(2)
#     with col_m:
#         month = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     with col_y:
#         year = st.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query = f'''
#         SELECT 
#             s.name as Vendedor,
#             COALESCE(SUM(v.total_points), 0) as Puntos,
#             COALESCE(SUM(v.total_commission), 0) as Comision,
#             COALESCE(t.target_points, 0) as Meta
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         GROUP BY s.id
#     '''
#     df = pd.read_sql_query(query, conn)
#     conn.close()

#     if not df.empty:
#         for _, row in df.iterrows():
#             with st.container(border=True):
#                 c1, c2 = st.columns([1, 4])
#                 with c1:
#                     st.subheader(row['Vendedor'])
#                     st.metric("Comisiones", f"${row['Comision']:,.0f}")
#                 with c2:
#                     puntos = row['Puntos']
#                     meta = row['Meta']
#                     porcentaje = min(puntos / meta, 1.0) if meta > 0 else 0.0
#                     st.write(f"**Progreso de Meta:** {int(puntos)} / {int(meta)} puntos")
#                     st.progress(porcentaje)
#                     if puntos >= meta and meta > 0:
#                         st.success("🎯 ¡Meta Alcanzada!")
#     else:
#         st.info("No hay datos registrados para este periodo.")

# # --- LÓGICA DE CONFIGURACIÓN ---
# elif choice == "Configuración":
#     st.header("⚙️ Administración del Sistema")
#     t1, t2, t3 = st.tabs(["Metas Mensuales", "Valores de Puntos", "Personal y Tiendas"])
    
#     with t1:
#         st.subheader("Establecer Metas del Mes")
#         sellers_df = get_sellers()
#         m = st.selectbox("Mes Meta", range(1, 13), index=datetime.now().month - 1, key="ms")
#         y = st.number_input("Año Meta", value=datetime.now().year, key="ys")
        
#         for _, row in sellers_df.iterrows():
#             conn = get_connection()
#             cur = conn.cursor()
#             cur.execute("SELECT target_points FROM targets WHERE seller_id=? AND month=? AND year=?", (row['id'], m, y))
#             res = cur.fetchone()
#             val = res[0] if res else 0
            
#             new_t = st.number_input(f"Meta para {row['name']}", value=val, key=f"meta_{row['id']}")
#             if st.button(f"Guardar Meta {row['name']}", key=f"btn_meta_{row['id']}"):
#                 cur.execute("INSERT INTO targets (seller_id, month, year, target_points) VALUES (?,?,?,?) ON CONFLICT(seller_id, month, year) DO UPDATE SET target_points=excluded.target_points", (row['id'], m, y, new_t))
#                 conn.commit()
#                 st.toast(f"Meta de {row['name']} actualizada")
#             conn.close()

#     with t2:
#         st.subheader("Valores de Puntos y Comisiones")
#         rules_df = get_all_rules()
#         for i, row in rules_df.iterrows():
#             c_n, c_v, c_b = st.columns([3, 2, 1])
#             with c_n: st.write(row['item_name'])
#             with c_v: new_v = st.number_input("Valor", value=float(row['value']), key=f"v_{i}", label_visibility="collapsed")
#             with c_b:
#                 if st.button("💾", key=f"s_{i}"):
#                     conn = get_connection(); cur = conn.cursor()
#                     cur.execute("UPDATE point_rules SET value=? WHERE item_name=?", (new_v, row['item_name']))
#                     conn.commit(); conn.close(); st.rerun()

#     with t3:
#         st.subheader("Gestión de Vendedores")
#         with st.form("add_seller"):
#             new_s_name = st.text_input("Nombre del Nuevo Vendedor")
#             if st.form_submit_button("Agregar Vendedor") and new_s_name:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_s_name,))
#                 conn.commit(); conn.close(); st.rerun()
        
#         sellers_df = get_sellers()
#         for _, s in sellers_df.iterrows():
#             col_s, col_d = st.columns([4, 1])
#             col_s.write(s['name'])
#             if col_d.button("🗑️", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id=?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()

# elif choice == "Historial":
#     st.header("📋 Historial Detallado de Ventas")
#     conn = get_connection()
#     df = pd.read_sql_query('''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, 
#                v.total_points as Puntos, v.total_commission as [Comisión $], v.category as Detalle,
#                v.device_name as Equipo, v.imei as IMEI, v.phone_number as [Teléfono]
#         FROM sales v JOIN sellers s ON v.seller_id = s.id ORDER BY v.id DESC
#     ''', conn)
    
#     if not df.empty:
#         # Mostramos la tabla con los nuevos campos de IMEI y Teléfono
#         st.dataframe(df.drop(columns=['id']), use_container_width=True)
        
#         st.divider()
#         st.subheader("Acciones de Historial")
#         col_del, col_exp = st.columns([2, 2])
        
#         with col_del:
#             id_to_del = st.number_input("ID de venta para eliminar", min_value=1, step=1)
#             if st.button("Eliminar Registro Permanentemente", type="secondary"):
#                 cur = conn.cursor()
#                 cur.execute("DELETE FROM sales WHERE id=?", (id_to_del,))
#                 conn.commit(); st.rerun()
        
#         with col_exp:
#             # Opción simple de exportar a CSV para sustituir el Drive
#             csv = df.to_csv(index=False).encode('utf-8')
#             st.download_button(
#                 label="Descargar Historial (CSV)",
#                 data=csv,
#                 file_name=f'ventas_{datetime.now().strftime("%Y%m%d")}.csv',
#                 mime='text/csv',
#             )
#     else:
#         st.info("No hay ventas registradas.")
#     conn.close()










# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     # Tablas principales con todos los campos necesarios para sustituir el Drive
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER,
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category_summary TEXT, 
            
#             -- Campos específicos de Línea
#             phone_number TEXT,
#             iccid TEXT,
            
#             -- Campos específicos de Equipo
#             device_name TEXT,
#             imei TEXT,
#             has_insurance INTEGER DEFAULT 0,
            
#             -- Campos específicos de Accesorios
#             accessory_name TEXT,
#             accessory_code TEXT,
            
#             -- Campos específicos de Fibra
#             fiber_plan TEXT,
#             fiber_address TEXT,
            
#             status TEXT DEFAULT 'approved',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     # Datos iniciales y Reglas por defecto
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Vendedor de Prueba', 1)")
        
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE APOYO ---
# def get_sellers():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT id, name FROM sellers", conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- INTERFAZ ---
# st.sidebar.title("🛠️ Sales Manager")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu)

# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.error("Debe configurar vendedores primero.")
#     else:
#         with st.form("main_form", clear_on_submit=True):
#             # 1. Datos Generales
#             col_g1, col_g2, col_g3 = st.columns(3)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()

#             # 2. Agrupación de Productos
#             # --- SECCIÓN A: LÍNEAS (Porta, Postpago, Extras) ---
#             st.subheader("📱 Telefonía / Líneas")
#             col_a1, col_a2, col_a3 = st.columns(3)
#             with col_a1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_a2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_a3:
#                 tipo_extra = st.selectbox("Otros Planes", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"]) # Prepago aquí según instrucción

#             # Campos condicionales para Líneas
#             phone_val = ""
#             iccid_val = ""
#             if any(x != "No aplica" for x in [tipo_porta, tipo_post, tipo_extra]):
#                 c_l1, c_l2 = st.columns(2)
#                 phone_val = c_l1.text_input("Número de Teléfono")
#                 iccid_val = c_l2.text_input("ICCID de la SIM")

#             st.divider()

#             # --- SECCIÓN B: EQUIPOS ---
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2 = st.columns(2)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Venta de Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 # El seguro queda asociado al equipo
#                 ins_check = st.checkbox("¿Incluye Seguro? (Comisión $)")

#             device_name = ""
#             imei_val = ""
#             if tipo_equipo != "No aplica":
#                 c_e1, c_e2 = st.columns(2)
#                 device_name = c_e1.text_input("Modelo del Equipo")
#                 imei_val = c_e2.text_input("IMEI")

#             st.divider()

#             # --- SECCIÓN C: ACCESORIOS Y FIBRA ---
#             st.subheader("🔌 Accesorios y 🌐 Fibra")
#             col_c1, col_c2 = st.columns(2)
            
#             with col_c1:
#                 acc_check = st.checkbox("¿Venta de Accesorio?")
#                 acc_name = ""
#                 acc_code = ""
#                 if acc_check:
#                     acc_name = st.text_input("Nombre del Accesorio")
#                     acc_code = st.text_input("Código del Accesorio")
            
#             with col_c2:
#                 fibra_check = st.selectbox("Venta de Fibra", ["No aplica", "Fibra"])
#                 fib_plan = ""
#                 fib_addr = ""
#                 if fibra_check != "No aplica":
#                     fib_plan = st.text_input("Plan de Fibra")
#                     fib_addr = st.text_input("Dirección de Instalación")

#             st.divider()
            
#             # 3. Monto y Cálculo
#             amount = st.number_input("Monto Total Boleta ($)", min_value=0.0, step=500.0)
            
#             # --- Lógica de Cálculo de Puntos ---
#             items_seleccionados = []
#             if tipo_porta != "No aplica": items_seleccionados.append(tipo_porta)
#             if tipo_post != "No aplica": items_seleccionados.append(tipo_post)
#             if tipo_extra != "No aplica": items_seleccionados.append(tipo_extra)
#             if tipo_equipo != "No aplica": items_seleccionados.append(tipo_equipo)
#             if fibra_check != "No aplica": items_seleccionados.append(fibra_check)
            
#             puntos_totales = sum(rules.get(item, 0) for item in items_seleccionados)
#             comision_total = 0
#             if ins_check: comision_total += rules.get("Seguro", 1500)
#             if acc_check: comision_total += rules.get("Accesorio", 1000)
            
#             st.markdown(f"### Resumen: **{int(puntos_totales)} Puntos** | **${comision_total:,.0f} Comisión**")
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
            
#             if submit:
#                 if not customer:
#                     st.error("El nombre del cliente es obligatorio.")
#                 else:
#                     summary = ", ".join(items_seleccionados)
#                     conn = get_connection()
#                     cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (
#                             date, seller_id, customer_name, total_amount, total_points, total_commission, 
#                             category_summary, phone_number, iccid, device_name, imei, has_insurance,
#                             accessory_name, accessory_code, fiber_plan, fiber_address
#                         ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                     ''', (
#                         sale_date.strftime("%Y-%m-%d"), seller_id, customer, amount, puntos_totales, comision_total,
#                         summary, phone_val, iccid_val, device_name, imei_val, (1 if ins_check else 0),
#                         acc_name, acc_code, fib_plan, fib_addr
#                     ))
#                     conn.commit()
#                     conn.close()
#                     st.success("¡Venta registrada con éxito!")
#                     st.balloons()

# elif choice == "Dashboard":
#     st.header("📊 Cumplimiento de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query = f'''
#         SELECT s.name as Vendedor, COALESCE(SUM(v.total_points), 0) as Puntos,
#                COALESCE(SUM(v.total_commission), 0) as Comision, COALESCE(t.target_points, 0) as Meta
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         GROUP BY s.id
#     '''
#     df = pd.read_sql_query(query, conn)
#     conn.close()

#     for _, row in df.iterrows():
#         with st.container(border=True):
#             c1, c2 = st.columns([1, 4])
#             c1.metric(row['Vendedor'], f"{int(row['Puntos'])} pts")
#             c1.write(f"💰 Com: ${row['Comision']:,.0f}")
            
#             meta = row['Meta']
#             prog = min(row['Puntos'] / meta, 1.0) if meta > 0 else 0.0
#             c2.write(f"Meta: {int(meta)} puntos")
#             c2.progress(prog)
#             if row['Puntos'] >= meta and meta > 0:
#                 c2.caption("✅ ¡Meta alcanzada!")

# elif choice == "Historial":
#     st.header("📋 Historial de Ventas")
#     conn = get_connection()
#     df = pd.read_sql_query('''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, 
#                v.total_points as Pts, v.total_commission as [$], v.category_summary as Resumen,
#                v.phone_number, v.device_name as Equipo, v.imei, v.fiber_plan as [Plan Fibra]
#         FROM sales v JOIN sellers s ON v.seller_id = s.id ORDER BY v.id DESC
#     ''', conn)
#     conn.close()
    
#     if not df.empty:
#         st.dataframe(df, use_container_width=True)
#         csv = df.to_csv(index=False).encode('utf-8')
#         st.download_button("📥 Descargar Excel (CSV)", csv, "ventas.csv", "text/csv")
#     else:
#         st.info("No hay registros.")

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2 = st.tabs(["Vendedores y Metas", "Reglas de Puntos"])
    
#     with t1:
#         st.subheader("Agregar Vendedor")
#         with st.form("new_seller"):
#             name = st.text_input("Nombre completo")
#             if st.form_submit_button("Añadir") and name:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (name,))
#                 conn.commit(); conn.close(); st.rerun()
        
#         st.subheader("Metas Mensuales")
#         sellers = get_sellers()
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="mt")
#         y_t = st.number_input("Año", value=2025, key="yt")
        
#         for _, s in sellers.iterrows():
#             conn = get_connection(); cur = conn.cursor()
#             cur.execute("SELECT target_points FROM targets WHERE seller_id=? AND month=? AND year=?", (s['id'], m_t, y_t))
#             res = cur.fetchone()
#             val = res[0] if res else 0
            
#             new_m = st.number_input(f"Meta para {s['name']}", value=val)
#             if st.button(f"Guardar Meta {s['name']}"):
#                 cur.execute("INSERT INTO targets (seller_id, month, year, target_points) VALUES (?,?,?,?) ON CONFLICT(seller_id, month, year) DO UPDATE SET target_points=excluded.target_points", (s['id'], m_t, y_t, new_m))
#                 conn.commit(); conn.close(); st.success("Meta guardada")

#     with t2:
#         st.subheader("Editar Valores")
#         conn = get_connection()
#         rules_df = pd.read_sql_query("SELECT * FROM point_rules", conn)
#         for i, r in rules_df.iterrows():
#             c1, c2, c3 = st.columns([3, 2, 1])
#             c1.write(r['item_name'])
#             new_v = c2.number_input("Valor", value=float(r['value']), key=f"r{i}", label_visibility="collapsed")
#             if c3.button("💾", key=f"b{i}"):
#                 cur = conn.cursor()
#                 cur.execute("UPDATE point_rules SET value=? WHERE id=?", (new_v, r['id']))
#                 conn.commit(); conn.close(); st.rerun()







# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     # Tablas principales con todos los campos necesarios para sustituir el Drive
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER,
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category_summary TEXT, 
            
#             -- Campos específicos de Línea
#             phone_number TEXT,
#             iccid TEXT,
            
#             -- Campos específicos de Equipo
#             device_name TEXT,
#             imei TEXT,
#             has_insurance INTEGER DEFAULT 0,
            
#             -- Campos específicos de Accesorios
#             accessory_name TEXT,
#             accessory_code TEXT,
            
#             -- Campos específicos de Fibra
#             fiber_plan TEXT,
#             fiber_address TEXT,
            
#             -- Campos de Pago y Documento
#             doc_type TEXT,
#             doc_number TEXT,
#             payment_method TEXT,
            
#             status TEXT DEFAULT 'approved',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     # Datos iniciales y Reglas por defecto
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Vendedor de Prueba', 1)")
        
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE APOYO ---
# def get_sellers():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT id, name FROM sellers", conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- INTERFAZ ---
# st.sidebar.title("🛠️ Sales Manager")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu)

# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.error("Debe configurar vendedores primero.")
#     else:
#         # Usamos el formulario principal
#         with st.form("main_form", clear_on_submit=True):
#             # 1. Datos Generales
#             col_g1, col_g2, col_g3 = st.columns(3)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()

#             # 2. Agrupación de Productos
#             # --- SECCIÓN A: LÍNEAS ---
#             st.subheader("📱 Telefonía / Líneas")
#             col_a1, col_a2, col_a3 = st.columns(3)
#             with col_a1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_a2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_a3:
#                 tipo_extra = st.selectbox("Otros Planes", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             # Campos condicionales para Líneas (ahora se guardan en variables de estado del form)
#             phone_val = st.text_input("Número de Teléfono (Si aplica)")
#             iccid_val = st.text_input("ICCID de la SIM (Si aplica)")

#             st.divider()

#             # --- SECCIÓN B: EQUIPOS ---
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2 = st.columns(2)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Venta de Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 ins_check = st.checkbox("¿Incluye Seguro?")

#             device_name = st.text_input("Modelo del Equipo (Si aplica)")
#             imei_val = st.text_input("IMEI (Si aplica)")

#             st.divider()

#             # --- SECCIÓN C: ACCESORIOS (Separado) ---
#             st.subheader("🔌 Accesorios")
#             acc_check = st.checkbox("¿Venta de Accesorio?")
#             col_acc1, col_acc2 = st.columns(2)
#             with col_acc1:
#                 acc_name = st.text_input("Nombre del Accesorio")
#             with col_acc2:
#                 acc_code = st.text_input("Código del Accesorio")

#             st.divider()

#             # --- SECCIÓN D: FIBRA (Separado) ---
#             st.subheader("🌐 Fibra Óptica")
#             fibra_check = st.selectbox("Venta de Fibra", ["No aplica", "Fibra"])
#             col_fib1, col_fib2 = st.columns(2)
#             with col_fib1:
#                 fib_plan = st.text_input("Plan de Fibra")
#             with col_fib2:
#                 fib_addr = st.text_input("Dirección de Instalación")

#             st.divider()
            
#             # --- SECCIÓN E: DATOS DE DOCUMENTO Y PAGO ---
#             st.subheader("💳 Información de Pago y Documento")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_type = st.selectbox("Tipo de Documento", ["Boleta", "Guía", "Factura"])
#             with col_p2:
#                 doc_number = st.text_input("Número de Documento")
#             with col_p3:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             # --- Lógica de Cálculo de Puntos ---
#             items_seleccionados = []
#             if tipo_porta != "No aplica": items_seleccionados.append(tipo_porta)
#             if tipo_post != "No aplica": items_seleccionados.append(tipo_post)
#             if tipo_extra != "No aplica": items_seleccionados.append(tipo_extra)
#             if tipo_equipo != "No aplica": items_seleccionados.append(tipo_equipo)
#             if fibra_check != "No aplica": items_seleccionados.append(fibra_check)
            
#             puntos_totales = sum(rules.get(item, 0) for item in items_seleccionados)
#             comision_total = 0
#             if ins_check: comision_total += rules.get("Seguro", 1500)
#             if acc_check: comision_total += rules.get("Accesorio", 1000)
            
#             st.markdown(f"### Estimación: **{int(puntos_totales)} Puntos** | **${comision_total:,.0f} Comisión**")
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
            
#             if submit:
#                 if not customer:
#                     st.error("El nombre del cliente es obligatorio.")
#                 elif not doc_number:
#                     st.error("El número de documento es obligatorio.")
#                 else:
#                     summary = ", ".join(items_seleccionados)
#                     conn = get_connection()
#                     cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (
#                             date, seller_id, customer_name, total_amount, total_points, total_commission, 
#                             category_summary, phone_number, iccid, device_name, imei, has_insurance,
#                             accessory_name, accessory_code, fiber_plan, fiber_address,
#                             doc_type, doc_number, payment_method
#                         ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                     ''', (
#                         sale_date.strftime("%Y-%m-%d"), seller_id, customer, amount, puntos_totales, comision_total,
#                         summary, phone_val, iccid_val, device_name, imei_val, (1 if ins_check else 0),
#                         acc_name, acc_code, fib_plan, fib_addr,
#                         doc_type, doc_number, payment_method
#                     ))
#                     conn.commit()
#                     conn.close()
#                     st.success(f"Venta registrada: {doc_type} N°{doc_number}")
#                     st.balloons()

# elif choice == "Dashboard":
#     st.header("📊 Cumplimiento de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query = f'''
#         SELECT s.name as Vendedor, COALESCE(SUM(v.total_points), 0) as Puntos,
#                COALESCE(SUM(v.total_commission), 0) as Comision, COALESCE(t.target_points, 0) as Meta
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         GROUP BY s.id
#     '''
#     df = pd.read_sql_query(query, conn)
#     conn.close()

#     for _, row in df.iterrows():
#         with st.container(border=True):
#             c1, c2 = st.columns([1, 4])
#             c1.metric(row['Vendedor'], f"{int(row['Puntos'])} pts")
#             c1.write(f"💰 Com: ${row['Comision']:,.0f}")
            
#             meta = row['Meta']
#             prog = min(row['Puntos'] / meta, 1.0) if meta > 0 else 0.0
#             c2.write(f"Meta: {int(meta)} puntos")
#             c2.progress(prog)
#             if row['Puntos'] >= meta and meta > 0:
#                 c2.caption("✅ ¡Meta alcanzada!")

# elif choice == "Historial":
#     st.header("📋 Historial de Ventas")
#     conn = get_connection()
#     df = pd.read_sql_query('''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, 
#                v.doc_type as Tipo, v.doc_number as [N° Doc], v.payment_method as Pago,
#                v.total_amount as [Monto $], v.total_points as Pts, v.category_summary as Resumen
#         FROM sales v JOIN sellers s ON v.seller_id = s.id ORDER BY v.id DESC
#     ''', conn)
#     conn.close()
    
#     if not df.empty:
#         st.dataframe(df, use_container_width=True)
#         csv = df.to_csv(index=False).encode('utf-8')
#         st.download_button("📥 Descargar Excel (CSV)", csv, "ventas.csv", "text/csv")
#     else:
#         st.info("No hay registros.")

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2 = st.tabs(["Vendedores y Metas", "Reglas de Puntos"])
    
#     with t1:
#         st.subheader("Agregar Vendedor")
#         with st.form("new_seller"):
#             name = st.text_input("Nombre completo")
#             if st.form_submit_button("Añadir") and name:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (name,))
#                 conn.commit(); conn.close(); st.rerun()
        
#         st.subheader("Metas Mensuales")
#         sellers = get_sellers()
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="mt")
#         y_t = st.number_input("Año", value=2025, key="yt")
        
#         for _, s in sellers.iterrows():
#             conn = get_connection(); cur = conn.cursor()
#             cur.execute("SELECT target_points FROM targets WHERE seller_id=? AND month=? AND year=?", (s['id'], m_t, y_t))
#             res = cur.fetchone()
#             val = res[0] if res else 0
            
#             new_m = st.number_input(f"Meta para {s['name']}", value=val)
#             if st.button(f"Guardar Meta {s['name']}"):
#                 cur.execute("INSERT INTO targets (seller_id, month, year, target_points) VALUES (?,?,?,?) ON CONFLICT(seller_id, month, year) DO UPDATE SET target_points=excluded.target_points", (s['id'], m_t, y_t, new_m))
#                 conn.commit(); conn.close(); st.success("Meta guardada")

#     with t2:
#         st.subheader("Editar Valores")
#         conn = get_connection()
#         rules_df = pd.read_sql_query("SELECT * FROM point_rules", conn)
#         for i, r in rules_df.iterrows():
#             c1, c2, c3 = st.columns([3, 2, 1])
#             c1.write(r['item_name'])
#             new_v = c2.number_input("Valor", value=float(r['value']), key=f"r{i}", label_visibility="collapsed")
#             if c3.button("💾", key=f"b{i}"):
#                 cur = conn.cursor()
#                 cur.execute("UPDATE point_rules SET value=? WHERE id=?", (new_v, r['id']))
#                 conn.commit(); conn.close(); st.rerun()







# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     # Tablas principales actualizadas
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         -- Tabla de metas extendida para cubrir todos los KPIs solicitados
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER, -- 0 para meta GRUPAL de la tienda
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             target_postpago INTEGER DEFAULT 0,
#             target_portabilidad INTEGER DEFAULT 0,
#             target_fibra INTEGER DEFAULT 0,
#             target_seguro INTEGER DEFAULT 0,
#             target_renovacion INTEGER DEFAULT 0,
#             target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             customer_rut TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category_summary TEXT, 
            
#             phone_number TEXT,
#             iccid TEXT,
#             device_name TEXT,
#             imei TEXT,
#             has_insurance INTEGER DEFAULT 0,
#             accessory_name TEXT,
#             accessory_code TEXT,
#             fiber_plan TEXT,
#             fiber_address TEXT,
            
#             doc_type TEXT,
#             doc_number TEXT,
#             payment_method TEXT,
            
#             status TEXT DEFAULT 'approved',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     # Datos iniciales y Reglas por defecto
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Vendedor de Prueba', 1)")
        
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE APOYO ---
# def get_sellers():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT id, name FROM sellers", conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- INTERFAZ ---
# st.sidebar.title("🛠️ Sales Manager")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu)

# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.error("Debe configurar vendedores primero.")
#     else:
#         with st.form("main_form", clear_on_submit=True):
#             # 1. Datos Generales
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()

#             # 2. Agrupación de Productos
#             st.subheader("📱 Telefonía / Líneas")
#             col_a1, col_a2, col_a3 = st.columns(3)
#             with col_a1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_a2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_a3:
#                 tipo_extra = st.selectbox("Otros Planes", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             phone_val = st.text_input("Número de Teléfono (Si aplica)")
#             iccid_val = st.text_input("ICCID de la SIM (Si aplica)")

#             st.divider()

#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2 = st.columns(2)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Venta de Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 ins_check = st.checkbox("¿Incluye Seguro?")

#             device_name = st.text_input("Modelo del Equipo (Si aplica)")
#             imei_val = st.text_input("IMEI (Si aplica)")

#             st.divider()

#             st.subheader("🔌 Accesorios")
#             acc_check = st.checkbox("¿Venta de Accesorio?")
#             col_acc1, col_acc2 = st.columns(2)
#             with col_acc1:
#                 acc_name = st.text_input("Nombre del Accesorio")
#             with col_acc2:
#                 acc_code = st.text_input("Código del Accesorio")

#             st.divider()

#             st.subheader("🌐 Fibra Óptica")
#             fibra_check = st.selectbox("Venta de Fibra", ["No aplica", "Fibra"])
#             col_fib1, col_fib2 = st.columns(2)
#             with col_fib1:
#                 fib_plan = st.text_input("Plan de Fibra")
#             with col_fib2:
#                 fib_addr = st.text_input("Dirección de Instalación")

#             st.divider()
            
#             st.subheader("💳 Información de Pago y Documento")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_type = st.selectbox("Tipo de Documento", ["Boleta", "Guía", "Factura"])
#             with col_p2:
#                 doc_number = st.text_input("Número de Documento")
#             with col_p3:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             # Cálculo de Puntos
#             items_seleccionados = []
#             if tipo_porta != "No aplica": items_seleccionados.append(tipo_porta)
#             if tipo_post != "No aplica": items_seleccionados.append(tipo_post)
#             if tipo_extra != "No aplica": items_seleccionados.append(tipo_extra)
#             if tipo_equipo != "No aplica": items_seleccionados.append(tipo_equipo)
#             if fibra_check != "No aplica": items_seleccionados.append(fibra_check)
            
#             puntos_totales = sum(rules.get(item, 0) for item in items_seleccionados)
#             comision_total = 0
#             if ins_check: comision_total += rules.get("Seguro", 1500)
#             if acc_check: comision_total += rules.get("Accesorio", 1000)
            
#             st.markdown(f"### Estimación: **{int(puntos_totales)} Puntos** | **${comision_total:,.0f} Comisión**")
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
            
#             if submit:
#                 if not customer or not customer_rut:
#                     st.error("Nombre y RUT del cliente son obligatorios.")
#                 elif not doc_number:
#                     st.error("El número de documento es obligatorio.")
#                 else:
#                     summary = ", ".join(items_seleccionados)
#                     conn = get_connection()
#                     cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (
#                             date, seller_id, customer_name, customer_rut, total_amount, total_points, total_commission, 
#                             category_summary, phone_number, iccid, device_name, imei, has_insurance,
#                             accessory_name, accessory_code, fiber_plan, fiber_address,
#                             doc_type, doc_number, payment_method
#                         ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                     ''', (
#                         sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, amount, puntos_totales, comision_total,
#                         summary, phone_val, iccid_val, device_name, imei_val, (1 if ins_check else 0),
#                         acc_name, acc_code, fib_plan, fib_addr,
#                         doc_type, doc_number, payment_method
#                     ))
#                     conn.commit()
#                     conn.close()
#                     st.success(f"Venta registrada: {doc_type} N°{doc_number}")
#                     st.balloons()

# elif choice == "Dashboard":
#     st.header("📊 Dashboard de Metas y Cumplimiento")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
    
#     # 1. Metas Grupales (Tienda)
#     st.subheader("🏢 Resumen Grupal (Tienda)")
#     query_grupal = f'''
#         SELECT 
#             SUM(total_points) as total_pts,
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as total_post,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as total_porta,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as total_fibra,
#             SUM(has_insurance) as total_seguros,
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as total_renov,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as total_womgo
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}'
#     '''
#     res_actual = pd.read_sql_query(query_grupal, conn).iloc[0]
    
#     # Obtener metas grupales (seller_id = 0)
#     meta_grupal = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_grupal.empty:
#         m = meta_grupal.iloc[0]
#         cols = st.columns(4)
#         cols[0].metric("Puntos Tienda", f"{int(res_actual['total_pts'] or 0)}", f"Meta: {m['target_points']}")
#         cols[1].metric("Postpagos", f"{int(res_actual['total_post'] or 0)}", f"Meta: {m['target_postpago']}")
#         cols[2].metric("Portabilidades", f"{int(res_actual['total_porta'] or 0)}", f"Meta: {m['target_portabilidad']}")
#         cols[3].metric("Fibra", f"{int(res_actual['total_fibra'] or 0)}", f"Meta: {m['target_fibra']}")
#     else:
#         st.warning("No hay metas grupales configuradas para este periodo.")

#     st.divider()
    
#     # 2. Resumen Individual por Vendedor
#     st.subheader("👤 Rendimiento Individual")
#     query_ind = f'''
#         SELECT s.id, s.name as Vendedor, 
#                COALESCE(SUM(v.total_points), 0) as Puntos,
#                COALESCE(SUM(v.total_commission), 0) as Comision,
#                COALESCE(t.target_points, 0) as Meta
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         GROUP BY s.id
#     '''
#     df_ind = pd.read_sql_query(query_ind, conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             c1, c2 = st.columns([1, 4])
#             meta = row['Meta']
#             puntos = row['Puntos']
#             cumplimiento = (puntos / meta) if meta > 0 else 0
            
#             with c1:
#                 st.write(f"**{row['Vendedor']}**")
#                 st.write(f"Pts: {int(puntos)}")
#                 # Regla del 80% para comisionar
#                 if cumplimiento >= 0.8:
#                     st.success(f"Comisiona: ${row['Comision']:,.0f}")
#                 else:
#                     st.error(f"No comisiona ({(cumplimiento*100):.1f}%)")
            
#             with c2:
#                 st.write(f"Meta Individual: {int(meta)} pts")
#                 st.progress(min(cumplimiento, 1.0))
#                 if cumplimiento >= 1.0: st.caption("🎯 Meta 100% completada")
#                 elif cumplimiento >= 0.8: st.caption("✔️ Sobre el umbral del 80%")
    
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial de Ventas")
#     conn = get_connection()
#     df = pd.read_sql_query('''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, v.customer_rut as RUT,
#                v.doc_type as Tipo, v.doc_number as [N° Doc], v.payment_method as Pago,
#                v.total_amount as [Monto $], v.total_points as Pts, v.category_summary as Resumen
#         FROM sales v JOIN sellers s ON v.seller_id = s.id ORDER BY v.id DESC
#     ''', conn)
#     conn.close()
    
#     if not df.empty:
#         st.dataframe(df, use_container_width=True)
#         csv = df.to_csv(index=False).encode('utf-8')
#         st.download_button("📥 Descargar Excel (CSV)", csv, "ventas.csv", "text/csv")
#     else:
#         st.info("No hay registros.")

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2, t3 = st.tabs(["Vendedores", "Metas Mensuales (Individual/Grupal)", "Reglas de Puntos"])
    
#     with t1:
#         st.subheader("Gestión de Personal")
#         with st.form("new_seller"):
#             name = st.text_input("Nombre completo")
#             if st.form_submit_button("Añadir") and name:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (name,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         st.subheader("Configuración de Objetivos")
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="mt")
#         y_t = st.number_input("Año", value=2025, key="yt")
        
#         # Añadir opción de Meta Grupal (ID 0) a la lista de vendedores para configurar
#         sellers = get_sellers()
#         options = [(0, "🏬 META GRUPAL (TIENDA)")] + list(zip(sellers['id'], sellers['name']))
        
#         target_to_edit = st.selectbox("Seleccionar para editar meta:", options, format_func=lambda x: x[1])
        
#         with st.form("form_metas"):
#             st.write(f"Editando metas para: {target_to_edit[1]}")
#             conn = get_connection(); cur = conn.cursor()
#             cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (target_to_edit[0], m_t, y_t))
#             res = cur.fetchone()
            
#             # Valores actuales o 0
#             v0 = res[4] if res else 0 # pts
#             v1 = res[5] if res else 0 # post
#             v2 = res[6] if res else 0 # porta
#             v3 = res[7] if res else 0 # fibra
#             v4 = res[8] if res else 0 # seguro
#             v5 = res[9] if res else 0 # renov
#             v6 = res[10] if res else 0 # womgo
            
#             c1, c2, c3 = st.columns(3)
#             mt_pts = c1.number_input("Meta Puntos", value=v0)
#             mt_post = c2.number_input("Meta Postpago (Q)", value=v1)
#             mt_porta = c3.number_input("Meta Portabilidad (Q)", value=v2)
            
#             c4, c5, c6, c7 = st.columns(4)
#             mt_fibra = c4.number_input("Meta Fibra (Q)", value=v3)
#             mt_seguro = c5.number_input("Meta Seguro (Q)", value=v4)
#             mt_renov = c6.number_input("Meta Renovación (Q)", value=v5)
#             mt_womgo = c7.number_input("Meta Wom Go (Q)", value=v6)
            
#             if st.form_submit_button("Guardar todas las metas"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_portabilidad, 
#                                        target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (?,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points,
#                         target_postpago=excluded.target_postpago,
#                         target_portabilidad=excluded.target_portabilidad,
#                         target_fibra=excluded.target_fibra,
#                         target_seguro=excluded.target_seguro,
#                         target_renovacion=excluded.target_renovacion,
#                         target_womgo=excluded.target_womgo
#                 ''', (target_to_edit[0], m_t, y_t, mt_pts, mt_post, mt_porta, mt_fibra, mt_seguro, mt_renov, mt_womgo))
#                 conn.commit(); conn.close(); st.success("Metas actualizadas correctamente")

#     with t3:
#         st.subheader("Valores de ítems")
#         conn = get_connection()
#         rules_df = pd.read_sql_query("SELECT * FROM point_rules", conn)
#         for i, r in rules_df.iterrows():
#             c1, c2, c3 = st.columns([3, 2, 1])
#             c1.write(r['item_name'])
#             new_v = c2.number_input("Valor", value=float(r['value']), key=f"r{i}", label_visibility="collapsed")
#             if c3.button("💾", key=f"b{i}"):
#                 cur = conn.cursor()
#                 cur.execute("UPDATE point_rules SET value=? WHERE id=?", (new_v, r['id']))
#                 conn.commit(); conn.close(); st.rerun()







# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             active INTEGER DEFAULT 1,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER, -- 0 para meta GLOBAL de la tienda
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             target_postpago INTEGER DEFAULT 0,
#             target_porta_pct REAL DEFAULT 0.0, -- Ahora es porcentaje
#             target_fibra INTEGER DEFAULT 0,
#             target_seguro INTEGER DEFAULT 0,
#             target_renovacion INTEGER DEFAULT 0,
#             target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             customer_rut TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category_summary TEXT, 
#             phone_number TEXT,
#             iccid TEXT,
#             device_name TEXT,
#             imei TEXT,
#             has_insurance INTEGER DEFAULT 0,
#             accessory_name TEXT,
#             accessory_code TEXT,
#             fiber_plan TEXT,
#             fiber_address TEXT,
#             doc_type TEXT,
#             doc_number TEXT,
#             payment_method TEXT,
#             status TEXT DEFAULT 'approved',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Vendedor de Prueba', 1)")
        
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE APOYO ---
# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- INTERFAZ ---
# st.sidebar.title("🛠️ Sales Manager")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu)

# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.error("Debe configurar vendedores primero.")
#     else:
#         with st.form("main_form", clear_on_submit=True):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()
#             st.subheader("📱 Telefonía / Líneas")
#             col_a1, col_a2, col_a3 = st.columns(3)
#             with col_a1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_a2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_a3:
#                 tipo_extra = st.selectbox("Otros Planes", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             phone_val = st.text_input("Número de Teléfono (Si aplica)")
#             iccid_val = st.text_input("ICCID de la SIM (Si aplica)")

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2 = st.columns(2)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Venta de Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 ins_check = st.checkbox("¿Incluye Seguro?")

#             device_name = st.text_input("Modelo del Equipo (Si aplica)")
#             imei_val = st.text_input("IMEI (Si aplica)")

#             st.divider()
#             st.subheader("🔌 Accesorios")
#             acc_check = st.checkbox("¿Venta de Accesorio?")
#             col_acc1, col_acc2 = st.columns(2)
#             with col_acc1:
#                 acc_name = st.text_input("Nombre del Accesorio")
#             with col_acc2:
#                 acc_code = st.text_input("Código del Accesorio")

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             fibra_check = st.selectbox("Venta de Fibra", ["No aplica", "Fibra"])
#             col_fib1, col_fib2 = st.columns(2)
#             with col_fib1:
#                 fib_plan = st.text_input("Plan de Fibra")
#             with col_fib2:
#                 fib_addr = st.text_input("Dirección de Instalación")

#             st.divider()
#             st.subheader("💳 Información de Pago y Documento")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_type = st.selectbox("Tipo de Documento", ["Boleta", "Guía", "Factura"])
#             with col_p2:
#                 doc_number = st.text_input("Número de Documento")
#             with col_p3:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             items_seleccionados = []
#             if tipo_porta != "No aplica": items_seleccionados.append(tipo_porta)
#             if tipo_post != "No aplica": items_seleccionados.append(tipo_post)
#             if tipo_extra != "No aplica": items_seleccionados.append(tipo_extra)
#             if tipo_equipo != "No aplica": items_seleccionados.append(tipo_equipo)
#             if fibra_check != "No aplica": items_seleccionados.append(fibra_check)
            
#             puntos_totales = sum(rules.get(item, 0) for item in items_seleccionados)
#             comision_total = 0
#             if ins_check: comision_total += rules.get("Seguro", 1500)
#             if acc_check: comision_total += rules.get("Accesorio", 1000)
            
#             st.markdown(f"### Estimación: **{int(puntos_totales)} Puntos** | **${comision_total:,.0f} Comisión**")
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
#             if submit:
#                 if not customer or not customer_rut or not doc_number:
#                     st.error("Por favor rellene los campos obligatorios (Nombre, RUT, N° Documento)")
#                 else:
#                     summary = ", ".join(items_seleccionados)
#                     conn = get_connection(); cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (
#                             date, seller_id, customer_name, customer_rut, total_amount, total_points, total_commission, 
#                             category_summary, phone_number, iccid, device_name, imei, has_insurance,
#                             accessory_name, accessory_code, fiber_plan, fiber_address,
#                             doc_type, doc_number, payment_method
#                         ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                     ''', (
#                         sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, amount, puntos_totales, comision_total,
#                         summary, phone_val, iccid_val, device_name, imei_val, (1 if ins_check else 0),
#                         acc_name, acc_code, fib_plan, fib_addr,
#                         doc_type, doc_number, payment_method
#                     ))
#                     conn.commit(); conn.close()
#                     st.success(f"Venta registrada con éxito")
#                     st.balloons()

# elif choice == "Dashboard":
#     st.header("📊 Dashboard de Metas y Cumplimiento")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     st.subheader("🏢 Resumen Global de la Tienda")
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as total_pts,
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as v_post,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as v_porta,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as v_fibra,
#             SUM(has_insurance) as v_seguros,
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as v_renov,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as v_womgo
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}'
#     '''
#     res_actual = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_grupal = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_grupal.empty:
#         m = meta_grupal.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos Tienda", f"{int(res_actual['total_pts'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpagos", f"{int(res_actual['v_post'] or 0)}", f"Meta: {m['target_postpago']}")
        
#         # Lógica de porcentaje para Portabilidad
#         porta_real_pct = (res_actual['v_porta'] / res_actual['v_post'] * 100) if res_actual['v_post'] and res_actual['v_post'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res_actual['v_fibra'] or 0)}", f"Meta: {m['target_fibra']}")
#     else:
#         st.warning("No hay metas globales configuradas.")

#     st.divider()
#     st.subheader("👤 Rendimiento Individual")
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.id, s.name as Vendedor, 
#                COALESCE(SUM(v.total_points), 0) as Puntos,
#                COALESCE(SUM(v.total_commission), 0) as Comision,
#                COALESCE(t.target_points, 0) as Meta
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1
#         GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             c1, c2 = st.columns([1, 4])
#             meta = row['Meta']
#             puntos = row['Puntos']
#             cumplimiento = (puntos / meta) if meta > 0 else 0
#             with c1:
#                 st.write(f"**{row['Vendedor']}**")
#                 st.write(f"Pts: {int(puntos)}")
#                 if cumplimiento >= 0.8:
#                     st.success(f"Comisiona: ${row['Comision']:,.0f}")
#                 else:
#                     st.error(f"No comisiona ({(cumplimiento*100):.1f}%)")
#             with c2:
#                 st.write(f"Progreso Meta ({int(meta)} pts)")
#                 st.progress(min(cumplimiento, 1.0))
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial de Ventas")
#     conn = get_connection()
#     df = pd.read_sql_query('''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, v.customer_rut as RUT,
#                v.doc_type as Tipo, v.doc_number as [N° Doc], v.payment_method as Pago,
#                v.total_amount as [Monto $], v.total_points as Pts, v.category_summary as Resumen
#         FROM sales v JOIN sellers s ON v.seller_id = s.id ORDER BY v.id DESC
#     ''', conn)
#     conn.close()
#     st.dataframe(df, use_container_width=True)

# elif choice == "Configuración":
#     st.header("⚙️ Configuración del Sistema")
#     t1, t2, t3 = st.tabs(["👥 Gestión de Vendedores", "🎯 Configuración de Metas", "💎 Reglas de Puntos"])
    
#     with t1:
#         st.subheader("Vendedores")
#         # Listar y Acciones
#         sellers_all = get_sellers(only_active=False)
#         for i, s in sellers_all.iterrows():
#             col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
#             col_s1.write(f"**{s['name']}** ({'Activo' if s['active'] else 'Inactivo'})")
#             if col_s2.button("Inactivar/Activar", key=f"status_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("UPDATE sellers SET active = ? WHERE id = ?", (0 if s['active'] else 1, s['id']))
#                 conn.commit(); conn.close(); st.rerun()
#             if col_s3.button("Eliminar", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         st.divider()
#         st.subheader("Nuevo Vendedor")
#         with st.form("new_seller"):
#             new_name = st.text_input("Nombre completo")
#             if st.form_submit_button("Registrar Vendedor") and new_name:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_name,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         st.subheader("Definición de Objetivos")
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="meta_m")
#         y_t = st.number_input("Año", value=2025, key="meta_y")
        
#         # --- META GLOBAL ---
#         st.markdown("### 🏬 Meta Global de la Tienda")
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         with st.form("meta_global"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3 = st.columns(3)
#             g_pts = c1.number_input("Puntos Globales", value=v[4])
#             g_post = c2.number_input("Cantidad Postpagos", value=v[5])
#             g_porta_pct = c3.number_input("% Portabilidades sobre Postpago", value=float(v[6]), format="%.1f")
            
#             c4, c5, c6, c7 = st.columns(4)
#             g_fibra = c4.number_input("Fibra Global", value=v[7])
#             g_seguro = c5.number_input("Seguros Global", value=v[8])
#             g_reno = c6.number_input("Renovación Global", value=v[9])
#             g_womgo = c7.number_input("Wom Go Global", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, 
#                                        target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                         target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                         target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion,
#                         target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_porta_pct, g_fibra, g_seguro, g_reno, g_womgo))
#                 conn.commit(); st.success("Meta Global Guardada")
        
#         # --- METAS INDIVIDUALES ---
#         st.markdown("### 👤 Metas Individuales")
#         active_sellers = get_sellers()
#         num_v = len(active_sellers)
        
#         if num_v > 0 and g_meta:
#             if st.button(f"🪄 Sugerir Metas (Dividir Global entre {num_v} vendedores)"):
#                 for _, s in active_sellers.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, 
#                                            target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                             target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                             target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                             target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion,
#                             target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//num_v, g_post//num_v, g_porta_pct, g_fibra//num_v, g_seguro//num_v, g_reno//num_v, g_womgo//num_v))
#                 conn.commit(); st.success("Metas individuales sugeridas y guardadas."); st.rerun()

#         selected_s = st.selectbox("Editar meta específica de:", active_sellers['name'].tolist())
#         s_id = active_sellers[active_sellers['name'] == selected_s]['id'].values[0]
        
#         cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#         s_meta = cur.fetchone()
#         with st.form("meta_individual"):
#             sv = s_meta if s_meta else [0]*11
#             sc1, sc2, sc3 = st.columns(3)
#             si_pts = sc1.number_input("Puntos", value=sv[4])
#             si_post = sc2.number_input("Postpago", value=sv[5])
#             si_porta = sc3.number_input("% Porta", value=float(sv[6]))
            
#             if st.form_submit_button("Guardar Meta Individual"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, 
#                                        target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (?,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET target_points=excluded.target_points, target_postpago=excluded.target_postpago, target_porta_pct=excluded.target_porta_pct
#                 ''', (s_id, m_t, y_t, si_pts, si_post, si_porta, 0, 0, 0, 0))
#                 conn.commit(); st.success("Meta Individual Actualizada")
#         conn.close()

#     with t3:
#         st.subheader("Configuración de Puntaje")
#         conn = get_connection(); rules_df = pd.read_sql_query("SELECT * FROM point_rules", conn)
#         for i, r in rules_df.iterrows():
#             c1, c2, c3 = st.columns([3, 2, 1])
#             c1.write(r['item_name'])
#             new_v = c2.number_input("Valor", value=float(r['value']), key=f"rule_{i}", label_visibility="collapsed")
#             if c3.button("💾", key=f"save_rule_{i}"):
#                 cur = conn.cursor()
#                 cur.execute("UPDATE point_rules SET value=? WHERE id=?", (new_v, r['id']))
#                 conn.commit(); conn.close(); st.rerun()




# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             active INTEGER DEFAULT 1,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER, -- 0 para meta GLOBAL de la tienda
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             target_postpago INTEGER DEFAULT 0,
#             target_porta_pct REAL DEFAULT 0.0, -- Ahora es porcentaje
#             target_fibra INTEGER DEFAULT 0,
#             target_seguro INTEGER DEFAULT 0,
#             target_renovacion INTEGER DEFAULT 0,
#             target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             customer_rut TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category_summary TEXT, 
#             phone_number TEXT,
#             iccid TEXT,
#             device_name TEXT,
#             imei TEXT,
#             has_insurance INTEGER DEFAULT 0,
#             accessory_name TEXT,
#             accessory_code TEXT,
#             fiber_plan TEXT,
#             fiber_address TEXT,
#             doc_type TEXT,
#             doc_number TEXT,
#             payment_method TEXT,
#             status TEXT DEFAULT 'approved',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Vendedor de Prueba', 1)")
        
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE APOYO ---
# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- INTERFAZ ---
# st.sidebar.title("🛠️ Sales Manager")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu)

# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.error("Debe configurar vendedores primero.")
#     else:
#         with st.form("main_form", clear_on_submit=True):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()
#             st.subheader("📱 Telefonía / Líneas")
#             col_a1, col_a2, col_a3 = st.columns(3)
#             with col_a1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_a2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_a3:
#                 tipo_extra = st.selectbox("Otros Planes", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             phone_val = st.text_input("Número de Teléfono (Si aplica)")
#             iccid_val = st.text_input("ICCID de la SIM (Si aplica)")

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2 = st.columns(2)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Venta de Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 ins_check = st.checkbox("¿Incluye Seguro?")

#             device_name = st.text_input("Modelo del Equipo (Si aplica)")
#             imei_val = st.text_input("IMEI (Si aplica)")

#             st.divider()
#             st.subheader("🔌 Accesorios")
#             acc_check = st.checkbox("¿Venta de Accesorio?")
#             col_acc1, col_acc2 = st.columns(2)
#             with col_acc1:
#                 acc_name = st.text_input("Nombre del Accesorio")
#             with col_acc2:
#                 acc_code = st.text_input("Código del Accesorio")

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             fibra_check = st.selectbox("Venta de Fibra", ["No aplica", "Fibra"])
#             col_fib1, col_fib2 = st.columns(2)
#             with col_fib1:
#                 fib_plan = st.text_input("Plan de Fibra")
#             with col_fib2:
#                 fib_addr = st.text_input("Dirección de Instalación")

#             st.divider()
#             st.subheader("💳 Información de Pago y Documento")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_type = st.selectbox("Tipo de Documento", ["Boleta", "Guía", "Factura"])
#             with col_p2:
#                 doc_number = st.text_input("Número de Documento")
#             with col_p3:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             items_seleccionados = []
#             if tipo_porta != "No aplica": items_seleccionados.append(tipo_porta)
#             if tipo_post != "No aplica": items_seleccionados.append(tipo_post)
#             if tipo_extra != "No aplica": items_seleccionados.append(tipo_extra)
#             if tipo_equipo != "No aplica": items_seleccionados.append(tipo_equipo)
#             if fibra_check != "No aplica": items_seleccionados.append(fibra_check)
            
#             puntos_totales = sum(rules.get(item, 0) for item in items_seleccionados)
#             comision_total = 0
#             if ins_check: comision_total += rules.get("Seguro", 1500)
#             if acc_check: comision_total += rules.get("Accesorio", 1000)
            
#             st.markdown(f"### Estimación: **{int(puntos_totales)} Puntos** | **${comision_total:,.0f} Comisión**")
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
#             if submit:
#                 if not customer or not customer_rut or not doc_number:
#                     st.error("Por favor rellene los campos obligatorios (Nombre, RUT, N° Documento)")
#                 else:
#                     summary = ", ".join(items_seleccionados)
#                     conn = get_connection(); cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (
#                             date, seller_id, customer_name, customer_rut, total_amount, total_points, total_commission, 
#                             category_summary, phone_number, iccid, device_name, imei, has_insurance,
#                             accessory_name, accessory_code, fiber_plan, fiber_address,
#                             doc_type, doc_number, payment_method
#                         ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                     ''', (
#                         sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, amount, puntos_totales, comision_total,
#                         summary, phone_val, iccid_val, device_name, imei_val, (1 if ins_check else 0),
#                         acc_name, acc_code, fib_plan, fib_addr,
#                         doc_type, doc_number, payment_method
#                     ))
#                     conn.commit(); conn.close()
#                     st.success(f"Venta registrada con éxito")
#                     st.balloons()

# elif choice == "Dashboard":
#     st.header("📊 Dashboard de Metas y Cumplimiento")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     st.subheader("🏢 Resumen Global de la Tienda")
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as total_pts,
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as v_post,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as v_porta,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as v_fibra,
#             SUM(has_insurance) as v_seguros,
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as v_renov,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as v_womgo
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}'
#     '''
#     res_actual = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_grupal = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_grupal.empty:
#         m = meta_grupal.iloc[0]
#         # Primera fila de métricas
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos Tienda", f"{int(res_actual['total_pts'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpagos", f"{int(res_actual['v_post'] or 0)}", f"Meta: {m['target_postpago']}")
        
#         porta_real_pct = (res_actual['v_porta'] / res_actual['v_post'] * 100) if res_actual['v_post'] and res_actual['v_post'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res_actual['v_fibra'] or 0)}", f"Meta: {m['target_fibra']}")

#         # Segunda fila de métricas (Seguros, Renovación, Wom Go)
#         c5, c6, c7, c8 = st.columns(4)
#         c5.metric("Seguros", f"{int(res_actual['v_seguros'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res_actual['v_renov'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res_actual['v_womgo'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.warning("No hay metas globales configuradas.")

#     st.divider()
#     st.subheader("👤 Rendimiento Individual")
    
#     # Query expandida para traer cantidades individuales
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.id, s.name as Vendedor, 
#                COALESCE(SUM(v.total_points), 0) as Puntos,
#                COALESCE(SUM(v.total_commission), 0) as Comision,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END), 0) as v_porta,
#                COALESCE(SUM(v.has_insurance), 0) as v_seguros,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_renov,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_womgo,
#                COALESCE(t.target_points, 0) as m_points,
#                COALESCE(t.target_postpago, 0) as m_post,
#                COALESCE(t.target_porta_pct, 0) as m_porta_pct,
#                COALESCE(t.target_seguro, 0) as m_seguro,
#                COALESCE(t.target_renovacion, 0) as m_renov,
#                COALESCE(t.target_womgo, 0) as m_womgo
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1
#         GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             # Layout de fila por vendedor
#             col_info, col_prog = st.columns([1, 4])
            
#             puntos = row['Puntos']
#             meta_pts = row['m_points']
#             cumplimiento = (puntos / meta_pts) if meta_pts > 0 else 0
            
#             with col_info:
#                 st.markdown(f"#### {row['Vendedor']}")
#                 if cumplimiento >= 0.8:
#                     st.success(f"Comisiona: ${row['Comision']:,.0f}")
#                 else:
#                     st.error(f"No comisiona ({(cumplimiento*100):.1f}%)")
            
#             with col_prog:
#                 # Barra de progreso de puntos
#                 st.write(f"**Puntos:** {int(puntos)} / {int(meta_pts)} ({cumplimiento:.1%})")
#                 st.progress(min(cumplimiento, 1.0))
                
#                 # Desglose de cantidades en columnas pequeñas
#                 d1, d2, d3, d4, d5, d6 = st.columns(6)
                
#                 # Postpagos
#                 d1.caption("Postpago")
#                 d1.write(f"{int(row['v_post'])}/{int(row['m_post'])}")
                
#                 # Portas (Cálculo de porcentaje real vs meta)
#                 porta_pct_real = (row['v_porta'] / row['v_post'] * 100) if row['v_post'] > 0 else 0
#                 d2.caption("Porta %")
#                 d2.write(f"{porta_pct_real:.0f}/{int(row['m_porta_pct'])}%")
                
#                 # Seguros
#                 d3.caption("Seguros")
#                 d3.write(f"{int(row['v_seguros'])}/{int(row['m_seguro'])}")
                
#                 # Renovaciones
#                 d4.caption("Renov.")
#                 d4.write(f"{int(row['v_renov'])}/{int(row['m_renov'])}")
                
#                 # Wom Go
#                 d5.caption("Wom Go")
#                 d5.write(f"{int(row['v_womgo'])}/{int(row['m_womgo'])}")
                
#                 # Comision actual (referencia rápida)
#                 d6.caption("Comisión")
#                 d6.write(f"${row['Comision']:,.0f}")

#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial de Ventas")
#     conn = get_connection()
#     df = pd.read_sql_query('''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, v.customer_rut as RUT,
#                v.doc_type as Tipo, v.doc_number as [N° Doc], v.payment_method as Pago,
#                v.total_amount as [Monto $], v.total_points as Pts, v.category_summary as Resumen
#         FROM sales v JOIN sellers s ON v.seller_id = s.id ORDER BY v.id DESC
#     ''', conn)
#     conn.close()
#     st.dataframe(df, use_container_width=True)

# elif choice == "Configuración":
#     st.header("⚙️ Configuración del Sistema")
#     t1, t2, t3 = st.tabs(["👥 Gestión de Vendedores", "🎯 Configuración de Metas", "💎 Reglas de Puntos"])
    
#     with t1:
#         st.subheader("Vendedores")
#         sellers_all = get_sellers(only_active=False)
#         for i, s in sellers_all.iterrows():
#             col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
#             col_s1.write(f"**{s['name']}** ({'Activo' if s['active'] else 'Inactivo'})")
#             if col_s2.button("Inactivar/Activar", key=f"status_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("UPDATE sellers SET active = ? WHERE id = ?", (0 if s['active'] else 1, s['id']))
#                 conn.commit(); conn.close(); st.rerun()
#             if col_s3.button("Eliminar", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         st.divider()
#         st.subheader("Nuevo Vendedor")
#         with st.form("new_seller"):
#             new_name = st.text_input("Nombre completo")
#             if st.form_submit_button("Registrar Vendedor") and new_name:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_name,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         st.subheader("Definición de Objetivos")
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="meta_m")
#         y_t = st.number_input("Año", value=2025, key="meta_y")
        
#         # --- META GLOBAL ---
#         st.markdown("### 🏬 Meta Global de la Tienda")
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         with st.form("meta_global"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3 = st.columns(3)
#             g_pts = c1.number_input("Puntos Globales", value=v[4])
#             g_post = c2.number_input("Cantidad Postpagos", value=v[5])
#             g_porta_pct = c3.number_input("% Portabilidades sobre Postpago", value=float(v[6]), format="%.1f")
            
#             c4, c5, c6, c7 = st.columns(4)
#             g_fibra = c4.number_input("Fibra Global", value=v[7])
#             g_seguro = c5.number_input("Seguros Global", value=v[8])
#             g_reno = c6.number_input("Renovación Global", value=v[9])
#             g_womgo = c7.number_input("Wom Go Global", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, 
#                                        target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                         target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                         target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion,
#                         target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_porta_pct, g_fibra, g_seguro, g_reno, g_womgo))
#                 conn.commit(); st.success("Meta Global Guardada")
        
#         # --- METAS INDIVIDUALES ---
#         st.markdown("### 👤 Metas Individuales")
#         active_sellers = get_sellers()
#         num_v = len(active_sellers)
        
#         if num_v > 0 and g_meta:
#             if st.button(f"🪄 Sugerir Metas (Dividir Global entre {num_v} vendedores)"):
#                 for _, s in active_sellers.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, 
#                                            target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                             target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                             target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                             target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion,
#                             target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//num_v, g_post//num_v, g_porta_pct, g_fibra//num_v, g_seguro//num_v, g_reno//num_v, g_womgo//num_v))
#                 conn.commit(); st.success("Metas individuales sugeridas y guardadas."); st.rerun()

#         selected_s = st.selectbox("Editar meta específica de:", active_sellers['name'].tolist())
#         s_id = active_sellers[active_sellers['name'] == selected_s]['id'].values[0]
        
#         cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#         s_meta = cur.fetchone()
#         with st.form("meta_individual"):
#             sv = s_meta if s_meta else [0]*11
#             sc1, sc2, sc3 = st.columns(3)
#             si_pts = sc1.number_input("Puntos", value=sv[4])
#             si_post = sc2.number_input("Postpago", value=sv[5])
#             si_porta = sc3.number_input("% Porta", value=float(sv[6]))
            
#             sc4, sc5, sc6 = st.columns(3)
#             si_seg = sc4.number_input("Seguro", value=sv[8])
#             si_ren = sc5.number_input("Renovación", value=sv[9])
#             si_wom = sc6.number_input("Wom Go", value=sv[10])
            
#             if st.form_submit_button("Guardar Meta Individual"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, 
#                                        target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (?,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET 
#                         target_points=excluded.target_points, 
#                         target_postpago=excluded.target_postpago, 
#                         target_porta_pct=excluded.target_porta_pct,
#                         target_seguro=excluded.target_seguro,
#                         target_renovacion=excluded.target_renovacion,
#                         target_womgo=excluded.target_womgo
#                 ''', (s_id, m_t, y_t, si_pts, si_post, si_porta, 0, si_seg, si_ren, si_wom))
#                 conn.commit(); st.success("Meta Individual Actualizada")
#         conn.close()

#     with t3:
#         st.subheader("Configuración de Puntaje")
#         conn = get_connection(); rules_df = pd.read_sql_query("SELECT * FROM point_rules", conn)
#         for i, r in rules_df.iterrows():
#             c1, c2, c3 = st.columns([3, 2, 1])
#             c1.write(r['item_name'])
#             new_v = c2.number_input("Valor", value=float(r['value']), key=f"rule_{i}", label_visibility="collapsed")
#             if c3.button("💾", key=f"save_rule_{i}"):
#                 cur = conn.cursor()
#                 cur.execute("UPDATE point_rules SET value=? WHERE id=?", (new_v, r['id']))
#                 conn.commit(); conn.close(); st.rerun()




# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- INICIALIZACIÓN DE ESTADO DE NAVEGACIÓN ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             active INTEGER DEFAULT 1,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER,
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             target_postpago INTEGER DEFAULT 0,
#             target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0,
#             target_seguro INTEGER DEFAULT 0,
#             target_renovacion INTEGER DEFAULT 0,
#             target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             customer_rut TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category_summary TEXT, 
#             phone_number TEXT,
#             iccid TEXT,
#             device_name TEXT,
#             imei TEXT,
#             has_insurance INTEGER DEFAULT 0,
#             accessory_name TEXT,
#             accessory_code TEXT,
#             fiber_plan TEXT,
#             fiber_address TEXT,
#             doc_type TEXT,
#             doc_number TEXT,
#             payment_method TEXT,
#             status TEXT DEFAULT 'Aprobada',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     cursor.execute("SELECT COUNT(*) FROM stores")
#     if cursor.fetchone()[0] == 0:
#         cursor.execute("INSERT INTO stores (name) VALUES ('Tienda Central')")
#         cursor.execute("INSERT INTO sellers (name, store_id) VALUES ('Vendedor de Prueba', 1)")
        
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE APOYO ---
# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- INTERFAZ ---
# st.sidebar.title("🛠️ Sales Manager")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu, index=menu.index(st.session_state.menu_option))

# # Actualizar el estado si el usuario cambia el selectbox manualmente
# st.session_state.menu_option = choice

# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.error("Debe configurar vendedores primero.")
#     else:
#         with st.form("main_form", clear_on_submit=True):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()
#             st.subheader("📱 Telefonía / Líneas")
#             col_a1, col_a2, col_a3 = st.columns(3)
#             with col_a1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_a2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_a3:
#                 tipo_extra = st.selectbox("Otros Planes", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2 = st.columns(2)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Venta de Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 ins_check = st.checkbox("¿Incluye Seguro?")

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             fibra_check = st.selectbox("Venta de Fibra", ["No aplica", "Fibra"])
#             col_fib1, col_fib2 = st.columns(2)
#             with col_fib1:
#                 fib_plan = st.text_input("Plan de Fibra")
#             with col_fib2:
#                 fib_addr = st.text_input("Dirección de Instalación")

#             st.divider()
#             st.subheader("💳 Pago")
#             col_p1, col_p2, col_p3 = st.columns(3)
#             with col_p1:
#                 doc_number = st.text_input("Número de Documento")
#             with col_p2:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p3:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             items_seleccionados = []
#             if tipo_porta != "No aplica": items_seleccionados.append(tipo_porta)
#             if tipo_post != "No aplica": items_seleccionados.append(tipo_post)
#             if tipo_extra != "No aplica": items_seleccionados.append(tipo_extra)
#             if tipo_equipo != "No aplica": items_seleccionados.append(tipo_equipo)
#             if fibra_check != "No aplica": items_seleccionados.append(fibra_check)
            
#             puntos_totales = sum(rules.get(item, 0) for item in items_seleccionados)
#             comision_total = 0
#             if ins_check: comision_total += rules.get("Seguro", 1500)
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
#             if submit:
#                 if not customer or not customer_rut or not doc_number:
#                     st.error("Campos obligatorios faltantes.")
#                 else:
#                     summary = ", ".join(items_seleccionados)
#                     conn = get_connection(); cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (
#                             date, seller_id, customer_name, customer_rut, total_amount, total_points, total_commission, 
#                             category_summary, has_insurance, fiber_plan, fiber_address, doc_number, payment_method, status
#                         ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                     ''', (
#                         sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, amount, puntos_totales, comision_total,
#                         summary, (1 if ins_check else 0), fib_plan, fib_addr, doc_number, payment_method, 'Aprobada'
#                     ))
#                     conn.commit(); conn.close()
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Dashboard de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     # Solo sumar ventas en estado 'Aprobada'
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as total_pts,
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as v_post,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as v_porta,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as v_fibra,
#             SUM(has_insurance) as v_seguros,
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as v_renov,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as v_womgo
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' 
#         AND status = 'Aprobada'
#     '''
#     res_actual = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_grupal = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_grupal.empty:
#         m = meta_grupal.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos Tienda", f"{int(res_actual['total_pts'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpagos", f"{int(res_actual['v_post'] or 0)}", f"Meta: {m['target_postpago']}")
        
#         porta_real_pct = (res_actual['v_porta'] / res_actual['v_post'] * 100) if res_actual['v_post'] and res_actual['v_post'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res_actual['v_fibra'] or 0)}", f"Meta: {m['target_fibra']}")

#         c5, c6, c7 = st.columns(3)
#         c5.metric("Seguros", f"{int(res_actual['v_seguros'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res_actual['v_renov'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res_actual['v_womgo'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.warning("No hay metas globales configuradas.")

#     st.divider()
#     st.subheader("👤 Rendimiento Individual")
    
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.id, s.name as Vendedor, 
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.total_points ELSE 0 END), 0) as Puntos,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.total_commission ELSE 0 END), 0) as Comision,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as v_fibra,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.has_insurance ELSE 0 END), 0) as v_seguros,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_renov,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_womgo,
#                COALESCE(t.target_points, 0) as m_points,
#                COALESCE(t.target_postpago, 0) as m_post,
#                COALESCE(t.target_fibra, 0) as m_fibra,
#                COALESCE(t.target_seguro, 0) as m_seguro,
#                COALESCE(t.target_renovacion, 0) as m_renov,
#                COALESCE(t.target_womgo, 0) as m_womgo
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1
#         GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             col_info, col_prog = st.columns([1, 4])
#             puntos = row['Puntos']
#             meta_pts = row['m_points']
#             cumplimiento = (puntos / meta_pts) if meta_pts > 0 else 0
            
#             with col_info:
#                 st.markdown(f"#### {row['Vendedor']}")
#                 if cumplimiento >= 0.8:
#                     st.success(f"Cumple: {cumplimiento:.1%}")
#                     st.write(f"💰 ${row['Comision']:,.0f}")
#                 else:
#                     st.error(f"Piso: {cumplimiento:.1%}")
            
#             with col_prog:
#                 st.write(f"**Progreso Puntos:** {int(puntos)} / {int(meta_pts)}")
#                 st.progress(min(cumplimiento, 1.0))
                
#                 d1, d2, d3, d4, d5 = st.columns(5)
#                 d1.caption("Postpago"); d1.write(f"{int(row['v_post'])}/{int(row['m_post'])}")
#                 d2.caption("Fibra"); d2.write(f"{int(row['v_fibra'])}/{int(row['m_fibra'])}")
#                 d3.caption("Seguros"); d3.write(f"{int(row['v_seguros'])}/{int(row['m_seguro'])}")
#                 d4.caption("Renov."); d4.write(f"{int(row['v_renov'])}/{int(row['m_renov'])}")
#                 d5.caption("Wom Go"); d5.write(f"{int(row['v_womgo'])}/{int(row['m_womgo'])}")

#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial y Gestión de Ventas")
    
#     col_f1, col_f2 = st.columns([2, 5])
#     filter_date = col_f1.date_input("Filtrar por día", datetime.now())
    
#     conn = get_connection()
#     query = f'''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, 
#                v.doc_number as [N° Doc], v.total_points as Pts, v.status as Estado, v.category_summary
#         FROM sales v JOIN sellers s ON v.seller_id = s.id 
#         WHERE v.date = '{filter_date.strftime("%Y-%m-%d")}'
#         ORDER BY v.id DESC
#     '''
#     df_hist = pd.read_sql_query(query, conn)
    
#     if df_hist.empty:
#         st.info("No hay ventas registradas en esta fecha.")
#     else:
#         for _, row in df_hist.iterrows():
#             with st.expander(f"DOC: {row['N° Doc']} | {row['Vendedor']} | {row['Pts']} pts | [{row['Estado']}]"):
#                 st.write(f"**Cliente:** {row['Cliente']} | **Resumen:** {row['category_summary']}")
#                 c_edit1, c_edit2, c_edit3 = st.columns(3)
                
#                 new_status = c_edit1.selectbox("Cambiar Estado", ["Aprobada", "Rechazada"], index=0 if row['Estado']=='Aprobada' else 1, key=f"stat_{row['id']}")
                
#                 if c_edit2.button("Actualizar Estado", key=f"upd_{row['id']}"):
#                     cur = conn.cursor()
#                     cur.execute("UPDATE sales SET status = ? WHERE id = ?", (new_status, row['id']))
#                     conn.commit(); st.rerun()
                    
#                 if c_edit3.button("🗑️ Eliminar Venta", key=f"del_sale_{row['id']}"):
#                     cur = conn.cursor()
#                     cur.execute("DELETE FROM sales WHERE id = ?", (row['id'],))
#                     conn.commit(); st.rerun()
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2 = st.tabs(["👥 Vendedores", "🎯 Metas"])
    
#     with t1:
#         st.subheader("Gestión de Equipo")
#         sellers_all = get_sellers(only_active=False)
#         for i, s in sellers_all.iterrows():
#             col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
#             col_s1.write(f"**{s['name']}** ({'Activo' if s['active'] else 'Inactivo'})")
#             if col_s2.button("Toggle Activo", key=f"stat_sel_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("UPDATE sellers SET active = ? WHERE id = ?", (0 if s['active'] else 1, s['id']))
#                 conn.commit(); conn.close(); st.rerun()
#             if col_s3.button("Eliminar", key=f"del_sel_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller"):
#             n_sel = st.text_input("Nombre Nuevo Vendedor")
#             if st.form_submit_button("Añadir") and n_sel:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (n_sel,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         st.subheader("Metas Mensuales")
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="cfg_m")
#         y_t = st.number_input("Año", value=2025, key="cfg_y")
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         with st.form("global_targets"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3, c4 = st.columns(4)
#             g_pts = c1.number_input("Puntos", value=v[4])
#             g_post = c2.number_input("Postpago", value=v[5])
#             g_fib = c3.number_input("Fibra", value=v[7])
#             g_pct = c4.number_input("% Porta", value=float(v[6]))
            
#             if st.form_submit_button("Guardar Metas Tienda"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra)
#                     VALUES (0,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                     target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra
#                 ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib))
#                 conn.commit(); st.success("Guardado")
        
#         st.divider()
#         if st.button("🪄 Dividir Metas entre Vendedores Activos"):
#             act_s = get_sellers()
#             if not act_s.empty and g_meta:
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra)
#                         VALUES (?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago, target_fibra=excluded.target_fibra
#                     ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n))
#                 conn.commit(); st.success("Metas divididas"); st.rerun()
#         conn.close()




# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide")

# # --- INICIALIZACIÓN DE ESTADO DE NAVEGACIÓN ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             active INTEGER DEFAULT 1,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER,
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             target_postpago INTEGER DEFAULT 0,
#             target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0,
#             target_seguro INTEGER DEFAULT 0,
#             target_renovacion INTEGER DEFAULT 0,
#             target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             customer_rut TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category_summary TEXT, 
#             has_insurance INTEGER DEFAULT 0,
#             fiber_plan TEXT,
#             fiber_address TEXT,
#             doc_number TEXT,
#             payment_method TEXT,
#             status TEXT DEFAULT 'Aprobada',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     cursor.execute("SELECT COUNT(*) FROM point_rules")
#     if cursor.fetchone()[0] == 0:
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission'),
#             ('Accesorio', 1000, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# # --- FUNCIONES DE APOYO ---
# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- INTERFAZ ---
# st.sidebar.title("🛠️ Sales Manager")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu, index=menu.index(st.session_state.menu_option))
# st.session_state.menu_option = choice

# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.error("Debe configurar vendedores primero.")
#     else:
#         with st.form("main_form", clear_on_submit=True):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()
#             st.subheader("📱 Telefonía / Líneas")
#             col_a1, col_a2, col_a3 = st.columns(3)
#             with col_a1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_a2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_a3:
#                 tipo_extra = st.selectbox("Otros Planes", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2 = st.columns(2)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Venta de Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 ins_check = st.checkbox("¿Incluye Seguro?")

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             fibra_check = st.selectbox("Venta de Fibra", ["No aplica", "Fibra"])
#             col_fib1, col_fib2 = st.columns(2)
#             with col_fib1:
#                 fib_plan = st.text_input("Plan de Fibra")
#             with col_fib2:
#                 fib_addr = st.text_input("Dirección de Instalación")

#             st.divider()
#             st.subheader("💳 Pago")
#             col_p1, col_p2, col_p3 = st.columns(3)
#             with col_p1:
#                 doc_number = st.text_input("Número de Documento")
#             with col_p2:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p3:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             items_seleccionados = []
#             if tipo_porta != "No aplica": items_seleccionados.append(tipo_porta)
#             if tipo_post != "No aplica": items_seleccionados.append(tipo_post)
#             if tipo_extra != "No aplica": items_seleccionados.append(tipo_extra)
#             if tipo_equipo != "No aplica": items_seleccionados.append(tipo_equipo)
#             if fibra_check != "No aplica": items_seleccionados.append(fibra_check)
            
#             puntos_totales = sum(rules.get(item, 0) for item in items_seleccionados)
#             comision_total = 0
#             if ins_check: comision_total += rules.get("Seguro", 1500)
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
#             if submit:
#                 if not customer or not customer_rut or not doc_number:
#                     st.error("Campos obligatorios faltantes.")
#                 else:
#                     summary = ", ".join(items_seleccionados)
#                     conn = get_connection(); cur = conn.cursor()
#                     cur.execute('''
#                         INSERT INTO sales (
#                             date, seller_id, customer_name, customer_rut, total_amount, total_points, total_commission, 
#                             category_summary, has_insurance, fiber_plan, fiber_address, doc_number, payment_method, status
#                         ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                     ''', (
#                         sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, amount, puntos_totales, comision_total,
#                         summary, (1 if ins_check else 0), fib_plan, fib_addr, doc_number, payment_method, 'Aprobada'
#                     ))
#                     conn.commit(); conn.close()
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Dashboard de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as total_pts,
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as v_post,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as v_porta,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as v_fibra,
#             SUM(has_insurance) as v_seguros,
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as v_renov,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as v_womgo
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' 
#         AND status = 'Aprobada'
#     '''
#     res_actual = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_grupal = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_grupal.empty:
#         m = meta_grupal.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos Tienda", f"{int(res_actual['total_pts'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpagos", f"{int(res_actual['v_post'] or 0)}", f"Meta: {m['target_postpago']}")
#         porta_real_pct = (res_actual['v_porta'] / res_actual['v_post'] * 100) if res_actual['v_post'] and res_actual['v_post'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res_actual['v_fibra'] or 0)}", f"Meta: {m['target_fibra']}")

#         c5, c6, c7 = st.columns(3)
#         c5.metric("Seguros", f"{int(res_actual['v_seguros'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res_actual['v_renov'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res_actual['v_womgo'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.warning("No hay metas globales configuradas.")

#     st.divider()
#     st.subheader("👤 Rendimiento Individual")
    
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.id, s.name as Vendedor, 
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.total_points ELSE 0 END), 0) as Puntos,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.total_commission ELSE 0 END), 0) as Comision,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as v_fibra,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.has_insurance ELSE 0 END), 0) as v_seguros,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_renov,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_womgo,
#                COALESCE(t.target_points, 0) as m_points,
#                COALESCE(t.target_postpago, 0) as m_post,
#                COALESCE(t.target_fibra, 0) as m_fibra,
#                COALESCE(t.target_seguro, 0) as m_seguro,
#                COALESCE(t.target_renovacion, 0) as m_renov,
#                COALESCE(t.target_womgo, 0) as m_womgo
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1
#         GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             col_info, col_prog = st.columns([1, 4])
#             puntos = row['Puntos']
#             meta_pts = row['m_points']
#             cumplimiento = (puntos / meta_pts) if meta_pts > 0 else 0
            
#             with col_info:
#                 st.markdown(f"#### {row['Vendedor']}")
#                 if cumplimiento >= 0.8:
#                     st.success(f"Cumple: {cumplimiento:.1%}")
#                 else:
#                     st.error(f"Piso: {cumplimiento:.1%}")
#                 st.write(f"💰 Com: ${row['Comision']:,.0f}")
            
#             with col_prog:
#                 st.write(f"**Puntos:** {int(puntos)} / {int(meta_pts)}")
#                 st.progress(min(cumplimiento, 1.0))
                
#                 d1, d2, d3, d4, d5 = st.columns(5)
#                 d1.caption("Postpago"); d1.write(f"{int(row['v_post'])}/{int(row['m_post'])}")
#                 d2.caption("Fibra"); d2.write(f"{int(row['v_fibra'])}/{int(row['m_fibra'])}")
#                 d3.caption("Seguros"); d3.write(f"{int(row['v_seguros'])}/{int(row['m_seguro'])}")
#                 d4.caption("Renov."); d4.write(f"{int(row['v_renov'])}/{int(row['m_renov'])}")
#                 d5.caption("Wom Go"); d5.write(f"{int(row['v_womgo'])}/{int(row['m_womgo'])}")
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial por Día")
#     col_f1, _ = st.columns([2, 5])
#     filter_date = col_f1.date_input("Filtrar por día", datetime.now())
    
#     conn = get_connection()
#     query = f'''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, 
#                v.doc_number as [N° Doc], v.total_points as Pts, v.status as Estado, v.category_summary
#         FROM sales v JOIN sellers s ON v.seller_id = s.id 
#         WHERE v.date = '{filter_date.strftime("%Y-%m-%d")}'
#         ORDER BY v.id DESC
#     '''
#     df_hist = pd.read_sql_query(query, conn)
    
#     if df_hist.empty:
#         st.info("No hay ventas este día.")
#     else:
#         for _, row in df_hist.iterrows():
#             with st.expander(f"DOC: {row['N° Doc']} | {row['Vendedor']} | {row['Pts']} pts | [{row['Estado']}]"):
#                 st.write(f"**Cliente:** {row['Cliente']} | **Resumen:** {row['category_summary']}")
#                 c_edit1, c_edit2, c_edit3 = st.columns(3)
#                 new_status = c_edit1.selectbox("Cambiar Estado", ["Aprobada", "Rechazada"], index=0 if row['Estado']=='Aprobada' else 1, key=f"stat_{row['id']}")
#                 if c_edit2.button("Actualizar", key=f"upd_{row['id']}"):
#                     cur = conn.cursor(); cur.execute("UPDATE sales SET status = ? WHERE id = ?", (new_status, row['id']))
#                     conn.commit(); st.rerun()
#                 if c_edit3.button("Eliminar", key=f"del_sale_{row['id']}"):
#                     cur = conn.cursor(); cur.execute("DELETE FROM sales WHERE id = ?", (row['id'],))
#                     conn.commit(); st.rerun()
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales"])
    
#     with t1:
#         st.subheader("Gestión de Equipo")
#         sellers_all = get_sellers(only_active=False)
#         for i, s in sellers_all.iterrows():
#             col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
#             col_s1.write(f"**{s['name']}** ({'Activo' if s['active'] else 'Inactivo'})")
#             if col_s2.button("Invertir Estado", key=f"stat_sel_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("UPDATE sellers SET active = ? WHERE id = ?", (0 if s['active'] else 1, s['id']))
#                 conn.commit(); conn.close(); st.rerun()
#             if col_s3.button("Borrar", key=f"del_sel_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller"):
#             n_sel = st.text_input("Nombre Nuevo Vendedor")
#             if st.form_submit_button("Añadir") and n_sel:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (n_sel,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="cfg_m")
#         y_t = st.number_input("Año", value=2025, key="cfg_y")
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         st.subheader("🏬 Meta Global de Tienda")
#         with st.form("global_targets"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3, c4 = st.columns(4)
#             g_pts = c1.number_input("Puntos", value=v[4])
#             g_post = c2.number_input("Postpago", value=v[5])
#             g_fib = c3.number_input("Fibra", value=v[7])
#             g_pct = c4.number_input("% Porta", value=float(v[6]))
            
#             c5, c6, c7 = st.columns(3)
#             g_seg = c5.number_input("Seguros", value=v[8])
#             g_ren = c6.number_input("Renovaciones", value=v[9])
#             g_wom = c7.number_input("Wom Go", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                     target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                     target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
#                 conn.commit(); st.success("Meta Global guardada")

#         st.divider()
#         st.subheader("👤 Metas Individuales")
#         act_s = get_sellers()
#         if st.button("🪄 Dividir Global entre Vendedores"):
#             if not act_s.empty and g_meta:
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n, g_seg//n, g_ren//n, g_wom//n))
#                 conn.commit(); st.success("Metas distribuidas"); st.rerun()

#         selected_name = st.selectbox("Editar manual para:", act_s['name'].tolist())
#         s_id = act_s[act_s['name'] == selected_name]['id'].values[0]
#         cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#         s_meta = cur.fetchone()
        
#         with st.form("ind_target_form"):
#             sv = s_meta if s_meta else [0]*11
#             sc1, sc2, sc3, sc4 = st.columns(4)
#             si_pts = sc1.number_input("Puntos", value=sv[4])
#             si_post = sc2.number_input("Postpago", value=sv[5])
#             si_fib = sc3.number_input("Fibra", value=sv[7])
#             si_pct = sc4.number_input("% Porta", value=float(sv[6]))
            
#             sc5, sc6, sc7 = st.columns(3)
#             si_seg = sc5.number_input("Seguro", value=sv[8])
#             si_ren = sc6.number_input("Renovación", value=sv[9])
#             si_wom = sc7.number_input("Wom Go", value=sv[10])
            
#             if st.form_submit_button("Guardar Meta Individual"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (?,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET 
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                     target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
#                     target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (s_id, m_t, y_t, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
#                 conn.commit(); st.success("Meta Individual actualizada")
#         conn.close()






# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime
# import time

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# # --- INICIALIZACIÓN DE ESTADO DE NAVEGACIÓN ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         );
        
#         CREATE TABLE IF NOT EXISTS sellers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             store_id INTEGER,
#             active INTEGER DEFAULT 1,
#             FOREIGN KEY (store_id) REFERENCES stores(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             seller_id INTEGER,
#             month INTEGER,
#             year INTEGER,
#             target_points INTEGER DEFAULT 0,
#             target_postpago INTEGER DEFAULT 0,
#             target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0,
#             target_seguro INTEGER DEFAULT 0,
#             target_renovacion INTEGER DEFAULT 0,
#             target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year),
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );

#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             seller_id INTEGER,
#             customer_name TEXT,
#             customer_rut TEXT,
#             total_amount REAL,
#             total_points INTEGER,
#             total_commission REAL DEFAULT 0,
#             category_summary TEXT, 
#             device_name TEXT,
#             imei TEXT,
#             has_insurance INTEGER DEFAULT 0,
#             fiber_plan TEXT,
#             fiber_address TEXT,
#             doc_type TEXT,
#             doc_number TEXT,
#             payment_method TEXT,
#             status TEXT DEFAULT 'Aprobada',
#             FOREIGN KEY (seller_id) REFERENCES sellers(id)
#         );
        
#         CREATE TABLE IF NOT EXISTS point_rules (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT UNIQUE,
#             value REAL,
#             type TEXT 
#         );
#     ''')
    
#     cursor.execute("SELECT COUNT(*) FROM point_rules")
#     if cursor.fetchone()[0] == 0:
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'),
#             ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'),
#             ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'),
#             ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'),
#             ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'),
#             ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'),
#             ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'),
#             ('Fibra', 10, 'points'),
#             ('Seguro', 1500, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
        
#     conn.commit()
#     conn.close()

# init_db()

# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- LÓGICA DE NAVEGACIÓN ---
# st.sidebar.title("🛠️ Sales Manager")
# menu = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# choice = st.sidebar.selectbox("Navegación", menu, index=menu.index(st.session_state.menu_option))
# st.session_state.menu_option = choice

# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.error("Debe configurar vendedores primero.")
#     else:
#         with st.form("main_form", clear_on_submit=False):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()
#             st.subheader("📱 Telefonía / Líneas")
#             col_a1, col_a2, col_a3 = st.columns(3)
#             with col_a1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_a2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_a3:
#                 tipo_extra = st.selectbox("Otros Planes", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2, col_b3 = st.columns(3)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Tipo de Venta Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 device_name = st.text_input("Nombre del Equipo (Modelo)")
#             with col_b3:
#                 imei_val = st.text_input("IMEI")
            
#             ins_check = st.checkbox("¿Incluye Seguro?")

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             fibra_check = st.selectbox("Venta de Fibra", ["No aplica", "Fibra"])
#             col_fib1, col_fib2 = st.columns(2)
#             with col_fib1:
#                 fib_plan = st.text_input("Plan de Fibra")
#             with col_fib2:
#                 fib_addr = st.text_input("Dirección de Instalación")

#             st.divider()
#             st.subheader("💳 Pago")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_type = st.selectbox("Tipo Documento", ["Boleta", "Factura", "Guía"])
#             with col_p2:
#                 doc_number = st.text_input("Número de Documento")
#             with col_p3:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
            
#             if submit:
#                 if not customer or not customer_rut or not doc_number:
#                     st.error("Campos obligatorios faltantes (Nombre, RUT, N° Documento).")
#                 else:
#                     items_seleccionados = []
#                     if tipo_porta != "No aplica": items_seleccionados.append(tipo_porta)
#                     if tipo_post != "No aplica": items_seleccionados.append(tipo_post)
#                     if tipo_extra != "No aplica": items_seleccionados.append(tipo_extra)
#                     if tipo_equipo != "No aplica": items_seleccionados.append(tipo_equipo)
#                     if fibra_check != "No aplica": items_seleccionados.append(fibra_check)
                    
#                     puntos_totales = sum(rules.get(item, 0) for item in items_seleccionados)
#                     comision_total = rules.get("Seguro", 1500) if ins_check else 0
#                     summary = ", ".join(items_seleccionados)

#                     # Efecto visual de guardado
#                     with st.status("Procesando venta...", expanded=True) as status:
#                         st.write("Validando datos...")
#                         time.sleep(0.5)
#                         st.write("Registrando en base de datos...")
                        
#                         conn = get_connection(); cur = conn.cursor()
#                         cur.execute('''
#                             INSERT INTO sales (
#                                 date, seller_id, customer_name, customer_rut, total_amount, total_points, total_commission, 
#                                 category_summary, device_name, imei, has_insurance, fiber_plan, fiber_address, 
#                                 doc_type, doc_number, payment_method, status
#                             ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                         ''', (
#                             sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, amount, puntos_totales, comision_total,
#                             summary, device_name, imei_val, (1 if ins_check else 0), fib_plan, fib_addr, 
#                             doc_type, doc_number, payment_method, 'Aprobada'
#                         ))
#                         conn.commit(); conn.close()
                        
#                         time.sleep(0.5)
#                         status.update(label="¡Venta Guardada con éxito!", state="complete", expanded=False)
                    
#                     st.balloons()
#                     time.sleep(1)
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Dashboard de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     # Solo ventas Aprobadas
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as total_pts,
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as v_post,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as v_porta,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as v_fibra,
#             SUM(has_insurance) as v_seguros,
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as v_renov,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as v_womgo
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' 
#         AND status = 'Aprobada'
#     '''
#     res_actual = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_grupal = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_grupal.empty:
#         m = meta_grupal.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos Tienda", f"{int(res_actual['total_pts'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpagos", f"{int(res_actual['v_post'] or 0)}", f"Meta: {m['target_postpago']}")
#         porta_real_pct = (res_actual['v_porta'] / res_actual['v_post'] * 100) if res_actual['v_post'] and res_actual['v_post'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res_actual['v_fibra'] or 0)}", f"Meta: {m['target_fibra']}")

#         c5, c6, c7 = st.columns(3)
#         c5.metric("Seguros", f"{int(res_actual['v_seguros'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res_actual['v_renov'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res_actual['v_womgo'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.warning("No hay metas configuradas para este periodo.")

#     st.divider()
#     st.subheader("👤 Rendimiento Individual")
    
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.id, s.name as Vendedor, 
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.total_points ELSE 0 END), 0) as Puntos,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.total_commission ELSE 0 END), 0) as Comision,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as v_fibra,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' THEN v.has_insurance ELSE 0 END), 0) as v_seguros,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_renov,
#                COALESCE(SUM(CASE WHEN v.status = 'Aprobada' AND v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_womgo,
#                COALESCE(t.target_points, 0) as m_points,
#                COALESCE(t.target_postpago, 0) as m_post,
#                COALESCE(t.target_fibra, 0) as m_fibra,
#                COALESCE(t.target_seguro, 0) as m_seguro,
#                COALESCE(t.target_renovacion, 0) as m_renov,
#                COALESCE(t.target_womgo, 0) as m_womgo
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1
#         GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             col_info, col_prog = st.columns([1, 4])
#             puntos = row['Puntos']
#             meta_pts = row['m_points']
#             cumplimiento = (puntos / meta_pts) if meta_pts > 0 else 0
            
#             with col_info:
#                 st.markdown(f"#### {row['Vendedor']}")
#                 if cumplimiento >= 1.0: st.success("🎯 ¡Meta Lograda!")
#                 elif cumplimiento >= 0.8: st.warning(f"Cerca: {cumplimiento:.1%}")
#                 else: st.error(f"Falta: {cumplimiento:.1%}")
#                 st.write(f"💰 Com: ${row['Comision']:,.0f}")
            
#             with col_prog:
#                 st.write(f"**Puntos:** {int(puntos)} / {int(meta_pts)}")
#                 st.progress(min(cumplimiento, 1.0))
                
#                 d1, d2, d3, d4, d5 = st.columns(5)
#                 d1.caption("Postpago"); d1.write(f"{int(row['v_post'])}/{int(row['m_post'])}")
#                 d2.caption("Fibra"); d2.write(f"{int(row['v_fibra'])}/{int(row['m_fibra'])}")
#                 d3.caption("Seguros"); d3.write(f"{int(row['v_seguros'])}/{int(row['m_seguro'])}")
#                 d4.caption("Renov."); d4.write(f"{int(row['v_renov'])}/{int(row['m_renov'])}")
#                 d5.caption("Wom Go"); d5.write(f"{int(row['v_womgo'])}/{int(row['m_womgo'])}")
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial por Día")
#     col_f1, _ = st.columns([2, 5])
#     filter_date = col_f1.date_input("Filtrar por día", datetime.now())
    
#     conn = get_connection()
#     query = f'''
#         SELECT v.id, v.date as Fecha, s.name as Vendedor, v.customer_name as Cliente, 
#                v.doc_type as Tipo, v.doc_number as [N° Doc], v.total_points as Pts, v.status as Estado, 
#                v.category_summary, v.device_name, v.imei
#         FROM sales v JOIN sellers s ON v.seller_id = s.id 
#         WHERE v.date = '{filter_date.strftime("%Y-%m-%d")}'
#         ORDER BY v.id DESC
#     '''
#     df_hist = pd.read_sql_query(query, conn)
    
#     if df_hist.empty:
#         st.info("No hay ventas registradas para este día.")
#     else:
#         for _, row in df_hist.iterrows():
#             with st.expander(f"[{row['Tipo']}] {row['N° Doc']} | {row['Vendedor']} | {row['Pts']} pts | [{row['Estado']}]"):
#                 st.write(f"**Cliente:** {row['Cliente']} | **Equipo:** {row['device_name'] or 'N/A'} | **IMEI:** {row['imei'] or 'N/A'}")
#                 st.caption(f"**Categorías:** {row['category_summary']}")
                
#                 c_edit1, c_edit2, c_edit3 = st.columns(3)
#                 new_status = c_edit1.selectbox("Cambiar Estado", ["Aprobada", "Rechazada"], index=0 if row['Estado']=='Aprobada' else 1, key=f"stat_{row['id']}")
#                 if c_edit2.button("Actualizar Estado", key=f"upd_{row['id']}"):
#                     cur = conn.cursor(); cur.execute("UPDATE sales SET status = ? WHERE id = ?", (new_status, row['id']))
#                     conn.commit(); st.success("Actualizado"); time.sleep(0.5); st.rerun()
#                 if c_edit3.button("🗑️ Eliminar Venta", key=f"del_sale_{row['id']}"):
#                     cur = conn.cursor(); cur.execute("DELETE FROM sales WHERE id = ?", (row['id'],))
#                     conn.commit(); st.error("Eliminado"); time.sleep(0.5); st.rerun()
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales"])
    
#     with t1:
#         st.subheader("Gestión de Equipo")
#         sellers_all = get_sellers(only_active=False)
#         for i, s in sellers_all.iterrows():
#             col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
#             col_s1.write(f"**{s['name']}** ({'Activo' if s['active'] else 'Inactivo'})")
#             if col_s2.button("Alternar Activo", key=f"stat_sel_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("UPDATE sellers SET active = ? WHERE id = ?", (0 if s['active'] else 1, s['id']))
#                 conn.commit(); conn.close(); st.rerun()
#             if col_s3.button("Borrar", key=f"del_sel_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller"):
#             n_sel = st.text_input("Nombre Nuevo Vendedor")
#             if st.form_submit_button("Añadir Vendedor") and n_sel:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (n_sel,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="cfg_m")
#         y_t = st.number_input("Año", value=2025, key="cfg_y")
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         st.subheader("🏬 Meta Global de Tienda")
#         with st.form("global_targets"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3, c4 = st.columns(4)
#             g_pts = c1.number_input("Puntos", value=v[4])
#             g_post = c2.number_input("Postpago", value=v[5])
#             g_fib = c3.number_input("Fibra", value=v[7])
#             g_pct = c4.number_input("% Porta", value=float(v[6]))
            
#             c5, c6, c7 = st.columns(3)
#             g_seg = c5.number_input("Seguros", value=v[8])
#             g_ren = c6.number_input("Renovaciones", value=v[9])
#             g_wom = c7.number_input("Wom Go", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                     target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                     target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
#                 conn.commit(); st.success("Meta Global guardada")

#         st.divider()
#         st.subheader("👤 Metas Individuales")
#         act_s = get_sellers()
#         if st.button("🪄 Distribuir Global entre Activos"):
#             if not act_s.empty and g_meta:
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n, g_seg//n, g_ren//n, g_wom//n))
#                 conn.commit(); st.success("Metas distribuidas"); st.rerun()

#         selected_name = st.selectbox("Editar manual para:", act_s['name'].tolist())
#         s_id = act_s[act_s['name'] == selected_name]['id'].values[0]
#         cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#         s_meta = cur.fetchone()
        
#         with st.form("ind_target_form"):
#             sv = s_meta if s_meta else [0]*11
#             sc1, sc2, sc3, sc4 = st.columns(4)
#             si_pts = sc1.number_input("Puntos", value=sv[4])
#             si_post = sc2.number_input("Postpago", value=sv[5])
#             si_fib = sc3.number_input("Fibra", value=sv[7])
#             si_pct = sc4.number_input("% Porta", value=float(sv[6]))
            
#             sc5, sc6, sc7 = st.columns(3)
#             si_seg = sc5.number_input("Seguro", value=sv[8])
#             si_ren = sc6.number_input("Renovación", value=sv[9])
#             si_wom = sc7.number_input("Wom Go", value=sv[10])
            
#             if st.form_submit_button("Guardar Meta Vendedor"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (?,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET 
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                     target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
#                     target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (s_id, m_t, y_t, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
#                 conn.commit(); st.success("Meta Individual actualizada")
#         conn.close()





# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime
# import time

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# # --- ESTILO CSS PERSONALIZADO ---
# st.markdown("""
#     <style>
#     div.stButton > button {
#         width: 100%;
#         border-radius: 5px;
#         height: 3em;
#         background-color: #f0f2f6;
#         border: 1px solid #d1d5db;
#     }
#     div.stButton > button:hover {
#         background-color: #e5e7eb;
#         border: 1px solid #9ca3af;
#     }
#     .active-nav {
#         background-color: #2563eb !important;
#         color: white !important;
#         border: none !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # --- INICIALIZACIÓN DE ESTADO ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
#         CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, store_id INTEGER, active INTEGER DEFAULT 1);
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, month INTEGER, year INTEGER,
#             target_points INTEGER DEFAULT 0, target_postpago INTEGER DEFAULT 0, target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0, target_seguro INTEGER DEFAULT 0, target_renovacion INTEGER DEFAULT 0, target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year)
#         );
#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, seller_id INTEGER,
#             customer_name TEXT, customer_rut TEXT, phone_number TEXT, iccid TEXT,
#             total_amount REAL, total_points INTEGER, total_commission REAL DEFAULT 0,
#             category_summary TEXT, device_name TEXT, imei TEXT, has_insurance INTEGER DEFAULT 0,
#             fiber_plan TEXT, fiber_address TEXT, doc_type TEXT, doc_number TEXT, payment_method TEXT, status TEXT DEFAULT 'Aprobada'
#         );
#         CREATE TABLE IF NOT EXISTS point_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, value REAL, type TEXT);
#     ''')
#     cursor.execute("SELECT COUNT(*) FROM point_rules")
#     if cursor.fetchone()[0] == 0:
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'), ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'), ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'), ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'), ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'), ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'), ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'), ('Fibra', 10, 'points'), ('Seguro', 1500, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
#     conn.commit()
#     conn.close()

# init_db()

# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- NAVEGACIÓN LATERAL POR BOTONES ---
# st.sidebar.title("🛠️ Sales Manager")
# st.sidebar.markdown("---")

# nav_options = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# for opt in nav_options:
#     is_active = st.session_state.menu_option == opt
#     if st.sidebar.button(opt, key=f"nav_{opt}", help=f"Ir a {opt}", use_container_width=True, type="primary" if is_active else "secondary"):
#         st.session_state.menu_option = opt
#         st.rerun()

# choice = st.session_state.menu_option

# # --- SECCIONES ---
# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.warning("⚠️ No hay vendedores activos. Por favor, agregue uno en Configuración.")
#     else:
#         with st.form("main_form", clear_on_submit=False):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()
#             st.subheader("📱 Telefonía y Líneas")
#             col_l1, col_l2, col_l3, col_l4 = st.columns(4)
#             with col_l1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_l2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_l3:
#                 num_tel = st.text_input("Número de Teléfono")
#             with col_l4:
#                 iccid_val = st.text_input("ICCID / Serie SIM")
            
#             tipo_extra = st.selectbox("Otros Planes / Servicios", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2, col_b3 = st.columns(3)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Tipo Venta Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 device_name = st.text_input("Modelo del Equipo")
#             with col_b3:
#                 imei_val = st.text_input("IMEI")
            
#             ins_check = st.checkbox("¿Incluye Seguro?")

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             col_fib1, col_fib2, col_fib3 = st.columns([1,2,2])
#             with col_fib1:
#                 fibra_check = st.selectbox("Venta Fibra", ["No aplica", "Fibra"])
#             with col_fib2:
#                 fib_plan = st.text_input("Plan Fibra")
#             with col_fib3:
#                 fib_addr = st.text_input("Dirección Instalación")

#             st.divider()
#             st.subheader("💳 Pago")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_type = st.selectbox("Documento", ["Boleta", "Factura", "Guía"])
#             with col_p2:
#                 doc_number = st.text_input("N° Documento")
#             with col_p3:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
            
#             if submit:
#                 if not customer or not doc_number:
#                     st.error("Nombre de Cliente y Número de Documento son obligatorios.")
#                 else:
#                     items_sel = [i for i in [tipo_porta, tipo_post, tipo_extra, tipo_equipo, fibra_check] if i != "No aplica"]
#                     puntos = sum(rules.get(item, 0) for item in items_sel)
#                     comis = rules.get("Seguro", 1500) if ins_check else 0
#                     summary = ", ".join(items_sel)

#                     with st.status("Validando y Guardando...", expanded=True) as status:
#                         time.sleep(0.5)
#                         conn = get_connection(); cur = conn.cursor()
#                         cur.execute('''
#                             INSERT INTO sales (
#                                 date, seller_id, customer_name, customer_rut, phone_number, iccid,
#                                 total_amount, total_points, total_commission, category_summary,
#                                 device_name, imei, has_insurance, fiber_plan, fiber_address,
#                                 doc_type, doc_number, payment_method, status
#                             ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                         ''', (
#                             sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                             amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                             fib_plan, fib_addr, doc_type, doc_number, payment_method, 'Aprobada'
#                         ))
#                         conn.commit(); conn.close()
#                         time.sleep(0.5)
#                         status.update(label="Venta Registrada!", state="complete", expanded=False)
                    
#                     st.balloons()
#                     time.sleep(1)
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Resumen de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query_total = f'''
#         SELECT SUM(total_points) as tp, SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as vp,
#         SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as vpt,
#         SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as vf,
#         SUM(has_insurance) as vs, SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as vr,
#         SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as vw
#         FROM sales WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' AND status = 'Aprobada'
#     '''
#     res = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_g = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_g.empty:
#         m = meta_g.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos", f"{int(res['tp'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpago", f"{int(res['vp'] or 0)}", f"Meta: {m['target_postpago']}")
#         c3.metric("Fibra", f"{int(res['vf'] or 0)}", f"Meta: {m['target_fibra']}")
#         c4.metric("Seguros", f"{int(res['vs'] or 0)}", f"Meta: {m['target_seguro']}")
#     else:
#         st.info("Configura las metas del mes para ver el progreso.")

#     st.divider()
#     st.subheader("👤 Rendimiento por Vendedor")
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.name as Vendedor, COALESCE(SUM(v.total_points), 0) as Pts, COALESCE(t.target_points, 0) as Meta
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND v.status = 'Aprobada' AND strftime('%m', v.date) = '{month:02}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1 GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         meta_pts = row['Meta'] if row['Meta'] > 0 else 1
#         prog = min(row['Pts'] / meta_pts, 1.0)
#         st.write(f"**{row['Vendedor']}** - {int(row['Pts'])} / {int(row['Meta'])} Puntos")
#         st.progress(prog)
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial")
#     filter_date = st.date_input("Fecha", datetime.now())
#     conn = get_connection()
#     df_hist = pd.read_sql_query(f'''
#         SELECT v.id, v.date, s.name as Vendedor, v.customer_name as Cliente, v.phone_number, v.total_points as Pts, v.status
#         FROM sales v JOIN sellers s ON v.seller_id = s.id WHERE v.date = '{filter_date}'
#     ''', conn)
    
#     if df_hist.empty:
#         st.info("Sin ventas registradas.")
#     else:
#         st.dataframe(df_hist, use_container_width=True)
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2 = st.tabs(["Vendedores", "Metas"])
    
#     with t1:
#         sellers_all = get_sellers(only_active=False)
#         for _, s in sellers_all.iterrows():
#             c_s1, c_s2 = st.columns([4, 1])
#             c_s1.write(f"{s['name']} ({'Activo' if s['active'] else 'Inactivo'})")
#             if c_s2.button("🗑️", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller_fixed"):
#             new_n = st.text_input("Nombre Vendedor")
#             if st.form_submit_button("Agregar") and new_n:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_n,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         st.subheader("Configurar Metas")
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month-1, key="meta_m")
#         y_t = datetime.now().year
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone() or [0]*11
        
#         with st.form("form_metas"):
#             st.write("Meta Global Tienda")
#             gc1, gc2, gc3, gc4 = st.columns(4)
#             gp = gc1.number_input("Puntos", value=g_meta[4])
#             gps = gc2.number_input("Postpago", value=g_meta[5])
#             gf = gc3.number_input("Fibra", value=g_meta[7])
#             gs = gc4.number_input("Seguros", value=g_meta[8])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_fibra, target_seguro)
#                                VALUES (0,?,?,?,?,?,?) ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                                target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                                target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro''',
#                             (m_t, y_t, gp, gps, gf, gs))
#                 conn.commit(); st.success("Meta guardada")
        
#         st.divider()
#         act_s = get_sellers()
#         if not act_s.empty:
#             if st.button("🪄 Dividir Metas entre Vendedores"):
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_fibra, target_seguro)
#                                    VALUES (?,?,?,?,?,?,?) ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                                    target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                                    target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro''',
#                                 (s['id'], m_t, y_t, gp//n, gps//n, gf//n, gs//n))
#                 conn.commit(); st.success("Metas distribuidas")
#         conn.close()






# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime
# import time

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# # --- ESTILO CSS PERSONALIZADO ---
# st.markdown("""
#     <style>
#     div.stButton > button {
#         width: 100%;
#         border-radius: 5px;
#         height: 3em;
#         background-color: #f0f2f6;
#         border: 1px solid #d1d5db;
#     }
#     div.stButton > button:hover {
#         background-color: #e5e7eb;
#         border: 1px solid #9ca3af;
#     }
#     .active-nav {
#         background-color: #2563eb !important;
#         color: white !important;
#         border: none !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # --- INICIALIZACIÓN DE ESTADO ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
#         CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, store_id INTEGER, active INTEGER DEFAULT 1);
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, month INTEGER, year INTEGER,
#             target_points INTEGER DEFAULT 0, target_postpago INTEGER DEFAULT 0, target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0, target_seguro INTEGER DEFAULT 0, target_renovacion INTEGER DEFAULT 0, target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year)
#         );
#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, seller_id INTEGER,
#             customer_name TEXT, customer_rut TEXT, phone_number TEXT, iccid TEXT,
#             total_amount REAL, total_points INTEGER, total_commission REAL DEFAULT 0,
#             category_summary TEXT, device_name TEXT, imei TEXT, has_insurance INTEGER DEFAULT 0,
#             fiber_plan TEXT, fiber_address TEXT, doc_type TEXT, doc_number TEXT, payment_method TEXT, status TEXT DEFAULT 'Aprobada'
#         );
#         CREATE TABLE IF NOT EXISTS point_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, value REAL, type TEXT);
#     ''')
#     cursor.execute("SELECT COUNT(*) FROM point_rules")
#     if cursor.fetchone()[0] == 0:
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'), ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'), ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'), ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'), ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'), ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'), ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'), ('Fibra', 10, 'points'), ('Seguro', 1500, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
#     conn.commit()
#     conn.close()

# init_db()

# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- NAVEGACIÓN LATERAL POR BOTONES ---
# st.sidebar.title("🛠️ Sales Manager")
# st.sidebar.markdown("---")

# nav_options = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# for opt in nav_options:
#     is_active = st.session_state.menu_option == opt
#     if st.sidebar.button(opt, key=f"nav_{opt}", help=f"Ir a {opt}", use_container_width=True, type="primary" if is_active else "secondary"):
#         st.session_state.menu_option = opt
#         st.rerun()

# choice = st.session_state.menu_option

# # --- SECCIONES ---
# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.warning("⚠️ No hay vendedores activos. Por favor, agregue uno en Configuración.")
#     else:
#         with st.form("main_form", clear_on_submit=False):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()
#             st.subheader("📱 Telefonía y Líneas")
#             col_l1, col_l2, col_l3, col_l4 = st.columns(4)
#             with col_l1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_l2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_l3:
#                 num_tel = st.text_input("Número de Teléfono")
#             with col_l4:
#                 iccid_val = st.text_input("ICCID / Serie SIM")
            
#             tipo_extra = st.selectbox("Otros Planes / Servicios", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2, col_b3 = st.columns(3)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Tipo Venta Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 device_name = st.text_input("Modelo del Equipo")
#             with col_b3:
#                 imei_val = st.text_input("IMEI")
            
#             ins_check = st.checkbox("¿Incluye Seguro?")

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             col_fib1, col_fib2, col_fib3 = st.columns([1,2,2])
#             with col_fib1:
#                 fibra_check = st.selectbox("Venta Fibra", ["No aplica", "Fibra"])
#             with col_fib2:
#                 fib_plan = st.text_input("Plan Fibra")
#             with col_fib3:
#                 fib_addr = st.text_input("Dirección Instalación")

#             st.divider()
#             st.subheader("💳 Pago")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_type = st.selectbox("Documento", ["Boleta", "Factura", "Guía"])
#             with col_p2:
#                 doc_number = st.text_input("N° Documento")
#             with col_p3:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
            
#             if submit:
#                 if not customer or not doc_number:
#                     st.error("Nombre de Cliente y Número de Documento son obligatorios.")
#                 else:
#                     items_sel = [i for i in [tipo_porta, tipo_post, tipo_extra, tipo_equipo, fibra_check] if i != "No aplica"]
#                     puntos = sum(rules.get(item, 0) for item in items_sel)
#                     comis = rules.get("Seguro", 1500) if ins_check else 0
#                     summary = ", ".join(items_sel)

#                     with st.status("Validando y Guardando...", expanded=True) as status:
#                         time.sleep(0.5)
#                         conn = get_connection(); cur = conn.cursor()
#                         cur.execute('''
#                             INSERT INTO sales (
#                                 date, seller_id, customer_name, customer_rut, phone_number, iccid,
#                                 total_amount, total_points, total_commission, category_summary,
#                                 device_name, imei, has_insurance, fiber_plan, fiber_address,
#                                 doc_type, doc_number, payment_method, status
#                             ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                         ''', (
#                             sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                             amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                             fib_plan, fib_addr, doc_type, doc_number, payment_method, 'Aprobada'
#                         ))
#                         conn.commit(); conn.close()
#                         time.sleep(0.5)
#                         status.update(label="Venta Registrada!", state="complete", expanded=False)
                    
#                     st.balloons()
#                     time.sleep(1)
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Resumen de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as tp, 
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as vp,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as vpt,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as vf,
#             SUM(has_insurance) as vs, 
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as vr,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as vw
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' AND status = 'Aprobada'
#     '''
#     res = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_g = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_g.empty:
#         m = meta_g.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos", f"{int(res['tp'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpago", f"{int(res['vp'] or 0)}", f"Meta: {m['target_postpago']}")
        
#         porta_real_pct = (res['vpt'] / res['vp'] * 100) if res['vp'] and res['vp'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res['vf'] or 0)}", f"Meta: {m['target_fibra']}")

#         st.write("---")
#         c5, c6, c7 = st.columns(3)
#         c5.metric("Seguros", f"{int(res['vs'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res['vr'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res['vw'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.info("Configura las metas del mes para ver el progreso.")

#     st.divider()
#     st.subheader("👤 Rendimiento por Vendedor")
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.name as Vendedor, 
#                COALESCE(SUM(v.total_points), 0) as Pts, 
#                COALESCE(t.target_points, 0) as Meta,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(t.target_postpago, 0) as m_post
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND v.status = 'Aprobada' AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1 GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             meta_pts = row['Meta'] if row['Meta'] > 0 else 1
#             prog = min(row['Pts'] / meta_pts, 1.0)
#             st.write(f"**{row['Vendedor']}**")
#             st.write(f"Puntos: {int(row['Pts'])} / {int(row['Meta'])}")
#             st.progress(prog)
#             st.caption(f"Postpagos: {int(row['v_post'])} / {int(row['m_post'])}")
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial")
#     filter_date = st.date_input("Fecha", datetime.now())
#     conn = get_connection()
#     df_hist = pd.read_sql_query(f'''
#         SELECT v.id, v.date, s.name as Vendedor, v.customer_name as Cliente, v.phone_number, v.total_points as Pts, v.status, v.device_name, v.imei
#         FROM sales v JOIN sellers s ON v.seller_id = s.id WHERE v.date = '{filter_date}'
#     ''', conn)
    
#     if df_hist.empty:
#         st.info("Sin ventas registradas.")
#     else:
#         st.dataframe(df_hist, use_container_width=True)
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales"])
    
#     with t1:
#         sellers_all = get_sellers(only_active=False)
#         for _, s in sellers_all.iterrows():
#             c_s1, c_s2 = st.columns([4, 1])
#             c_s1.write(f"{s['name']} ({'Activo' if s['active'] else 'Inactivo'})")
#             if c_s2.button("🗑️", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller_fixed"):
#             new_n = st.text_input("Nombre Vendedor")
#             if st.form_submit_button("Agregar") and new_n:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_n,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="cfg_m")
#         y_t = st.number_input("Año", value=2025, key="cfg_y")
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         st.subheader("🏬 Meta Global de Tienda")
#         with st.form("global_targets"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3, c4 = st.columns(4)
#             g_pts = c1.number_input("Puntos", value=v[4])
#             g_post = c2.number_input("Postpago", value=v[5])
#             g_fib = c3.number_input("Fibra", value=v[7])
#             g_pct = c4.number_input("% Porta", value=float(v[6]))
            
#             c5, c6, c7 = st.columns(3)
#             g_seg = c5.number_input("Seguros", value=v[8])
#             g_ren = c6.number_input("Renovaciones", value=v[9])
#             g_wom = c7.number_input("Wom Go", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                     target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                     target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
#                 conn.commit(); st.success("Meta Global guardada")

#         st.divider()
#         st.subheader("👤 Metas Individuales")
#         act_s = get_sellers()
#         if not act_s.empty:
#             if st.button("🪄 Distribuir Global entre Activos"):
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n, g_seg//n, g_ren//n, g_wom//n))
#                 conn.commit(); st.success("Metas distribuidas"); st.rerun()

#             selected_name = st.selectbox("Editar manual para:", act_s['name'].tolist())
#             s_id = act_s[act_s['name'] == selected_name]['id'].values[0]
#             cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#             s_meta = cur.fetchone()
            
#             with st.form("ind_target_form"):
#                 sv = s_meta if s_meta else [0]*11
#                 sc1, sc2, sc3, sc4 = st.columns(4)
#                 si_pts = sc1.number_input("Puntos", value=sv[4])
#                 si_post = sc2.number_input("Postpago", value=sv[5])
#                 si_fib = sc3.number_input("Fibra", value=sv[7])
#                 si_pct = sc4.number_input("% Porta", value=float(sv[6]))
                
#                 sc5, sc6, sc7 = st.columns(3)
#                 si_seg = sc5.number_input("Seguro", value=sv[8])
#                 si_ren = sc6.number_input("Renovación", value=sv[9])
#                 si_wom = sc7.number_input("Wom Go", value=sv[10])
                
#                 if st.form_submit_button("Guardar Meta Vendedor"):
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET 
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s_id, m_t, y_t, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
#                     conn.commit(); st.success("Meta Individual actualizada")
#         conn.close()





# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime
# import time

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# # --- ESTILO CSS PERSONALIZADO ---
# st.markdown("""
#     <style>
#     div.stButton > button {
#         width: 100%;
#         border-radius: 5px;
#         height: 3em;
#         background-color: #f0f2f6;
#         border: 1px solid #d1d5db;
#     }
#     div.stButton > button:hover {
#         background-color: #e5e7eb;
#         border: 1px solid #9ca3af;
#     }
#     .active-nav {
#         background-color: #2563eb !important;
#         color: white !important;
#         border: none !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # --- INICIALIZACIÓN DE ESTADO ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
#         CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, store_id INTEGER, active INTEGER DEFAULT 1);
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, month INTEGER, year INTEGER,
#             target_points INTEGER DEFAULT 0, target_postpago INTEGER DEFAULT 0, target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0, target_seguro INTEGER DEFAULT 0, target_renovacion INTEGER DEFAULT 0, target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year)
#         );
#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, seller_id INTEGER,
#             customer_name TEXT, customer_rut TEXT, phone_number TEXT, iccid TEXT,
#             total_amount REAL, total_points INTEGER, total_commission REAL DEFAULT 0,
#             category_summary TEXT, device_name TEXT, imei TEXT, has_insurance INTEGER DEFAULT 0,
#             fiber_plan TEXT, fiber_address TEXT, doc_type TEXT, doc_number TEXT, payment_method TEXT, status TEXT DEFAULT 'Aprobada'
#         );
#         CREATE TABLE IF NOT EXISTS point_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, value REAL, type TEXT);
#     ''')
#     cursor.execute("SELECT COUNT(*) FROM point_rules")
#     if cursor.fetchone()[0] == 0:
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'), ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'), ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'), ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'), ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'), ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'), ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'), ('Fibra', 10, 'points'), ('Seguro', 1500, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
#     conn.commit()
#     conn.close()

# init_db()

# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- NAVEGACIÓN LATERAL POR BOTONES ---
# st.sidebar.title("🛠️ Sales Manager")
# st.sidebar.markdown("---")

# nav_options = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# for opt in nav_options:
#     is_active = st.session_state.menu_option == opt
#     if st.sidebar.button(opt, key=f"nav_{opt}", help=f"Ir a {opt}", use_container_width=True, type="primary" if is_active else "secondary"):
#         st.session_state.menu_option = opt
#         st.rerun()

# choice = st.session_state.menu_option

# # --- SECCIONES ---
# if choice == "Registrar Venta":
#     st.header("📝 Nueva Venta")
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     if sellers_df.empty:
#         st.warning("⚠️ No hay vendedores activos. Por favor, agregue uno en Configuración.")
#     else:
#         with st.form("main_form", clear_on_submit=False):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", options=sellers_df['id'].tolist(), format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente")
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente")
#             with col_g4:
#                 sale_date = st.date_input("Fecha", datetime.now())
            
#             st.divider()
#             st.subheader("📱 Telefonía y Líneas")
#             col_l1, col_l2, col_l3, col_l4 = st.columns(4)
#             with col_l1:
#                 tipo_porta = st.selectbox("Portabilidad", ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"])
#             with col_l2:
#                 tipo_post = st.selectbox("Postpago", ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"])
#             with col_l3:
#                 num_tel = st.text_input("Número de Teléfono")
#             with col_l4:
#                 iccid_val = st.text_input("ICCID / Serie SIM")
            
#             tipo_extra = st.selectbox("Otros Planes / Servicios", ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"])

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2, col_b3 = st.columns(3)
#             with col_b1:
#                 tipo_equipo = st.selectbox("Tipo Venta Equipo", ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"])
#             with col_b2:
#                 device_name = st.text_input("Modelo del Equipo")
#             with col_b3:
#                 imei_val = st.text_input("IMEI")
            
#             ins_check = st.checkbox("¿Incluye Seguro?")

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             col_fib1, col_fib2, col_fib3 = st.columns([1,2,2])
#             with col_fib1:
#                 fibra_check = st.selectbox("Venta Fibra", ["No aplica", "Fibra"])
#             with col_fib2:
#                 fib_plan = st.text_input("Plan Fibra")
#             with col_fib3:
#                 fib_addr = st.text_input("Dirección Instalación")

#             st.divider()
#             st.subheader("💳 Pago")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_type = st.selectbox("Documento", ["Boleta", "Factura", "Guía"])
#             with col_p2:
#                 doc_number = st.text_input("N° Documento")
#             with col_p3:
#                 payment_method = st.selectbox("Método de Pago", ["Efectivo", "Débito", "Crédito"])
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0)
            
#             submit = st.form_submit_button("💾 GUARDAR VENTA")
            
#             if submit:
#                 if not customer or not doc_number:
#                     st.error("Nombre de Cliente y Número de Documento son obligatorios.")
#                 else:
#                     items_sel = [i for i in [tipo_porta, tipo_post, tipo_extra, tipo_equipo, fibra_check] if i != "No aplica"]
#                     puntos = sum(rules.get(item, 0) for item in items_sel)
#                     comis = rules.get("Seguro", 1500) if ins_check else 0
#                     summary = ", ".join(items_sel)

#                     with st.status("Validando y Guardando...", expanded=True) as status:
#                         time.sleep(0.5)
#                         conn = get_connection(); cur = conn.cursor()
#                         cur.execute('''
#                             INSERT INTO sales (
#                                 date, seller_id, customer_name, customer_rut, phone_number, iccid,
#                                 total_amount, total_points, total_commission, category_summary,
#                                 device_name, imei, has_insurance, fiber_plan, fiber_address,
#                                 doc_type, doc_number, payment_method, status
#                             ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                         ''', (
#                             sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                             amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                             fib_plan, fib_addr, doc_type, doc_number, payment_method, 'Aprobada'
#                         ))
#                         conn.commit(); conn.close()
#                         time.sleep(0.5)
#                         status.update(label="Venta Registrada!", state="complete", expanded=False)
                    
#                     st.balloons()
#                     time.sleep(1)
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Resumen de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as tp, 
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as vp,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as vpt,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as vf,
#             SUM(has_insurance) as vs, 
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as vr,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as vw
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' AND status = 'Aprobada'
#     '''
#     res = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_g = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_g.empty:
#         m = meta_g.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos", f"{int(res['tp'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpago", f"{int(res['vp'] or 0)}", f"Meta: {m['target_postpago']}")
        
#         porta_real_pct = (res['vpt'] / res['vp'] * 100) if res['vp'] and res['vp'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res['vf'] or 0)}", f"Meta: {m['target_fibra']}")

#         st.write("---")
#         c5, c6, c7 = st.columns(3)
#         c5.metric("Seguros", f"{int(res['vs'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res['vr'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res['vw'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.info("Configura las metas del mes para ver el progreso.")

#     st.divider()
#     st.subheader("👤 Rendimiento por Vendedor")
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.name as Vendedor, 
#                COALESCE(SUM(v.total_points), 0) as Pts, 
#                COALESCE(t.target_points, 0) as Meta,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(t.target_postpago, 0) as m_post,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as v_fibra,
#                COALESCE(t.target_fibra, 0) as m_fibra,
#                COALESCE(SUM(v.has_insurance), 0) as v_seguro,
#                COALESCE(t.target_seguro, 0) as m_seguro,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_reno,
#                COALESCE(t.target_renovacion, 0) as m_reno,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_wom,
#                COALESCE(t.target_womgo, 0) as m_wom
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND v.status = 'Aprobada' AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1 GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             meta_pts = row['Meta'] if row['Meta'] > 0 else 1
#             prog = min(row['Pts'] / meta_pts, 1.0)
#             st.write(f"**{row['Vendedor']}**")
            
#             col_ind1, col_ind2 = st.columns([1, 1])
#             with col_ind1:
#                 st.write(f"Puntos: {int(row['Pts'])} / {int(row['Meta'])}")
#                 st.progress(prog)
#             with col_ind2:
#                 # Resumen compacto de metas clave
#                 st.caption(f"Postpagos: {int(row['v_post'])}/{int(row['m_post'])} | Fibra: {int(row['v_fibra'])}/{int(row['m_fibra'])}")
#                 st.caption(f"Seguros: {int(row['v_seguro'])}/{int(row['m_seguro'])} | Reno: {int(row['v_reno'])}/{int(row['m_reno'])}")
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial")
#     filter_date = st.date_input("Fecha", datetime.now())
#     conn = get_connection()
#     df_hist = pd.read_sql_query(f'''
#         SELECT v.id, v.date, s.name as Vendedor, v.customer_name as Cliente, v.phone_number, v.total_points as Pts, v.status, v.device_name, v.imei
#         FROM sales v JOIN sellers s ON v.seller_id = s.id WHERE v.date = '{filter_date}'
#     ''', conn)
    
#     if df_hist.empty:
#         st.info("Sin ventas registradas.")
#     else:
#         st.dataframe(df_hist, use_container_width=True)
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2, t3 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales", "💎 Reglas de Puntos"])
    
#     with t1:
#         sellers_all = get_sellers(only_active=False)
#         for _, s in sellers_all.iterrows():
#             c_s1, c_s2 = st.columns([4, 1])
#             c_s1.write(f"{s['name']} ({'Activo' if s['active'] else 'Inactivo'})")
#             if c_s2.button("🗑️", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller_fixed"):
#             new_n = st.text_input("Nombre Vendedor")
#             if st.form_submit_button("Agregar") and new_n:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_n,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="cfg_m")
#         y_t = st.number_input("Año", value=2025, key="cfg_y")
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         st.subheader("🏬 Meta Global de Tienda")
#         with st.form("global_targets"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3, c4 = st.columns(4)
#             g_pts = c1.number_input("Puntos", value=v[4])
#             g_post = c2.number_input("Postpago", value=v[5])
#             g_fib = c3.number_input("Fibra", value=v[7])
#             g_pct = c4.number_input("% Porta", value=float(v[6]))
            
#             c5, c6, c7 = st.columns(3)
#             g_seg = c5.number_input("Seguros", value=v[8])
#             g_ren = c6.number_input("Renovaciones", value=v[9])
#             g_wom = c7.number_input("Wom Go", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                     target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                     target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
#                 conn.commit(); st.success("Meta Global guardada")

#         st.divider()
#         st.subheader("👤 Metas Individuales")
#         act_s = get_sellers()
#         if not act_s.empty:
#             if st.button("🪄 Distribuir Global entre Activos"):
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n, g_seg//n, g_ren//n, g_wom//n))
#                 conn.commit(); st.success("Metas distribuidas"); st.rerun()

#             selected_name = st.selectbox("Editar manual para:", act_s['name'].tolist())
#             s_id = act_s[act_s['name'] == selected_name]['id'].values[0]
#             cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#             s_meta = cur.fetchone()
            
#             with st.form("ind_target_form"):
#                 sv = s_meta if s_meta else [0]*11
#                 sc1, sc2, sc3, sc4 = st.columns(4)
#                 si_pts = sc1.number_input("Puntos", value=sv[4])
#                 si_post = sc2.number_input("Postpago", value=sv[5])
#                 si_fib = sc3.number_input("Fibra", value=sv[7])
#                 si_pct = sc4.number_input("% Porta", value=float(sv[6]))
                
#                 sc5, sc6, sc7 = st.columns(3)
#                 si_seg = sc5.number_input("Seguro", value=sv[8])
#                 si_ren = sc6.number_input("Renovación", value=sv[9])
#                 si_wom = sc7.number_input("Wom Go", value=sv[10])
                
#                 if st.form_submit_button("Guardar Meta Vendedor"):
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET 
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s_id, m_t, y_t, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
#                     conn.commit(); st.success("Meta Individual actualizada")
#         conn.close()

#     with t3:
#         st.subheader("Valor de Puntos por Producto")
#         conn = get_connection()
#         df_rules = pd.read_sql_query("SELECT * FROM point_rules", conn)
        
#         with st.form("edit_rules_form"):
#             for idx, row in df_rules.iterrows():
#                 col_r1, col_r2 = st.columns([3, 1])
#                 col_r1.write(f"**{row['item_name']}** ({row['type']})")
#                 new_val = col_r2.number_input("Valor", value=float(row['value']), key=f"rule_{row['id']}")
#                 df_rules.at[idx, 'value'] = new_val
            
#             if st.form_submit_button("Actualizar Reglas de Puntos"):
#                 cur = conn.cursor()
#                 for _, r in df_rules.iterrows():
#                     cur.execute("UPDATE point_rules SET value = ? WHERE id = ?", (r['value'], r['id']))
#                 conn.commit()
#                 st.success("Reglas actualizadas correctamente")
#         conn.close()




# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime
# import time

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# # --- ESTILO CSS PERSONALIZADO ---
# st.markdown("""
#     <style>
#     div.stButton > button {
#         width: 100%;
#         border-radius: 5px;
#         height: 3em;
#         background-color: #f0f2f6;
#         border: 1px solid #d1d5db;
#     }
#     div.stButton > button:hover {
#         background-color: #e5e7eb;
#         border: 1px solid #9ca3af;
#     }
#     .active-nav {
#         background-color: #2563eb !important;
#         color: white !important;
#         border: none !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # --- INICIALIZACIÓN DE ESTADO ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"
# if 'editing_sale' not in st.session_state:
#     st.session_state.editing_sale = None

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
#         CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, store_id INTEGER, active INTEGER DEFAULT 1);
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, month INTEGER, year INTEGER,
#             target_points INTEGER DEFAULT 0, target_postpago INTEGER DEFAULT 0, target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0, target_seguro INTEGER DEFAULT 0, target_renovacion INTEGER DEFAULT 0, target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year)
#         );
#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, seller_id INTEGER,
#             customer_name TEXT, customer_rut TEXT, phone_number TEXT, iccid TEXT,
#             total_amount REAL, total_points INTEGER, total_commission REAL DEFAULT 0,
#             category_summary TEXT, device_name TEXT, imei TEXT, has_insurance INTEGER DEFAULT 0,
#             fiber_plan TEXT, fiber_address TEXT, doc_type TEXT, doc_number TEXT, payment_method TEXT, status TEXT DEFAULT 'Aprobada'
#         );
#         CREATE TABLE IF NOT EXISTS point_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, value REAL, type TEXT);
#     ''')
#     cursor.execute("SELECT COUNT(*) FROM point_rules")
#     if cursor.fetchone()[0] == 0:
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'), ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'), ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'), ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'), ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'), ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'), ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'), ('Fibra', 10, 'points'), ('Seguro', 1500, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
#     conn.commit()
#     conn.close()

# init_db()

# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- NAVEGACIÓN LATERAL POR BOTONES ---
# st.sidebar.title("🛠️ Sales Manager")
# st.sidebar.markdown("---")

# nav_options = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# for opt in nav_options:
#     is_active = st.session_state.menu_option == opt
#     if st.sidebar.button(opt, key=f"nav_{opt}", help=f"Ir a {opt}", use_container_width=True, type="primary" if is_active else "secondary"):
#         st.session_state.menu_option = opt
#         st.session_state.editing_sale = None
#         st.rerun()

# choice = st.session_state.menu_option

# # --- SECCIONES ---
# if choice == "Registrar Venta":
#     is_edit = st.session_state.editing_sale is not None
#     st.header("📝 Editar Venta" if is_edit else "📝 Nueva Venta")
    
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     # Cargar datos si es edición
#     sale_data = {}
#     if is_edit:
#         conn = get_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM sales WHERE id = ?", (st.session_state.editing_sale,))
#         cols = [column[0] for column in cur.description]
#         row = cur.fetchone()
#         sale_data = dict(zip(cols, row))
#         conn.close()

#     if sellers_df.empty:
#         st.warning("⚠️ No hay vendedores activos. Por favor, agregue uno en Configuración.")
#     else:
#         with st.form("main_form", clear_on_submit=False):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", 
#                                         options=sellers_df['id'].tolist(), 
#                                         index=sellers_df['id'].tolist().index(sale_data['seller_id']) if is_edit else 0,
#                                         format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente", value=sale_data.get('customer_name', ""))
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente", value=sale_data.get('customer_rut', ""))
#             with col_g4:
#                 default_date = datetime.strptime(sale_data['date'], "%Y-%m-%d") if is_edit else datetime.now()
#                 sale_date = st.date_input("Fecha", default_date)
            
#             st.divider()
#             st.subheader("📱 Telefonía y Líneas")
#             summary_list = sale_data.get('category_summary', "").split(", ")
            
#             col_l1, col_l2, col_l3, col_l4 = st.columns(4)
#             with col_l1:
#                 porta_opts = ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"]
#                 def_porta = next((i for i in porta_opts if i in summary_list), "No aplica")
#                 tipo_porta = st.selectbox("Portabilidad", porta_opts, index=porta_opts.index(def_porta))
#             with col_l2:
#                 post_opts = ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"]
#                 def_post = next((i for i in post_opts if i in summary_list), "No aplica")
#                 tipo_post = st.selectbox("Postpago", post_opts, index=post_opts.index(def_post))
#             with col_l3:
#                 num_tel = st.text_input("Número de Teléfono", value=sale_data.get('phone_number', ""))
#             with col_l4:
#                 iccid_val = st.text_input("ICCID / Serie SIM", value=sale_data.get('iccid', ""))
            
#             extra_opts = ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"]
#             def_extra = next((i for i in extra_opts if i in summary_list), "No aplica")
#             tipo_extra = st.selectbox("Otros Planes / Servicios", extra_opts, index=extra_opts.index(def_extra))

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2, col_b3 = st.columns(3)
#             with col_b1:
#                 equipo_opts = ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"]
#                 def_eq = next((i for i in equipo_opts if i in summary_list), "No aplica")
#                 tipo_equipo = st.selectbox("Tipo Venta Equipo", equipo_opts, index=equipo_opts.index(def_eq))
#             with col_b2:
#                 device_name = st.text_input("Modelo del Equipo", value=sale_data.get('device_name', ""))
#             with col_b3:
#                 imei_val = st.text_input("IMEI", value=sale_data.get('imei', ""))
            
#             ins_check = st.checkbox("¿Incluye Seguro?", value=bool(sale_data.get('has_insurance', 0)))

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             col_fib1, col_fib2, col_fib3 = st.columns([1,2,2])
#             with col_fib1:
#                 fibra_opts = ["No aplica", "Fibra"]
#                 def_fib = "Fibra" if "Fibra" in summary_list else "No aplica"
#                 fibra_check = st.selectbox("Venta Fibra", fibra_opts, index=fibra_opts.index(def_fib))
#             with col_fib2:
#                 fib_plan = st.text_input("Plan Fibra", value=sale_data.get('fiber_plan', ""))
#             with col_fib3:
#                 fib_addr = st.text_input("Dirección Instalación", value=sale_data.get('fiber_address', ""))

#             st.divider()
#             st.subheader("💳 Pago")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_opts = ["Boleta", "Factura", "Guía"]
#                 doc_type = st.selectbox("Documento", doc_opts, index=doc_opts.index(sale_data.get('doc_type', "Boleta")))
#             with col_p2:
#                 doc_number = st.text_input("N° Documento", value=sale_data.get('doc_number', ""))
#             with col_p3:
#                 pay_opts = ["Efectivo", "Débito", "Crédito"]
#                 payment_method = st.selectbox("Método de Pago", pay_opts, index=pay_opts.index(sale_data.get('payment_method', "Efectivo")))
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0, value=float(sale_data.get('total_amount', 0.0)))
            
#             btn_label = "💾 ACTUALIZAR VENTA" if is_edit else "💾 GUARDAR VENTA"
#             submit = st.form_submit_button(btn_label)
            
#             if is_edit:
#                 if st.form_submit_button("❌ CANCELAR EDICIÓN"):
#                     st.session_state.editing_sale = None
#                     st.session_state.menu_option = "Historial"
#                     st.rerun()
            
#             if submit:
#                 if not customer or not doc_number:
#                     st.error("Nombre de Cliente y Número de Documento son obligatorios.")
#                 else:
#                     items_sel = [i for i in [tipo_porta, tipo_post, tipo_extra, tipo_equipo, fibra_check] if i != "No aplica"]
#                     puntos = sum(rules.get(item, 0) for item in items_sel)
#                     comis = rules.get("Seguro", 1500) if ins_check else 0
#                     summary = ", ".join(items_sel)

#                     with st.status("Procesando...", expanded=True) as status:
#                         time.sleep(0.5)
#                         conn = get_connection(); cur = conn.cursor()
#                         if is_edit:
#                             cur.execute('''
#                                 UPDATE sales SET 
#                                     date=?, seller_id=?, customer_name=?, customer_rut=?, phone_number=?, iccid=?,
#                                     total_amount=?, total_points=?, total_commission=?, category_summary=?,
#                                     device_name=?, imei=?, has_insurance=?, fiber_plan=?, fiber_address=?,
#                                     doc_type=?, doc_number=?, payment_method=?
#                                 WHERE id = ?
#                             ''', (
#                                 sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                                 amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                                 fib_plan, fib_addr, doc_type, doc_number, payment_method, st.session_state.editing_sale
#                             ))
#                         else:
#                             cur.execute('''
#                                 INSERT INTO sales (
#                                     date, seller_id, customer_name, customer_rut, phone_number, iccid,
#                                     total_amount, total_points, total_commission, category_summary,
#                                     device_name, imei, has_insurance, fiber_plan, fiber_address,
#                                     doc_type, doc_number, payment_method, status
#                                 ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                             ''', (
#                                 sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                                 amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                                 fib_plan, fib_addr, doc_type, doc_number, payment_method, 'Aprobada'
#                             ))
#                         conn.commit(); conn.close()
#                         time.sleep(0.5)
#                         status.update(label="¡Listo!", state="complete", expanded=False)
                    
#                     st.session_state.editing_sale = None
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Resumen de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as tp, 
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as vp,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as vpt,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as vf,
#             SUM(has_insurance) as vs, 
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as vr,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as vw
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' AND status = 'Aprobada'
#     '''
#     res = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_g = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_g.empty:
#         m = meta_g.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos", f"{int(res['tp'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpago", f"{int(res['vp'] or 0)}", f"Meta: {m['target_postpago']}")
        
#         porta_real_pct = (res['vpt'] / res['vp'] * 100) if res['vp'] and res['vp'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res['vf'] or 0)}", f"Meta: {m['target_fibra']}")

#         st.write("---")
#         c5, c6, c7 = st.columns(3)
#         c5.metric("Seguros", f"{int(res['vs'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res['vr'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res['vw'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.info("Configura las metas del mes para ver el progreso.")

#     st.divider()
#     st.subheader("👤 Rendimiento por Vendedor")
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.name as Vendedor, 
#                COALESCE(SUM(v.total_points), 0) as Pts, 
#                COALESCE(t.target_points, 0) as Meta,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(t.target_postpago, 0) as m_post,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as v_fibra,
#                COALESCE(t.target_fibra, 0) as m_fibra,
#                COALESCE(SUM(v.has_insurance), 0) as v_seguro,
#                COALESCE(t.target_seguro, 0) as m_seguro,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_reno,
#                COALESCE(t.target_renovacion, 0) as m_reno,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_wom,
#                COALESCE(t.target_womgo, 0) as m_wom
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND v.status = 'Aprobada' AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1 GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             meta_pts = row['Meta'] if row['Meta'] > 0 else 1
#             prog_val = row['Pts'] / meta_pts
#             prog = min(prog_val, 1.0)
            
#             col_head1, col_head2 = st.columns([1, 1])
#             col_head1.write(f"**{row['Vendedor']}**")
#             col_head2.markdown(f"<p style='text-align:right; color:#2563eb;'><b>{prog_val*100:.1f}% de la meta</b></p>", unsafe_allow_html=True)
            
#             col_ind1, col_ind2 = st.columns([1, 1])
#             with col_ind1:
#                 st.write(f"Puntos: {int(row['Pts'])} / {int(row['Meta'])}")
#                 st.progress(prog)
#             with col_ind2:
#                 st.caption(f"Postpagos: {int(row['v_post'])}/{int(row['m_post'])} | Fibra: {int(row['v_fibra'])}/{int(row['m_fibra'])}")
#                 st.caption(f"Seguros: {int(row['v_seguro'])}/{int(row['m_seguro'])} | Reno: {int(row['v_reno'])}/{int(row['m_reno'])}")
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial")
#     filter_date = st.date_input("Filtrar por Fecha", datetime.now())
#     conn = get_connection()
#     df_hist = pd.read_sql_query(f'''
#         SELECT v.id, v.date, s.name as Vendedor, v.customer_name as Cliente, v.phone_number, v.total_points as Pts, v.status, v.category_summary as Resumen
#         FROM sales v JOIN sellers s ON v.seller_id = s.id WHERE v.date = '{filter_date}'
#     ''', conn)
    
#     if df_hist.empty:
#         st.info("Sin ventas registradas en esta fecha.")
#     else:
#         for _, row in df_hist.iterrows():
#             with st.container(border=True):
#                 c_h1, c_h2, c_h3, c_h4 = st.columns([2, 2, 1, 1])
#                 c_h1.write(f"**Cliente:** {row['Cliente']}")
#                 c_h2.write(f"**Vendedor:** {row['Vendedor']}")
#                 c_h3.write(f"**Puntos:** {row['Pts']}")
#                 if c_h4.button("✏️ Editar", key=f"edit_btn_{row['id']}"):
#                     st.session_state.editing_sale = row['id']
#                     st.session_state.menu_option = "Registrar Venta"
#                     st.rerun()
#                 st.caption(f"Servicios: {row['Resumen']}")
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2, t3 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales", "💎 Reglas de Puntos"])
    
#     with t1:
#         sellers_all = get_sellers(only_active=False)
#         for _, s in sellers_all.iterrows():
#             c_s1, c_s2 = st.columns([4, 1])
#             c_s1.write(f"{s['name']} ({'Activo' if s['active'] else 'Inactivo'})")
#             if c_s2.button("🗑️", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller_fixed"):
#             new_n = st.text_input("Nombre Vendedor")
#             if st.form_submit_button("Agregar") and new_n:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_n,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="cfg_m")
#         y_t = st.number_input("Año", value=2025, key="cfg_y")
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         st.subheader("🏬 Meta Global de Tienda")
#         with st.form("global_targets"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3, c4 = st.columns(4)
#             g_pts = c1.number_input("Puntos", value=v[4])
#             g_post = c2.number_input("Postpago", value=v[5])
#             g_fib = c3.number_input("Fibra", value=v[7])
#             g_pct = c4.number_input("% Porta", value=float(v[6]))
            
#             c5, c6, c7 = st.columns(3)
#             g_seg = c5.number_input("Seguros", value=v[8])
#             g_ren = c6.number_input("Renovaciones", value=v[9])
#             g_wom = c7.number_input("Wom Go", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                     target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                     target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
#                 conn.commit(); st.success("Meta Global guardada")

#         st.divider()
#         st.subheader("👤 Metas Individuales")
#         act_s = get_sellers()
#         if not act_s.empty:
#             if st.button("🪄 Distribuir Global entre Activos"):
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n, g_seg//n, g_ren//n, g_wom//n))
#                 conn.commit(); st.success("Metas distribuidas"); st.rerun()

#             selected_name = st.selectbox("Editar manual para:", act_s['name'].tolist())
#             s_id = act_s[act_s['name'] == selected_name]['id'].values[0]
#             cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#             s_meta = cur.fetchone()
            
#             with st.form("ind_target_form"):
#                 sv = s_meta if s_meta else [0]*11
#                 sc1, sc2, sc3, sc4 = st.columns(4)
#                 si_pts = sc1.number_input("Puntos", value=sv[4])
#                 si_post = sc2.number_input("Postpago", value=sv[5])
#                 si_fib = sc3.number_input("Fibra", value=sv[7])
#                 si_pct = sc4.number_input("% Porta", value=float(sv[6]))
                
#                 sc5, sc6, sc7 = st.columns(3)
#                 si_seg = sc5.number_input("Seguro", value=sv[8])
#                 si_ren = sc6.number_input("Renovación", value=sv[9])
#                 si_wom = sc7.number_input("Wom Go", value=sv[10])
                
#                 if st.form_submit_button("Guardar Meta Vendedor"):
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET 
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s_id, m_t, y_t, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
#                     conn.commit(); st.success("Meta Individual actualizada")
#         conn.close()

#     with t3:
#         st.subheader("Valor de Puntos por Producto")
#         conn = get_connection()
#         df_rules = pd.read_sql_query("SELECT * FROM point_rules", conn)
        
#         with st.form("edit_rules_form"):
#             for idx, row in df_rules.iterrows():
#                 col_r1, col_r2 = st.columns([3, 1])
#                 col_r1.write(f"**{row['item_name']}** ({row['type']})")
#                 new_val = col_r2.number_input("Valor", value=float(row['value']), key=f"rule_{row['id']}")
#                 df_rules.at[idx, 'value'] = new_val
            
#             if st.form_submit_button("Actualizar Reglas de Puntos"):
#                 cur = conn.cursor()
#                 for _, r in df_rules.iterrows():
#                     cur.execute("UPDATE point_rules SET value = ? WHERE id = ?", (r['value'], r['id']))
#                 conn.commit()
#                 st.success("Reglas actualizadas correctamente")
#         conn.close()



# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime
# import time

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# # --- ESTILO CSS PERSONALIZADO ---
# st.markdown("""
#     <style>
#     div.stButton > button {
#         width: 100%;
#         border-radius: 5px;
#         height: 3em;
#         background-color: #f0f2f6;
#         border: 1px solid #d1d5db;
#     }
#     div.stButton > button:hover {
#         background-color: #e5e7eb;
#         border: 1px solid #9ca3af;
#     }
#     .active-nav {
#         background-color: #2563eb !important;
#         color: white !important;
#         border: none !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # --- INICIALIZACIÓN DE ESTADO ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"
# if 'editing_sale' not in st.session_state:
#     st.session_state.editing_sale = None

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
#         CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, store_id INTEGER, active INTEGER DEFAULT 1);
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, month INTEGER, year INTEGER,
#             target_points INTEGER DEFAULT 0, target_postpago INTEGER DEFAULT 0, target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0, target_seguro INTEGER DEFAULT 0, target_renovacion INTEGER DEFAULT 0, target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year)
#         );
#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, seller_id INTEGER,
#             customer_name TEXT, customer_rut TEXT, phone_number TEXT, iccid TEXT,
#             total_amount REAL, total_points INTEGER, total_commission REAL DEFAULT 0,
#             category_summary TEXT, device_name TEXT, imei TEXT, has_insurance INTEGER DEFAULT 0,
#             fiber_plan TEXT, fiber_address TEXT, doc_type TEXT, doc_number TEXT, payment_method TEXT, status TEXT DEFAULT 'Aprobada'
#         );
#         CREATE TABLE IF NOT EXISTS point_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, value REAL, type TEXT);
#     ''')
#     cursor.execute("SELECT COUNT(*) FROM point_rules")
#     if cursor.fetchone()[0] == 0:
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'), ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'), ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'), ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'), ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'), ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'), ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'), ('Fibra', 10, 'points'), ('Seguro', 1500, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
#     conn.commit()
#     conn.close()

# init_db()

# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- NAVEGACIÓN LATERAL POR BOTONES ---
# st.sidebar.title("🛠️ Sales Manager")
# st.sidebar.markdown("---")

# nav_options = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# for opt in nav_options:
#     is_active = st.session_state.menu_option == opt
#     if st.sidebar.button(opt, key=f"nav_{opt}", help=f"Ir a {opt}", use_container_width=True, type="primary" if is_active else "secondary"):
#         st.session_state.menu_option = opt
#         st.session_state.editing_sale = None
#         st.rerun()

# choice = st.session_state.menu_option

# # --- SECCIONES ---
# if choice == "Registrar Venta":
#     is_edit = st.session_state.editing_sale is not None
#     st.header("📝 Editar Venta" if is_edit else "📝 Nueva Venta")
    
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     # Cargar datos si es edición
#     sale_data = {}
#     if is_edit:
#         conn = get_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM sales WHERE id = ?", (st.session_state.editing_sale,))
#         cols = [column[0] for column in cur.description]
#         row = cur.fetchone()
#         sale_data = dict(zip(cols, row))
#         conn.close()

#     if sellers_df.empty:
#         st.warning("⚠️ No hay vendedores activos. Por favor, agregue uno en Configuración.")
#     else:
#         with st.form("main_form", clear_on_submit=False):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", 
#                                         options=sellers_df['id'].tolist(), 
#                                         index=sellers_df['id'].tolist().index(sale_data['seller_id']) if is_edit else 0,
#                                         format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente", value=sale_data.get('customer_name', ""))
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente", value=sale_data.get('customer_rut', ""))
#             with col_g4:
#                 default_date = datetime.strptime(sale_data['date'], "%Y-%m-%d") if is_edit else datetime.now()
#                 sale_date = st.date_input("Fecha", default_date)
            
#             st.divider()
#             st.subheader("📱 Telefonía y Líneas")
#             summary_list = sale_data.get('category_summary', "").split(", ")
            
#             col_l1, col_l2, col_l3, col_l4 = st.columns(4)
#             with col_l1:
#                 porta_opts = ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"]
#                 def_porta = next((i for i in porta_opts if i in summary_list), "No aplica")
#                 tipo_porta = st.selectbox("Portabilidad", porta_opts, index=porta_opts.index(def_porta))
#             with col_l2:
#                 post_opts = ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"]
#                 def_post = next((i for i in post_opts if i in summary_list), "No aplica")
#                 tipo_post = st.selectbox("Postpago", post_opts, index=post_opts.index(def_post))
#             with col_l3:
#                 num_tel = st.text_input("Número de Teléfono", value=sale_data.get('phone_number', ""))
#             with col_l4:
#                 iccid_val = st.text_input("ICCID / Serie SIM", value=sale_data.get('iccid', ""))
            
#             extra_opts = ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"]
#             def_extra = next((i for i in extra_opts if i in summary_list), "No aplica")
#             tipo_extra = st.selectbox("Otros Planes / Servicios", extra_opts, index=extra_opts.index(def_extra))

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2, col_b3 = st.columns(3)
#             with col_b1:
#                 equipo_opts = ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"]
#                 def_eq = next((i for i in equipo_opts if i in summary_list), "No aplica")
#                 tipo_equipo = st.selectbox("Tipo Venta Equipo", equipo_opts, index=equipo_opts.index(def_eq))
#             with col_b2:
#                 device_name = st.text_input("Modelo del Equipo", value=sale_data.get('device_name', ""))
#             with col_b3:
#                 imei_val = st.text_input("IMEI", value=sale_data.get('imei', ""))
            
#             ins_check = st.checkbox("¿Incluye Seguro?", value=bool(sale_data.get('has_insurance', 0)))

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             col_fib1, col_fib2, col_fib3 = st.columns([1,2,2])
#             with col_fib1:
#                 fibra_opts = ["No aplica", "Fibra"]
#                 def_fib = "Fibra" if "Fibra" in summary_list else "No aplica"
#                 fibra_check = st.selectbox("Venta Fibra", fibra_opts, index=fibra_opts.index(def_fib))
#             with col_fib2:
#                 fib_plan = st.text_input("Plan Fibra", value=sale_data.get('fiber_plan', ""))
#             with col_fib3:
#                 fib_addr = st.text_input("Dirección Instalación", value=sale_data.get('fiber_address', ""))

#             st.divider()
#             st.subheader("💳 Pago y Estado")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_opts = ["Boleta", "Factura", "Guía"]
#                 doc_type = st.selectbox("Documento", doc_opts, index=doc_opts.index(sale_data.get('doc_type', "Boleta")))
#             with col_p2:
#                 doc_number = st.text_input("N° Documento", value=sale_data.get('doc_number', ""))
#             with col_p3:
#                 pay_opts = ["Efectivo", "Débito", "Crédito"]
#                 payment_method = st.selectbox("Método de Pago", pay_opts, index=pay_opts.index(sale_data.get('payment_method', "Efectivo")))
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0, value=float(sale_data.get('total_amount', 0.0)))
            
#             # Campo de Estatus solo visible o editable en Edición (o nuevo registro con default)
#             status_opts = ["Aprobada", "Rechazada"]
#             current_status = sale_data.get('status', "Aprobada")
#             sale_status = st.selectbox("Estado de la Venta", status_opts, index=status_opts.index(current_status))
            
#             btn_label = "💾 ACTUALIZAR VENTA" if is_edit else "💾 GUARDAR VENTA"
#             submit = st.form_submit_button(btn_label)
            
#             if is_edit:
#                 if st.form_submit_button("❌ CANCELAR EDICIÓN"):
#                     st.session_state.editing_sale = None
#                     st.session_state.menu_option = "Historial"
#                     st.rerun()
            
#             if submit:
#                 if not customer or not doc_number:
#                     st.error("Nombre de Cliente y Número de Documento son obligatorios.")
#                 else:
#                     items_sel = [i for i in [tipo_porta, tipo_post, tipo_extra, tipo_equipo, fibra_check] if i != "No aplica"]
#                     puntos = sum(rules.get(item, 0) for item in items_sel)
#                     comis = rules.get("Seguro", 1500) if ins_check else 0
#                     summary = ", ".join(items_sel)

#                     with st.status("Procesando...", expanded=True) as status:
#                         time.sleep(0.5)
#                         conn = get_connection(); cur = conn.cursor()
#                         if is_edit:
#                             cur.execute('''
#                                 UPDATE sales SET 
#                                     date=?, seller_id=?, customer_name=?, customer_rut=?, phone_number=?, iccid=?,
#                                     total_amount=?, total_points=?, total_commission=?, category_summary=?,
#                                     device_name=?, imei=?, has_insurance=?, fiber_plan=?, fiber_address=?,
#                                     doc_type=?, doc_number=?, payment_method=?, status=?
#                                 WHERE id = ?
#                             ''', (
#                                 sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                                 amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                                 fib_plan, fib_addr, doc_type, doc_number, payment_method, sale_status, st.session_state.editing_sale
#                             ))
#                         else:
#                             cur.execute('''
#                                 INSERT INTO sales (
#                                     date, seller_id, customer_name, customer_rut, phone_number, iccid,
#                                     total_amount, total_points, total_commission, category_summary,
#                                     device_name, imei, has_insurance, fiber_plan, fiber_address,
#                                     doc_type, doc_number, payment_method, status
#                                 ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                             ''', (
#                                 sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                                 amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                                 fib_plan, fib_addr, doc_type, doc_number, payment_method, sale_status
#                             ))
#                         conn.commit(); conn.close()
#                         time.sleep(0.5)
#                         status.update(label="¡Listo!", state="complete", expanded=False)
                    
#                     st.session_state.editing_sale = None
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Resumen de Metas")
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
#     year = col_y.selectbox("Año", [2024, 2025, 2026], index=1)

#     conn = get_connection()
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as tp, 
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as vp,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as vpt,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as vf,
#             SUM(has_insurance) as vs, 
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as vr,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as vw
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' AND status = 'Aprobada'
#     '''
#     res = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_g = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_g.empty:
#         m = meta_g.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos", f"{int(res['tp'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpago", f"{int(res['vp'] or 0)}", f"Meta: {m['target_postpago']}")
        
#         porta_real_pct = (res['vpt'] / res['vp'] * 100) if res['vp'] and res['vp'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res['vf'] or 0)}", f"Meta: {m['target_fibra']}")

#         st.write("---")
#         c5, c6, c7 = st.columns(3)
#         c5.metric("Seguros", f"{int(res['vs'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res['vr'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res['vw'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.info("Configura las metas del mes para ver el progreso.")

#     st.divider()
#     st.subheader("👤 Rendimiento por Vendedor")
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.name as Vendedor, 
#                COALESCE(SUM(v.total_points), 0) as Pts, 
#                COALESCE(t.target_points, 0) as Meta,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(t.target_postpago, 0) as m_post,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as v_fibra,
#                COALESCE(t.target_fibra, 0) as m_fibra,
#                COALESCE(SUM(v.has_insurance), 0) as v_seguro,
#                COALESCE(t.target_seguro, 0) as m_seguro,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_reno,
#                COALESCE(t.target_renovacion, 0) as m_reno,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_wom,
#                COALESCE(t.target_womgo, 0) as m_wom
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND v.status = 'Aprobada' AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1 GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             meta_pts = row['Meta'] if row['Meta'] > 0 else 1
#             prog_val = row['Pts'] / meta_pts
#             prog = min(prog_val, 1.0)
            
#             col_head1, col_head2 = st.columns([1, 1])
#             col_head1.write(f"**{row['Vendedor']}**")
#             col_head2.markdown(f"<p style='text-align:right; color:#2563eb;'><b>{prog_val*100:.1f}% de la meta</b></p>", unsafe_allow_html=True)
            
#             col_ind1, col_ind2 = st.columns([1, 1])
#             with col_ind1:
#                 st.write(f"Puntos: {int(row['Pts'])} / {int(row['Meta'])}")
#                 st.progress(prog)
#             with col_ind2:
#                 st.caption(f"Postpagos: {int(row['v_post'])}/{int(row['m_post'])} | Fibra: {int(row['v_fibra'])}/{int(row['m_fibra'])}")
#                 st.caption(f"Seguros: {int(row['v_seguro'])}/{int(row['m_seguro'])} | Reno: {int(row['v_reno'])}/{int(row['m_reno'])}")
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial")
#     filter_date = st.date_input("Filtrar por Fecha", datetime.now())
#     conn = get_connection()
#     df_hist = pd.read_sql_query(f'''
#         SELECT v.id, v.date, s.name as Vendedor, v.customer_name as Cliente, v.phone_number, v.total_points as Pts, v.status, v.category_summary as Resumen
#         FROM sales v JOIN sellers s ON v.seller_id = s.id WHERE v.date = '{filter_date}'
#     ''', conn)
    
#     if df_hist.empty:
#         st.info("Sin ventas registradas en esta fecha.")
#     else:
#         for _, row in df_hist.iterrows():
#             with st.container(border=True):
#                 c_h1, c_h2, c_h3, c_h4 = st.columns([2, 2, 1, 1])
#                 c_h1.write(f"**Cliente:** {row['Cliente']} ({row['status']})")
#                 c_h2.write(f"**Vendedor:** {row['Vendedor']}")
#                 c_h3.write(f"**Puntos:** {row['Pts']}")
#                 if c_h4.button("✏️ Editar", key=f"edit_btn_{row['id']}"):
#                     st.session_state.editing_sale = row['id']
#                     st.session_state.menu_option = "Registrar Venta"
#                     st.rerun()
#                 st.caption(f"Servicios: {row['Resumen']}")
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2, t3 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales", "💎 Reglas de Puntos"])
    
#     with t1:
#         sellers_all = get_sellers(only_active=False)
#         for _, s in sellers_all.iterrows():
#             c_s1, c_s2 = st.columns([4, 1])
#             c_s1.write(f"{s['name']} ({'Activo' if s['active'] else 'Inactivo'})")
#             if c_s2.button("🗑️", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller_fixed"):
#             new_n = st.text_input("Nombre Vendedor")
#             if st.form_submit_button("Agregar") and new_n:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_n,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         m_t = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1, key="cfg_m")
#         y_t = st.number_input("Año", value=2025, key="cfg_y")
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         st.subheader("🏬 Meta Global de Tienda")
#         with st.form("global_targets"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3, c4 = st.columns(4)
#             g_pts = c1.number_input("Puntos", value=v[4])
#             g_post = c2.number_input("Postpago", value=v[5])
#             g_fib = c3.number_input("Fibra", value=v[7])
#             g_pct = c4.number_input("% Porta", value=float(v[6]))
            
#             c5, c6, c7 = st.columns(3)
#             g_seg = c5.number_input("Seguros", value=v[8])
#             g_ren = c6.number_input("Renovaciones", value=v[9])
#             g_wom = c7.number_input("Wom Go", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                     target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                     target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
#                 conn.commit(); st.success("Meta Global guardada")

#         st.divider()
#         st.subheader("👤 Metas Individuales")
#         act_s = get_sellers()
#         if not act_s.empty:
#             if st.button("🪄 Distribuir Global entre Activos"):
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n, g_seg//n, g_ren//n, g_wom//n))
#                 conn.commit(); st.success("Metas distribuidas"); st.rerun()

#             selected_name = st.selectbox("Editar manual para:", act_s['name'].tolist())
#             s_id = act_s[act_s['name'] == selected_name]['id'].values[0]
#             cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#             s_meta = cur.fetchone()
            
#             with st.form("ind_target_form"):
#                 sv = s_meta if s_meta else [0]*11
#                 sc1, sc2, sc3, sc4 = st.columns(4)
#                 si_pts = sc1.number_input("Puntos", value=sv[4])
#                 si_post = sc2.number_input("Postpago", value=sv[5])
#                 si_fib = sc3.number_input("Fibra", value=sv[7])
#                 si_pct = sc4.number_input("% Porta", value=float(sv[6]))
                
#                 sc5, sc6, sc7 = st.columns(3)
#                 si_seg = sc5.number_input("Seguro", value=sv[8])
#                 si_ren = sc6.number_input("Renovación", value=sv[9])
#                 si_wom = sc7.number_input("Wom Go", value=sv[10])
                
#                 if st.form_submit_button("Guardar Meta Vendedor"):
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET 
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s_id, m_t, y_t, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
#                     conn.commit(); st.success("Meta Individual actualizada")
#         conn.close()

#     with t3:
#         st.subheader("Valor de Puntos por Producto")
#         conn = get_connection()
#         df_rules = pd.read_sql_query("SELECT * FROM point_rules", conn)
        
#         with st.form("edit_rules_form"):
#             for idx, row in df_rules.iterrows():
#                 col_r1, col_r2 = st.columns([3, 1])
#                 col_r1.write(f"**{row['item_name']}** ({row['type']})")
#                 new_val = col_r2.number_input("Valor", value=float(row['value']), key=f"rule_{row['id']}")
#                 df_rules.at[idx, 'value'] = new_val
            
#             if st.form_submit_button("Actualizar Reglas de Puntos"):
#                 cur = conn.cursor()
#                 for _, r in df_rules.iterrows():
#                     cur.execute("UPDATE point_rules SET value = ? WHERE id = ?", (r['value'], r['id']))
#                 conn.commit()
#                 st.success("Reglas actualizadas correctamente")
#         conn.close()







# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime
# import time

# # --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# # --- ESTILO CSS PERSONALIZADO ---
# st.markdown("""
#     <style>
#     div.stButton > button {
#         width: 100%;
#         border-radius: 5px;
#         height: 3em;
#         background-color: #f0f2f6;
#         border: 1px solid #d1d5db;
#     }
#     div.stButton > button:hover {
#         background-color: #e5e7eb;
#         border: 1px solid #9ca3af;
#     }
#     .active-nav {
#         background-color: #2563eb !important;
#         color: white !important;
#         border: none !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # --- INICIALIZACIÓN DE ESTADO ---
# if 'menu_option' not in st.session_state:
#     st.session_state.menu_option = "Dashboard"
# if 'editing_sale' not in st.session_state:
#     st.session_state.editing_sale = None

# # --- CONEXIÓN A BASE DE DATOS ---
# def get_connection():
#     conn = sqlite3.connect('sales_system.db')
#     return conn

# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.executescript('''
#         CREATE TABLE IF NOT EXISTS stores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
#         CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, store_id INTEGER, active INTEGER DEFAULT 1);
#         CREATE TABLE IF NOT EXISTS targets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, month INTEGER, year INTEGER,
#             target_points INTEGER DEFAULT 0, target_postpago INTEGER DEFAULT 0, target_porta_pct REAL DEFAULT 0.0,
#             target_fibra INTEGER DEFAULT 0, target_seguro INTEGER DEFAULT 0, target_renovacion INTEGER DEFAULT 0, target_womgo INTEGER DEFAULT 0,
#             UNIQUE(seller_id, month, year)
#         );
#         CREATE TABLE IF NOT EXISTS sales (
#             id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, seller_id INTEGER,
#             customer_name TEXT, customer_rut TEXT, phone_number TEXT, iccid TEXT,
#             total_amount REAL, total_points INTEGER, total_commission REAL DEFAULT 0,
#             category_summary TEXT, device_name TEXT, imei TEXT, has_insurance INTEGER DEFAULT 0,
#             fiber_plan TEXT, fiber_address TEXT, doc_type TEXT, doc_number TEXT, payment_method TEXT, status TEXT DEFAULT 'Aprobada'
#         );
#         CREATE TABLE IF NOT EXISTS point_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, value REAL, type TEXT);
#     ''')
#     cursor.execute("SELECT COUNT(*) FROM point_rules")
#     if cursor.fetchone()[0] == 0:
#         default_rules = [
#             ('Postpago: Alto Valor', 9, 'points'), ('Postpago: Business', 12, 'points'),
#             ('Postpago: Consumer', 7, 'points'), ('Postpago: Adicional', 3, 'points'),
#             ('Portabilidad: Pre-Post', 3, 'points'), ('Portabilidad: Post-Post', 5, 'points'),
#             ('Migración', 5, 'points'), ('Plan Zero', 3, 'points'),
#             ('Equipo Prepago', 3, 'points'), ('Equipo Voz', 4, 'points'),
#             ('Equipo Datos', 4, 'points'), ('Renovación', 4, 'points'),
#             ('Wom Go', 4, 'points'), ('Fibra', 10, 'points'), ('Seguro', 1500, 'commission')
#         ]
#         cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
#     conn.commit()
#     conn.close()

# init_db()

# def get_sellers(only_active=True):
#     conn = get_connection()
#     query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def get_rules_dict():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
#     conn.close()
#     return dict(zip(df['item_name'], df['value']))

# # --- NAVEGACIÓN LATERAL POR BOTONES ---
# st.sidebar.title("🛠️ Sales Manager")
# st.sidebar.markdown("---")

# nav_options = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
# for opt in nav_options:
#     is_active = st.session_state.menu_option == opt
#     if st.sidebar.button(opt, key=f"nav_{opt}", help=f"Ir a {opt}", use_container_width=True, type="primary" if is_active else "secondary"):
#         st.session_state.menu_option = opt
#         st.session_state.editing_sale = None
#         st.rerun()

# choice = st.session_state.menu_option

# # --- SECCIONES ---
# if choice == "Registrar Venta":
#     is_edit = st.session_state.editing_sale is not None
#     st.header("📝 Editar Venta" if is_edit else "📝 Nueva Venta")
    
#     sellers_df = get_sellers()
#     rules = get_rules_dict()
    
#     # Cargar datos si es edición
#     sale_data = {}
#     if is_edit:
#         conn = get_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM sales WHERE id = ?", (st.session_state.editing_sale,))
#         cols = [column[0] for column in cur.description]
#         row = cur.fetchone()
#         sale_data = dict(zip(cols, row))
#         conn.close()

#     if sellers_df.empty:
#         st.warning("⚠️ No hay vendedores activos. Por favor, agregue uno en Configuración.")
#     else:
#         with st.form("main_form", clear_on_submit=False):
#             col_g1, col_g2, col_g3, col_g4 = st.columns(4)
#             with col_g1:
#                 seller_id = st.selectbox("Vendedor", 
#                                         options=sellers_df['id'].tolist(), 
#                                         index=sellers_df['id'].tolist().index(sale_data['seller_id']) if is_edit else 0,
#                                         format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
#             with col_g2:
#                 customer = st.text_input("Nombre del Cliente", value=sale_data.get('customer_name', ""))
#             with col_g3:
#                 customer_rut = st.text_input("RUT del Cliente", value=sale_data.get('customer_rut', ""))
#             with col_g4:
#                 default_date = datetime.strptime(sale_data['date'], "%Y-%m-%d") if is_edit else datetime.now()
#                 sale_date = st.date_input("Fecha", default_date)
            
#             st.divider()
#             st.subheader("📱 Telefonía y Líneas")
#             summary_list = sale_data.get('category_summary', "").split(", ")
            
#             col_l1, col_l2, col_l3, col_l4 = st.columns(4)
#             with col_l1:
#                 porta_opts = ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"]
#                 def_porta = next((i for i in porta_opts if i in summary_list), "No aplica")
#                 tipo_porta = st.selectbox("Portabilidad", porta_opts, index=porta_opts.index(def_porta))
#             with col_l2:
#                 post_opts = ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"]
#                 def_post = next((i for i in post_opts if i in summary_list), "No aplica")
#                 tipo_post = st.selectbox("Postpago", post_opts, index=post_opts.index(def_post))
#             with col_l3:
#                 num_tel = st.text_input("Número de Teléfono", value=sale_data.get('phone_number', ""))
#             with col_l4:
#                 iccid_val = st.text_input("ICCID / Serie SIM", value=sale_data.get('iccid', ""))
            
#             extra_opts = ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"]
#             def_extra = next((i for i in extra_opts if i in summary_list), "No aplica")
#             tipo_extra = st.selectbox("Otros Planes / Servicios", extra_opts, index=extra_opts.index(def_extra))

#             st.divider()
#             st.subheader("🛡️ Equipos y Seguros")
#             col_b1, col_b2, col_b3 = st.columns(3)
#             with col_b1:
#                 equipo_opts = ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"]
#                 def_eq = next((i for i in equipo_opts if i in summary_list), "No aplica")
#                 tipo_equipo = st.selectbox("Tipo Venta Equipo", equipo_opts, index=equipo_opts.index(def_eq))
#             with col_b2:
#                 device_name = st.text_input("Modelo del Equipo", value=sale_data.get('device_name', ""))
#             with col_b3:
#                 imei_val = st.text_input("IMEI", value=sale_data.get('imei', ""))
            
#             ins_check = st.checkbox("¿Incluye Seguro?", value=bool(sale_data.get('has_insurance', 0)))

#             st.divider()
#             st.subheader("🌐 Fibra Óptica")
#             col_fib1, col_fib2, col_fib3 = st.columns([1,2,2])
#             with col_fib1:
#                 fibra_opts = ["No aplica", "Fibra"]
#                 def_fib = "Fibra" if "Fibra" in summary_list else "No aplica"
#                 fibra_check = st.selectbox("Venta Fibra", fibra_opts, index=fibra_opts.index(def_fib))
#             with col_fib2:
#                 fib_plan = st.text_input("Plan Fibra", value=sale_data.get('fiber_plan', ""))
#             with col_fib3:
#                 fib_addr = st.text_input("Dirección Instalación", value=sale_data.get('fiber_address', ""))

#             st.divider()
#             st.subheader("💳 Pago y Estado")
#             col_p1, col_p2, col_p3, col_p4 = st.columns(4)
#             with col_p1:
#                 doc_opts = ["Boleta", "Factura", "Guía"]
#                 doc_type = st.selectbox("Documento", doc_opts, index=doc_opts.index(sale_data.get('doc_type', "Boleta")))
#             with col_p2:
#                 doc_number = st.text_input("N° Documento", value=sale_data.get('doc_number', ""))
#             with col_p3:
#                 pay_opts = ["Efectivo", "Débito", "Crédito"]
#                 payment_method = st.selectbox("Método de Pago", pay_opts, index=pay_opts.index(sale_data.get('payment_method', "Efectivo")))
#             with col_p4:
#                 amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0, value=float(sale_data.get('total_amount', 0.0)))
            
#             status_opts = ["Aprobada", "Rechazada"]
#             current_status = sale_data.get('status', "Aprobada")
#             sale_status = st.selectbox("Estado de la Venta", status_opts, index=status_opts.index(current_status))
            
#             btn_label = "💾 ACTUALIZAR VENTA" if is_edit else "💾 GUARDAR VENTA"
#             submit = st.form_submit_button(btn_label)
            
#             if is_edit:
#                 if st.form_submit_button("❌ CANCELAR EDICIÓN"):
#                     st.session_state.editing_sale = None
#                     st.session_state.menu_option = "Historial"
#                     st.rerun()
            
#             if submit:
#                 if not customer or not doc_number:
#                     st.error("Nombre de Cliente y Número de Documento son obligatorios.")
#                 else:
#                     items_sel = [i for i in [tipo_porta, tipo_post, tipo_extra, tipo_equipo, fibra_check] if i != "No aplica"]
#                     puntos = sum(rules.get(item, 0) for item in items_sel)
#                     comis = rules.get("Seguro", 1500) if ins_check else 0
#                     summary = ", ".join(items_sel)

#                     with st.status("Procesando...", expanded=True) as status:
#                         time.sleep(0.5)
#                         conn = get_connection(); cur = conn.cursor()
#                         if is_edit:
#                             cur.execute('''
#                                 UPDATE sales SET 
#                                     date=?, seller_id=?, customer_name=?, customer_rut=?, phone_number=?, iccid=?,
#                                     total_amount=?, total_points=?, total_commission=?, category_summary=?,
#                                     device_name=?, imei=?, has_insurance=?, fiber_plan=?, fiber_address=?,
#                                     doc_type=?, doc_number=?, payment_method=?, status=?
#                                 WHERE id = ?
#                             ''', (
#                                 sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                                 amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                                 fib_plan, fib_addr, doc_type, doc_number, payment_method, sale_status, st.session_state.editing_sale
#                             ))
#                         else:
#                             cur.execute('''
#                                 INSERT INTO sales (
#                                     date, seller_id, customer_name, customer_rut, phone_number, iccid,
#                                     total_amount, total_points, total_commission, category_summary,
#                                     device_name, imei, has_insurance, fiber_plan, fiber_address,
#                                     doc_type, doc_number, payment_method, status
#                                 ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#                             ''', (
#                                 sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
#                                 amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
#                                 fib_plan, fib_addr, doc_type, doc_number, payment_method, sale_status
#                             ))
#                         conn.commit(); conn.close()
#                         time.sleep(0.5)
#                         status.update(label="¡Listo!", state="complete", expanded=False)
                    
#                     st.session_state.editing_sale = None
#                     st.session_state.menu_option = "Dashboard"
#                     st.rerun()

# elif choice == "Dashboard":
#     st.header("📊 Resumen de Metas")
#     now = datetime.now()
#     col_m, col_y = st.columns(2)
#     month = col_m.selectbox("Mes", range(1, 13), index=now.month - 1)
    
#     # Rango de años dinámico (año actual -1 hasta año actual +2)
#     year_range = [now.year - 1, now.year, now.year + 1, now.year + 2]
#     year = col_y.selectbox("Año", year_range, index=year_range.index(now.year))

#     conn = get_connection()
#     query_total = f'''
#         SELECT 
#             SUM(total_points) as tp, 
#             SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as vp,
#             SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as vpt,
#             SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as vf,
#             SUM(has_insurance) as vs, 
#             SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as vr,
#             SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as vw
#         FROM sales 
#         WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' AND status = 'Aprobada'
#     '''
#     res = pd.read_sql_query(query_total, conn).iloc[0]
#     meta_g = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
#     if not meta_g.empty:
#         m = meta_g.iloc[0]
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("Puntos", f"{int(res['tp'] or 0)}", f"Meta: {m['target_points']}")
#         c2.metric("Postpago", f"{int(res['vp'] or 0)}", f"Meta: {m['target_postpago']}")
        
#         porta_real_pct = (res['vpt'] / res['vp'] * 100) if res['vp'] and res['vp'] > 0 else 0
#         c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
#         c4.metric("Fibra", f"{int(res['vf'] or 0)}", f"Meta: {m['target_fibra']}")

#         st.write("---")
#         c5, c6, c7 = st.columns(3)
#         c5.metric("Seguros", f"{int(res['vs'] or 0)}", f"Meta: {m['target_seguro']}")
#         c6.metric("Renovaciones", f"{int(res['vr'] or 0)}", f"Meta: {m['target_renovacion']}")
#         c7.metric("Wom Go", f"{int(res['vw'] or 0)}", f"Meta: {m['target_womgo']}")
#     else:
#         st.info(f"Configura las metas de {month}/{year} en la sección de Configuración para ver el progreso.")

#     st.divider()
#     st.subheader("👤 Rendimiento por Vendedor")
#     df_ind = pd.read_sql_query(f'''
#         SELECT s.name as Vendedor, 
#                COALESCE(SUM(v.total_points), 0) as Pts, 
#                COALESCE(t.target_points, 0) as Meta,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
#                COALESCE(t.target_postpago, 0) as m_post,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as v_fibra,
#                COALESCE(t.target_fibra, 0) as m_fibra,
#                COALESCE(SUM(v.has_insurance), 0) as v_seguro,
#                COALESCE(t.target_seguro, 0) as m_seguro,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_reno,
#                COALESCE(t.target_renovacion, 0) as m_reno,
#                COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_wom,
#                COALESCE(t.target_womgo, 0) as m_wom
#         FROM sellers s
#         LEFT JOIN sales v ON s.id = v.seller_id AND v.status = 'Aprobada' AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
#         LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
#         WHERE s.active = 1 GROUP BY s.id
#     ''', conn)
    
#     for _, row in df_ind.iterrows():
#         with st.container(border=True):
#             meta_pts = row['Meta'] if row['Meta'] > 0 else 1
#             prog_val = row['Pts'] / meta_pts
#             prog = min(prog_val, 1.0)
            
#             col_head1, col_head2 = st.columns([1, 1])
#             col_head1.write(f"**{row['Vendedor']}**")
#             col_head2.markdown(f"<p style='text-align:right; color:#2563eb;'><b>{prog_val*100:.1f}% de la meta</b></p>", unsafe_allow_html=True)
            
#             col_ind1, col_ind2 = st.columns([1, 1])
#             with col_ind1:
#                 st.write(f"Puntos: {int(row['Pts'])} / {int(row['Meta'])}")
#                 st.progress(prog)
#             with col_ind2:
#                 st.caption(f"Postpagos: {int(row['v_post'])}/{int(row['m_post'])} | Fibra: {int(row['v_fibra'])}/{int(row['m_fibra'])}")
#                 st.caption(f"Seguros: {int(row['v_seguro'])}/{int(row['m_seguro'])} | Reno: {int(row['v_reno'])}/{int(row['m_reno'])}")
#     conn.close()

# elif choice == "Historial":
#     st.header("📋 Historial")
#     filter_date = st.date_input("Filtrar por Fecha", datetime.now())
#     conn = get_connection()
#     df_hist = pd.read_sql_query(f'''
#         SELECT v.id, v.date, s.name as Vendedor, v.customer_name as Cliente, v.phone_number, v.total_points as Pts, v.status, v.category_summary as Resumen
#         FROM sales v JOIN sellers s ON v.seller_id = s.id WHERE v.date = '{filter_date}'
#     ''', conn)
    
#     if df_hist.empty:
#         st.info("Sin ventas registradas en esta fecha.")
#     else:
#         for _, row in df_hist.iterrows():
#             with st.container(border=True):
#                 c_h1, c_h2, c_h3, c_h4 = st.columns([2, 2, 1, 1])
#                 c_h1.write(f"**Cliente:** {row['Cliente']} ({row['status']})")
#                 c_h2.write(f"**Vendedor:** {row['Vendedor']}")
#                 c_h3.write(f"**Puntos:** {row['Pts']}")
#                 if c_h4.button("✏️ Editar", key=f"edit_btn_{row['id']}"):
#                     st.session_state.editing_sale = row['id']
#                     st.session_state.menu_option = "Registrar Venta"
#                     st.rerun()
#                 st.caption(f"Servicios: {row['Resumen']}")
#     conn.close()

# elif choice == "Configuración":
#     st.header("⚙️ Configuración")
#     t1, t2, t3 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales", "💎 Reglas de Puntos"])
    
#     with t1:
#         sellers_all = get_sellers(only_active=False)
#         for _, s in sellers_all.iterrows():
#             c_s1, c_s2 = st.columns([4, 1])
#             c_s1.write(f"{s['name']} ({'Activo' if s['active'] else 'Inactivo'})")
#             if c_s2.button("🗑️", key=f"del_{s['id']}"):
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
#                 conn.commit(); conn.close(); st.rerun()
        
#         with st.form("add_seller_fixed"):
#             new_n = st.text_input("Nombre Vendedor")
#             if st.form_submit_button("Agregar") and new_n:
#                 conn = get_connection(); cur = conn.cursor()
#                 cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_n,))
#                 conn.commit(); conn.close(); st.rerun()

#     with t2:
#         now = datetime.now()
#         m_t = st.selectbox("Mes", range(1, 13), index=now.month - 1, key="cfg_m")
#         y_t = st.number_input("Año", value=now.year, key="cfg_y")
        
#         conn = get_connection(); cur = conn.cursor()
#         cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
#         g_meta = cur.fetchone()
        
#         st.subheader("🏬 Meta Global de Tienda")
#         with st.form("global_targets"):
#             v = g_meta if g_meta else [0]*11
#             c1, c2, c3, c4 = st.columns(4)
#             g_pts = c1.number_input("Puntos", value=v[4])
#             g_post = c2.number_input("Postpago", value=v[5])
#             g_fib = c3.number_input("Fibra", value=v[7])
#             g_pct = c4.number_input("% Porta", value=float(v[6]))
            
#             c5, c6, c7 = st.columns(3)
#             g_seg = c5.number_input("Seguros", value=v[8])
#             g_ren = c6.number_input("Renovaciones", value=v[9])
#             g_wom = c7.number_input("Wom Go", value=v[10])
            
#             if st.form_submit_button("Guardar Meta Global"):
#                 cur.execute('''
#                     INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                     VALUES (0,?,?,?,?,?,?,?,?,?)
#                     ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                     target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                     target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
#                     target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                 ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
#                 conn.commit(); st.success("Meta Global guardada")

#         st.divider()
#         st.subheader("👤 Metas Individuales")
#         act_s = get_sellers()
#         if not act_s.empty:
#             if st.button("🪄 Distribuir Global entre Activos"):
#                 n = len(act_s)
#                 for _, s in act_s.iterrows():
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n, g_seg//n, g_ren//n, g_wom//n))
#                 conn.commit(); st.success("Metas distribuidas"); st.rerun()

#             selected_name = st.selectbox("Editar manual para:", act_s['name'].tolist())
#             s_id = act_s[act_s['name'] == selected_name]['id'].values[0]
#             cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
#             s_meta = cur.fetchone()
            
#             with st.form("ind_target_form"):
#                 sv = s_meta if s_meta else [0]*11
#                 sc1, sc2, sc3, sc4 = st.columns(4)
#                 si_pts = sc1.number_input("Puntos", value=sv[4])
#                 si_post = sc2.number_input("Postpago", value=sv[5])
#                 si_fib = sc3.number_input("Fibra", value=sv[7])
#                 si_pct = sc4.number_input("% Porta", value=float(sv[6]))
                
#                 sc5, sc6, sc7 = st.columns(3)
#                 si_seg = sc5.number_input("Seguro", value=sv[8])
#                 si_ren = sc6.number_input("Renovación", value=sv[9])
#                 si_wom = sc7.number_input("Wom Go", value=sv[10])
                
#                 if st.form_submit_button("Guardar Meta Vendedor"):
#                     cur.execute('''
#                         INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
#                         VALUES (?,?,?,?,?,?,?,?,?,?)
#                         ON CONFLICT(seller_id, month, year) DO UPDATE SET 
#                         target_points=excluded.target_points, target_postpago=excluded.target_postpago,
#                         target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
#                         target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
#                     ''', (s_id, m_t, y_t, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
#                     conn.commit(); st.success("Meta Individual actualizada")
#         conn.close()

#     with t3:
#         st.subheader("Valor de Puntos por Producto")
#         conn = get_connection()
#         df_rules = pd.read_sql_query("SELECT * FROM point_rules", conn)
        
#         with st.form("edit_rules_form"):
#             for idx, row in df_rules.iterrows():
#                 col_r1, col_r2 = st.columns([3, 1])
#                 col_r1.write(f"**{row['item_name']}** ({row['type']})")
#                 new_val = col_r2.number_input("Valor", value=float(row['value']), key=f"rule_{row['id']}")
#                 df_rules.at[idx, 'value'] = new_val
            
#             if st.form_submit_button("Actualizar Reglas de Puntos"):
#                 cur = conn.cursor()
#                 for _, r in df_rules.iterrows():
#                     cur.execute("UPDATE point_rules SET value = ? WHERE id = ?", (r['value'], r['id']))
#                 conn.commit()
#                 st.success("Reglas actualizadas correctamente")
#         conn.close()



















import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# --- ESTILO CSS PERSONALIZADO ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
    }
    div.stButton > button:hover {
        background-color: #e5e7eb;
        border: 1px solid #9ca3af;
    }
    .active-nav {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if 'menu_option' not in st.session_state:
    st.session_state.menu_option = "Dashboard"
if 'editing_sale' not in st.session_state:
    st.session_state.editing_sale = None

# --- CONEXIÓN A BASE DE DATOS ---
def get_connection():
    conn = sqlite3.connect('sales_system.db')
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS stores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, store_id INTEGER, active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, month INTEGER, year INTEGER,
            target_points INTEGER DEFAULT 0, target_postpago INTEGER DEFAULT 0, target_porta_pct REAL DEFAULT 0.0,
            target_fibra INTEGER DEFAULT 0, target_seguro INTEGER DEFAULT 0, target_renovacion INTEGER DEFAULT 0, target_womgo INTEGER DEFAULT 0,
            UNIQUE(seller_id, month, year)
        );
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, seller_id INTEGER,
            customer_name TEXT, customer_rut TEXT, phone_number TEXT, iccid TEXT,
            total_amount REAL, total_points INTEGER, total_commission REAL DEFAULT 0,
            category_summary TEXT, device_name TEXT, imei TEXT, has_insurance INTEGER DEFAULT 0,
            fiber_plan TEXT, fiber_address TEXT, doc_type TEXT, doc_number TEXT, payment_method TEXT, status TEXT DEFAULT 'Aprobada'
        );
        CREATE TABLE IF NOT EXISTS point_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, value REAL, type TEXT);
    ''')
    cursor.execute("SELECT COUNT(*) FROM point_rules")
    if cursor.fetchone()[0] == 0:
        default_rules = [
            ('Postpago: Alto Valor', 9, 'points'), ('Postpago: Business', 12, 'points'),
            ('Postpago: Consumer', 7, 'points'), ('Postpago: Adicional', 3, 'points'),
            ('Portabilidad: Pre-Post', 3, 'points'), ('Portabilidad: Post-Post', 5, 'points'),
            ('Migración', 5, 'points'), ('Plan Zero', 3, 'points'),
            ('Equipo Prepago', 3, 'points'), ('Equipo Voz', 4, 'points'),
            ('Equipo Datos', 4, 'points'), ('Renovación', 4, 'points'),
            ('Wom Go', 4, 'points'), ('Fibra', 10, 'points'), ('Seguro', 1500, 'commission')
        ]
        cursor.executemany("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", default_rules)
    conn.commit()
    conn.close()

init_db()

def get_sellers(only_active=True):
    conn = get_connection()
    query = "SELECT id, name FROM sellers WHERE active = 1" if only_active else "SELECT id, name, active FROM sellers"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_rules_dict():
    conn = get_connection()
    df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
    conn.close()
    return dict(zip(df['item_name'], df['value']))

# --- NAVEGACIÓN LATERAL POR BOTONES ---
st.sidebar.title("🛠️ Sales Manager")
st.sidebar.markdown("---")

nav_options = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
for opt in nav_options:
    is_active = st.session_state.menu_option == opt
    if st.sidebar.button(opt, key=f"nav_{opt}", help=f"Ir a {opt}", use_container_width=True, type="primary" if is_active else "secondary"):
        st.session_state.menu_option = opt
        st.session_state.editing_sale = None
        st.rerun()

choice = st.session_state.menu_option

# --- SECCIONES ---
if choice == "Registrar Venta":
    is_edit = st.session_state.editing_sale is not None
    st.header("📝 Editar Venta" if is_edit else "📝 Nueva Venta")
    
    sellers_df = get_sellers()
    rules = get_rules_dict()
    
    # Cargar datos si es edición
    sale_data = {}
    if is_edit:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM sales WHERE id = ?", (st.session_state.editing_sale,))
        cols = [column[0] for column in cur.description]
        row = cur.fetchone()
        sale_data = dict(zip(cols, row))
        conn.close()

    if sellers_df.empty:
        st.warning("⚠️ No hay vendedores activos. Por favor, agregue uno en Configuración.")
    else:
        with st.form("main_form", clear_on_submit=False):
            col_g1, col_g2, col_g3, col_g4 = st.columns(4)
            with col_g1:
                seller_id = st.selectbox("Vendedor", 
                                        options=sellers_df['id'].tolist(), 
                                        index=sellers_df['id'].tolist().index(sale_data['seller_id']) if is_edit else 0,
                                        format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0])
            with col_g2:
                customer = st.text_input("Nombre del Cliente", value=sale_data.get('customer_name', ""))
            with col_g3:
                customer_rut = st.text_input("RUT del Cliente", value=sale_data.get('customer_rut', ""))
            with col_g4:
                default_date = datetime.strptime(sale_data['date'], "%Y-%m-%d") if is_edit else datetime.now()
                sale_date = st.date_input("Fecha", default_date)
            
            st.divider()
            st.subheader("📱 Telefonía y Líneas")
            summary_list = sale_data.get('category_summary', "").split(", ")
            
            col_l1, col_l2, col_l3, col_l4 = st.columns(4)
            with col_l1:
                porta_opts = ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"]
                def_porta = next((i for i in porta_opts if i in summary_list), "No aplica")
                tipo_porta = st.selectbox("Portabilidad", porta_opts, index=porta_opts.index(def_porta))
            with col_l2:
                post_opts = ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"]
                def_post = next((i for i in post_opts if i in summary_list), "No aplica")
                tipo_post = st.selectbox("Postpago", post_opts, index=post_opts.index(def_post))
            with col_l3:
                num_tel = st.text_input("Número de Teléfono", value=sale_data.get('phone_number', ""))
            with col_l4:
                iccid_val = st.text_input("ICCID / Serie SIM", value=sale_data.get('iccid', ""))
            
            extra_opts = ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"]
            def_extra = next((i for i in extra_opts if i in summary_list), "No aplica")
            tipo_extra = st.selectbox("Otros Planes / Servicios", extra_opts, index=extra_opts.index(def_extra))

            st.divider()
            st.subheader("🛡️ Equipos y Seguros")
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                equipo_opts = ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"]
                def_eq = next((i for i in equipo_opts if i in summary_list), "No aplica")
                tipo_equipo = st.selectbox("Tipo Venta Equipo", equipo_opts, index=equipo_opts.index(def_eq))
            with col_b2:
                device_name = st.text_input("Modelo del Equipo", value=sale_data.get('device_name', ""))
            with col_b3:
                imei_val = st.text_input("IMEI", value=sale_data.get('imei', ""))
            
            ins_check = st.checkbox("¿Incluye Seguro?", value=bool(sale_data.get('has_insurance', 0)))

            st.divider()
            st.subheader("🌐 Fibra Óptica")
            col_fib1, col_fib2, col_fib3 = st.columns([1,2,2])
            with col_fib1:
                fibra_opts = ["No aplica", "Fibra"]
                def_fib = "Fibra" if "Fibra" in summary_list else "No aplica"
                fibra_check = st.selectbox("Venta Fibra", fibra_opts, index=fibra_opts.index(def_fib))
            with col_fib2:
                fib_plan = st.text_input("Plan Fibra", value=sale_data.get('fiber_plan', ""))
            with col_fib3:
                fib_addr = st.text_input("Dirección Instalación", value=sale_data.get('fiber_address', ""))

            st.divider()
            st.subheader("💳 Pago y Estado")
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            with col_p1:
                doc_opts = ["Boleta", "Factura", "Guía"]
                doc_type = st.selectbox("Documento", doc_opts, index=doc_opts.index(sale_data.get('doc_type', "Boleta")))
            with col_p2:
                doc_number = st.text_input("N° Documento", value=sale_data.get('doc_number', ""))
            with col_p3:
                pay_opts = ["Efectivo", "Débito", "Crédito"]
                payment_method = st.selectbox("Método de Pago", pay_opts, index=pay_opts.index(sale_data.get('payment_method', "Efectivo")))
            with col_p4:
                amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0, value=float(sale_data.get('total_amount', 0.0)))
            
            status_opts = ["Aprobada", "Rechazada"]
            current_status = sale_data.get('status', "Aprobada")
            sale_status = st.selectbox("Estado de la Venta", status_opts, index=status_opts.index(current_status))
            
            btn_label = "💾 ACTUALIZAR VENTA" if is_edit else "💾 GUARDAR VENTA"
            submit = st.form_submit_button(btn_label)
            
            if is_edit:
                if st.form_submit_button("❌ CANCELAR EDICIÓN"):
                    st.session_state.editing_sale = None
                    st.session_state.menu_option = "Historial"
                    st.rerun()
            
            if submit:
                if not customer or not doc_number:
                    st.error("Nombre de Cliente y Número de Documento son obligatorios.")
                else:
                    items_sel = [i for i in [tipo_porta, tipo_post, tipo_extra, tipo_equipo, fibra_check] if i != "No aplica"]
                    puntos = sum(rules.get(item, 0) for item in items_sel)
                    comis = rules.get("Seguro", 1500) if ins_check else 0
                    summary = ", ".join(items_sel)

                    with st.status("Procesando...", expanded=True) as status:
                        time.sleep(0.5)
                        conn = get_connection(); cur = conn.cursor()
                        if is_edit:
                            cur.execute('''
                                UPDATE sales SET 
                                    date=?, seller_id=?, customer_name=?, customer_rut=?, phone_number=?, iccid=?,
                                    total_amount=?, total_points=?, total_commission=?, category_summary=?,
                                    device_name=?, imei=?, has_insurance=?, fiber_plan=?, fiber_address=?,
                                    doc_type=?, doc_number=?, payment_method=?, status=?
                                WHERE id = ?
                            ''', (
                                sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
                                amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
                                fib_plan, fib_addr, doc_type, doc_number, payment_method, sale_status, st.session_state.editing_sale
                            ))
                        else:
                            cur.execute('''
                                INSERT INTO sales (
                                    date, seller_id, customer_name, customer_rut, phone_number, iccid,
                                    total_amount, total_points, total_commission, category_summary,
                                    device_name, imei, has_insurance, fiber_plan, fiber_address,
                                    doc_type, doc_number, payment_method, status
                                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                            ''', (
                                sale_date.strftime("%Y-%m-%d"), seller_id, customer, customer_rut, num_tel, iccid_val,
                                amount, puntos, comis, summary, device_name, imei_val, (1 if ins_check else 0),
                                fib_plan, fib_addr, doc_type, doc_number, payment_method, sale_status
                            ))
                        conn.commit(); conn.close()
                        time.sleep(0.5)
                        status.update(label="¡Listo!", state="complete", expanded=False)
                    
                    st.session_state.editing_sale = None
                    st.session_state.menu_option = "Dashboard"
                    st.rerun()

elif choice == "Dashboard":
    st.header("📊 Resumen de Metas")
    now = datetime.now()
    col_m, col_y = st.columns(2)
    month = col_m.selectbox("Mes", range(1, 13), index=now.month - 1)
    
    year_range = [now.year - 1, now.year, now.year + 1, now.year + 2]
    year = col_y.selectbox("Año", year_range, index=year_range.index(now.year))

    conn = get_connection()
    query_total = f'''
        SELECT 
            SUM(total_points) as tp, 
            SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END) as vp,
            SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END) as vpt,
            SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END) as vf,
            SUM(has_insurance) as vs, 
            SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END) as vr,
            SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END) as vw
        FROM sales 
        WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' AND status = 'Aprobada'
    '''
    res = pd.read_sql_query(query_total, conn).iloc[0]
    meta_g = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
    if not meta_g.empty:
        m = meta_g.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Puntos", f"{int(res['tp'] or 0)}", f"Meta: {m['target_points']}")
        c2.metric("Postpago", f"{int(res['vp'] or 0)}", f"Meta: {m['target_postpago']}")
        
        porta_real_pct = (res['vpt'] / res['vp'] * 100) if res['vp'] and res['vp'] > 0 else 0
        c3.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
        c4.metric("Fibra", f"{int(res['vf'] or 0)}", f"Meta: {m['target_fibra']}")

        st.write("---")
        c5, c6, c7 = st.columns(3)
        c5.metric("Seguros", f"{int(res['vs'] or 0)}", f"Meta: {m['target_seguro']}")
        c6.metric("Renovaciones", f"{int(res['vr'] or 0)}", f"Meta: {m['target_renovacion']}")
        c7.metric("Wom Go", f"{int(res['vw'] or 0)}", f"Meta: {m['target_womgo']}")
    else:
        st.info(f"Configura las metas de {month}/{year} en la sección de Configuración para ver el progreso.")

    st.divider()
    st.subheader("👤 Rendimiento por Vendedor")
    df_ind = pd.read_sql_query(f'''
        SELECT s.name as Vendedor, 
               COALESCE(SUM(v.total_points), 0) as Pts, 
               COALESCE(t.target_points, 0) as Meta,
               COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as v_post,
               COALESCE(t.target_postpago, 0) as m_post,
               COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as v_fibra,
               COALESCE(t.target_fibra, 0) as m_fibra,
               COALESCE(SUM(v.has_insurance), 0) as v_seguro,
               COALESCE(t.target_seguro, 0) as m_seguro,
               COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as v_reno,
               COALESCE(t.target_renovacion, 0) as m_reno,
               COALESCE(SUM(CASE WHEN v.category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as v_wom,
               COALESCE(t.target_womgo, 0) as m_wom
        FROM sellers s
        LEFT JOIN sales v ON s.id = v.seller_id AND v.status = 'Aprobada' AND strftime('%m', v.date) = '{month:02}' AND strftime('%Y', v.date) = '{year}'
        LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
        WHERE s.active = 1 GROUP BY s.id
    ''', conn)
    
    for _, row in df_ind.iterrows():
        with st.container(border=True):
            meta_pts = row['Meta'] if row['Meta'] > 0 else 1
            prog_val = row['Pts'] / meta_pts
            prog = min(prog_val, 1.0)
            
            col_head1, col_head2 = st.columns([1, 1])
            col_head1.write(f"**{row['Vendedor']}**")
            col_head2.markdown(f"<p style='text-align:right; color:#2563eb;'><b>{prog_val*100:.1f}% de la meta</b></p>", unsafe_allow_html=True)
            
            col_ind1, col_ind2 = st.columns([1, 1])
            with col_ind1:
                st.write(f"Puntos: {int(row['Pts'])} / {int(row['Meta'])}")
                st.progress(prog)
            with col_ind2:
                st.caption(f"Postpagos: {int(row['v_post'])}/{int(row['m_post'])} | Fibra: {int(row['v_fibra'])}/{int(row['m_fibra'])}")
                st.caption(f"Seguros: {int(row['v_seguro'])}/{int(row['m_seguro'])} | Reno: {int(row['v_reno'])}/{int(row['m_reno'])}")
    conn.close()

elif choice == "Historial":
    st.header("📋 Historial")
    
    # --- FILTROS HISTORIAL ---
    col_fh1, col_fh2 = st.columns([1, 1])
    with col_fh1:
        filter_date = st.date_input("Filtrar por Fecha", datetime.now())
    with col_fh2:
        sellers_df = get_sellers(only_active=False)
        seller_list = ["Todos"] + sellers_df['name'].tolist()
        filter_seller = st.selectbox("Filtrar por Vendedor", seller_list)

    # --- CONSULTA DINÁMICA ---
    conn = get_connection()
    query_hist = f'''
        SELECT v.id, v.date, s.name as Vendedor, v.customer_name as Cliente, v.phone_number, v.total_points as Pts, v.status, v.category_summary as Resumen
        FROM sales v JOIN sellers s ON v.seller_id = s.id 
        WHERE v.date = '{filter_date}'
    '''
    if filter_seller != "Todos":
        query_hist += f" AND s.name = '{filter_seller}'"
        
    df_hist = pd.read_sql_query(query_hist, conn)
    
    if df_hist.empty:
        st.info("Sin ventas registradas con los filtros seleccionados.")
    else:
        for _, row in df_hist.iterrows():
            with st.container(border=True):
                c_h1, c_h2, c_h3, c_h4 = st.columns([2, 2, 1, 1])
                c_h1.write(f"**Cliente:** {row['Cliente']} ({row['status']})")
                c_h2.write(f"**Vendedor:** {row['Vendedor']}")
                c_h3.write(f"**Puntos:** {row['Pts']}")
                if c_h4.button("✏️ Editar", key=f"edit_btn_{row['id']}"):
                    st.session_state.editing_sale = row['id']
                    st.session_state.menu_option = "Registrar Venta"
                    st.rerun()
                st.caption(f"Servicios: {row['Resumen']}")
    conn.close()

elif choice == "Configuración":
    st.header("⚙️ Configuración")
    t1, t2, t3 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales", "💎 Reglas de Puntos"])
    
    with t1:
        sellers_all = get_sellers(only_active=False)
        for _, s in sellers_all.iterrows():
            c_s1, c_s2 = st.columns([4, 1])
            c_s1.write(f"{s['name']} ({'Activo' if s['active'] else 'Inactivo'})")
            if c_s2.button("🗑️", key=f"del_{s['id']}"):
                conn = get_connection(); cur = conn.cursor()
                cur.execute("DELETE FROM sellers WHERE id = ?", (s['id'],))
                conn.commit(); conn.close(); st.rerun()
        
        with st.form("add_seller_fixed"):
            new_n = st.text_input("Nombre Vendedor")
            if st.form_submit_button("Agregar") and new_n:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("INSERT INTO sellers (name, store_id) VALUES (?, 1)", (new_n,))
                conn.commit(); conn.close(); st.rerun()

    with t2:
        now = datetime.now()
        m_t = st.selectbox("Mes", range(1, 13), index=now.month - 1, key="cfg_m")
        y_t = st.number_input("Año", value=now.year, key="cfg_y")
        
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (m_t, y_t))
        g_meta = cur.fetchone()
        
        st.subheader("🏬 Meta Global de Tienda")
        with st.form("global_targets"):
            v = g_meta if g_meta else [0]*11
            c1, c2, c3, c4 = st.columns(4)
            g_pts = c1.number_input("Puntos", value=v[4])
            g_post = c2.number_input("Postpago", value=v[5])
            g_fib = c3.number_input("Fibra", value=v[7])
            g_pct = c4.number_input("% Porta", value=float(v[6]))
            
            c5, c6, c7 = st.columns(3)
            g_seg = c5.number_input("Seguros", value=v[8])
            g_ren = c6.number_input("Renovaciones", value=v[9])
            g_wom = c7.number_input("Wom Go", value=v[10])
            
            if st.form_submit_button("Guardar Meta Global"):
                cur.execute('''
                    INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
                    VALUES (0,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(seller_id, month, year) DO UPDATE SET
                    target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
                    target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
                    target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
                ''', (m_t, y_t, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
                conn.commit(); st.success("Meta Global guardada")

        st.divider()
        st.subheader("👤 Metas Individuales")
        act_s = get_sellers()
        if not act_s.empty:
            if st.button("🪄 Distribuir Global entre Activos"):
                n = len(act_s)
                for _, s in act_s.iterrows():
                    cur.execute('''
                        INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
                        VALUES (?,?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(seller_id, month, year) DO UPDATE SET
                        target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
                        target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
                        target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
                    ''', (s['id'], m_t, y_t, g_pts//n, g_post//n, g_pct, g_fib//n, g_seg//n, g_ren//n, g_wom//n))
                conn.commit(); st.success("Metas distribuidas"); st.rerun()

            selected_name = st.selectbox("Editar manual para:", act_s['name'].tolist())
            s_id = act_s[act_s['name'] == selected_name]['id'].values[0]
            cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (s_id, m_t, y_t))
            s_meta = cur.fetchone()
            
            with st.form("ind_target_form"):
                sv = s_meta if s_meta else [0]*11
                sc1, sc2, sc3, sc4 = st.columns(4)
                si_pts = sc1.number_input("Puntos", value=sv[4])
                si_post = sc2.number_input("Postpago", value=sv[5])
                si_fib = sc3.number_input("Fibra", value=sv[7])
                si_pct = sc4.number_input("% Porta", value=float(sv[6]))
                
                sc5, sc6, sc7 = st.columns(3)
                si_seg = sc5.number_input("Seguro", value=sv[8])
                si_ren = sc6.number_input("Renovación", value=sv[9])
                si_wom = sc7.number_input("Wom Go", value=sv[10])
                
                if st.form_submit_button("Guardar Meta Vendedor"):
                    cur.execute('''
                        INSERT INTO targets (seller_id, month, year, target_points, target_postpago, target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
                        VALUES (?,?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(seller_id, month, year) DO UPDATE SET 
                        target_points=excluded.target_points, target_postpago=excluded.target_postpago,
                        target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
                        target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
                    ''', (s_id, m_t, y_t, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
                    conn.commit(); st.success("Meta Individual actualizada")
        conn.close()

    with t3:
        st.subheader("Valor de Puntos por Producto")
        conn = get_connection()
        df_rules = pd.read_sql_query("SELECT * FROM point_rules", conn)
        
        with st.form("edit_rules_form"):
            for idx, row in df_rules.iterrows():
                col_r1, col_r2 = st.columns([3, 1])
                col_r1.write(f"**{row['item_name']}** ({row['type']})")
                new_val = col_r2.number_input("Valor", value=float(row['value']), key=f"rule_{row['id']}")
                df_rules.at[idx, 'value'] = new_val
            
            if st.form_submit_button("Actualizar Reglas de Puntos"):
                cur = conn.cursor()
                for _, r in df_rules.iterrows():
                    cur.execute("UPDATE point_rules SET value = ? WHERE id = ?", (r['value'], r['id']))
                conn.commit()
                st.success("Reglas actualizadas correctamente")
        conn.close()