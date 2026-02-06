
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, List
import time
import hashlib

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sales Manager Pro", layout="wide", page_icon="📈")

# --- DATACLASSES PARA ESTRUCTURA DE DATOS ---
@dataclass
class SaleData:
    """Estructura para datos de venta"""
    seller_id: int
    customer_name: str
    customer_rut: str
    date: str
    phone_number: str = ""
    iccid: str = ""
    total_amount: float = 0.0
    total_points: int = 0
    total_commission: float = 0.0
    category_summary: str = ""
    device_name: str = ""
    imei: str = ""
    has_insurance: int = 0
    has_accessories: int = 0
    accessory_name: str = ""
    accessory_code: str = ""
    fiber_plan: str = ""
    fiber_address: str = ""
    doc_type: str = "Boleta"
    doc_number: str = ""
    payment_method: str = "Efectivo"
    status: str = "Aprobada"

# --- CONSTANTES ---
PRODUCT_OPTIONS = {
    'porta': ["No aplica", "Portabilidad: Pre-Post", "Portabilidad: Post-Post"],
    'post': ["No aplica", "Postpago: Alto Valor", "Postpago: Business", "Postpago: Consumer", "Postpago: Adicional"],
    'extra': ["No aplica", "Migración", "Plan Zero", "Equipo Prepago"],
    'equipo': ["No aplica", "Equipo Voz", "Equipo Datos", "Renovación", "Wom Go"],
    'fibra': ["No aplica", "Fibra"],
    'doc': ["Boleta", "Factura", "Guía"],
    'payment': ["Efectivo", "Débito", "Crédito"],
    'status': ["Aprobada", "Rechazada"]
}

DEFAULT_POINT_RULES = [
    ('Postpago: Alto Valor', 9, 'points'),
    ('Postpago: Business', 12, 'points'),
    ('Postpago: Consumer', 7, 'points'),
    ('Postpago: Adicional', 3, 'points'),
    ('Portabilidad: Pre-Post', 3, 'points'),
    ('Portabilidad: Post-Post', 5, 'points'),
    ('Migración', 5, 'points'),
    ('Plan Zero', 3, 'points'),
    ('Equipo Prepago', 3, 'points'),
    ('Equipo Voz', 4, 'points'),
    ('Equipo Datos', 4, 'points'),
    ('Renovación', 4, 'points'),
    ('Wom Go', 4, 'points'),
    ('Fibra', 10, 'points'),
    ('Seguro', 1500, 'commission'),
    ('Accesorio', 1000, 'commission')
]

# --- ESTILOS CSS MEJORADOS ---
def load_custom_css():
    st.markdown("""
        <style>
        /* Botones de navegación */
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            font-weight: 500;
            transition: all 0.2s ease;
            color: #1e293b !important;
        }
        div.stButton > button:hover {
            background-color: #f1f5f9;
            border-color: #cbd5e1;
            transform: translateY(-1px);
            color: #0f172a !important;
        }
        
        /* Contenedores con bordes */
        [data-testid="stContainer"] {
            border-radius: 8px;
        }
        
        /* Métricas */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        /* Títulos de sección */
        h3 {
            color: #1e293b;
            font-weight: 600;
        }
        
        /* Divisores */
        hr {
            margin: 1.5rem 0;
            border-color: #e2e8f0;
        }
        
        /* Login form styling */
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE AUTENTICACIÓN ---
def hash_password(password: str) -> str:
    """Hashea una contraseña usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username: str, password: str) -> bool:
    """Verifica las credenciales de login"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ? AND active = 1", (username,))
    result = cur.fetchone()
    conn.close()
    
    if result:
        return result[0] == hash_password(password)
    return False

def render_login_page():
    """Renderiza la página de login"""
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Sales Manager")
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                if verify_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Inicio de sesión exitoso")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown("---")
        st.caption("Sales Manager Pro v2.0")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- DATABASE MANAGER CLASS ---
def get_db_connection():
    """Función auxiliar para obtener conexión a BD"""
    return sqlite3.connect('sales_system.db')

class DatabaseManager:
    """Gestión centralizada de base de datos"""
    
    def __init__(self, db_path: str = 'sales_system.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Inicializa las tablas y datos por defecto"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL, 
                store_id INTEGER, 
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                seller_id INTEGER, 
                month INTEGER, 
                year INTEGER,
                target_points INTEGER DEFAULT 0, 
                target_postpago INTEGER DEFAULT 0, 
                target_porta_pct REAL DEFAULT 0.0,
                target_fibra INTEGER DEFAULT 0, 
                target_seguro INTEGER DEFAULT 0, 
                target_renovacion INTEGER DEFAULT 0, 
                target_womgo INTEGER DEFAULT 0,
                UNIQUE(seller_id, month, year)
            );
            
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                date TEXT NOT NULL, 
                seller_id INTEGER,
                customer_name TEXT, 
                customer_rut TEXT, 
                phone_number TEXT, 
                iccid TEXT,
                total_amount REAL, 
                total_points INTEGER, 
                total_commission REAL DEFAULT 0,
                category_summary TEXT, 
                device_name TEXT, 
                imei TEXT, 
                has_insurance INTEGER DEFAULT 0,
                has_accessories INTEGER DEFAULT 0,
                accessory_name TEXT,
                accessory_code TEXT,
                fiber_plan TEXT, 
                fiber_address TEXT, 
                doc_type TEXT, 
                doc_number TEXT, 
                payment_method TEXT, 
                status TEXT DEFAULT 'Aprobada',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS point_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                item_name TEXT UNIQUE, 
                value REAL, 
                type TEXT
            );
        ''')
        
        # Crear usuario admin por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            admin_password = hash_password("admin123")  # Cambiar esto en producción
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                ("admin", admin_password)
            )
        
        # Migración: Agregar columna has_accessories si no existe
        cursor.execute("PRAGMA table_info(sales)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'has_accessories' not in columns:
            cursor.execute("ALTER TABLE sales ADD COLUMN has_accessories INTEGER DEFAULT 0")
        if 'accessory_name' not in columns:
            cursor.execute("ALTER TABLE sales ADD COLUMN accessory_name TEXT")
        if 'accessory_code' not in columns:
            cursor.execute("ALTER TABLE sales ADD COLUMN accessory_code TEXT")
        
        # Insertar reglas por defecto si no existen
        cursor.execute("SELECT COUNT(*) FROM point_rules")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", 
                DEFAULT_POINT_RULES
            )
        else:
            # Asegurar que la regla de Accesorio existe
            cursor.execute("INSERT OR IGNORE INTO point_rules (item_name, value, type) VALUES (?, ?, ?)", 
                          ('Accesorio', 1000, 'commission'))
        
        conn.commit()
        conn.close()
    
    def get_sellers(self, only_active: bool = True) -> pd.DataFrame:
        """Obtiene vendedores"""
        conn = self.get_connection()
        if only_active:
            query = "SELECT id, name, active FROM sellers WHERE active = 1 ORDER BY name"
        else:
            query = "SELECT id, name, active, created_at, updated_at FROM sellers ORDER BY active DESC, name"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def add_seller(self, name: str) -> bool:
        """Agrega un nuevo vendedor"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO sellers (name, store_id, created_at, updated_at) VALUES (?, 1, datetime('now'), datetime('now'))", 
                (name,)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_seller(self, seller_id: int, new_name: str) -> bool:
        """Actualiza el nombre de un vendedor"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE sellers SET name = ?, updated_at = datetime('now') WHERE id = ?", 
                (new_name, seller_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def toggle_seller_status(self, seller_id: int) -> bool:
        """Activa o desactiva un vendedor"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE sellers SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END, updated_at = datetime('now') WHERE id = ?", 
                (seller_id,)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_rules_dict(self) -> Dict[str, float]:
        """Obtiene reglas de puntos como diccionario"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT item_name, value FROM point_rules", conn)
        conn.close()
        return dict(zip(df['item_name'], df['value']))
    
    def get_sale_by_id(self, sale_id: int) -> Optional[Dict]:
        """Obtiene una venta por ID"""
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM sales WHERE id = ?", (sale_id,))
        cols = [column[0] for column in cur.description]
        row = cur.fetchone()
        conn.close()
        return dict(zip(cols, row)) if row else None
    
    def save_sale(self, sale_data: Dict, sale_id: Optional[int] = None):
        """Guarda o actualiza una venta"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        if sale_id:
            # Actualizar
            cur.execute('''
                UPDATE sales SET 
                    date=?, seller_id=?, customer_name=?, customer_rut=?, phone_number=?, iccid=?,
                    total_amount=?, total_points=?, total_commission=?, category_summary=?,
                    device_name=?, imei=?, has_insurance=?, has_accessories=?, accessory_name=?, accessory_code=?,
                    fiber_plan=?, fiber_address=?, doc_type=?, doc_number=?, payment_method=?, status=?
                WHERE id = ?
            ''', (
                sale_data['date'], sale_data['seller_id'], sale_data['customer_name'], 
                sale_data['customer_rut'], sale_data['phone_number'], sale_data['iccid'],
                sale_data['total_amount'], sale_data['total_points'], sale_data['total_commission'], 
                sale_data['category_summary'], sale_data['device_name'], sale_data['imei'], 
                sale_data['has_insurance'], sale_data['has_accessories'], sale_data['accessory_name'], 
                sale_data['accessory_code'], sale_data['fiber_plan'], sale_data['fiber_address'],
                sale_data['doc_type'], sale_data['doc_number'], sale_data['payment_method'], 
                sale_data['status'], sale_id
            ))
        else:
            # Insertar (siempre con status "Aprobada" al crear)
            cur.execute('''
                INSERT INTO sales (
                    date, seller_id, customer_name, customer_rut, phone_number, iccid,
                    total_amount, total_points, total_commission, category_summary,
                    device_name, imei, has_insurance, has_accessories, accessory_name, accessory_code,
                    fiber_plan, fiber_address, doc_type, doc_number, payment_method, status, created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'))
            ''', (
                sale_data['date'], sale_data['seller_id'], sale_data['customer_name'], 
                sale_data['customer_rut'], sale_data['phone_number'], sale_data['iccid'],
                sale_data['total_amount'], sale_data['total_points'], sale_data['total_commission'], 
                sale_data['category_summary'], sale_data['device_name'], sale_data['imei'], 
                sale_data['has_insurance'], sale_data['has_accessories'], sale_data['accessory_name'],
                sale_data['accessory_code'], sale_data['fiber_plan'], sale_data['fiber_address'],
                sale_data['doc_type'], sale_data['doc_number'], sale_data['payment_method'],
                'Aprobada'  # Siempre aprobada al crear
            ))
        
        conn.commit()
        conn.close()

# --- INICIALIZACIÓN ---
load_custom_css()
db = DatabaseManager()

# --- ESTADO DE SESIÓN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'menu_option' not in st.session_state:
    st.session_state.menu_option = "Dashboard"
if 'editing_sale' not in st.session_state:
    st.session_state.editing_sale = None
if 'editing_seller' not in st.session_state:
    st.session_state.editing_seller = None

# --- VERIFICAR LOGIN ---
if not st.session_state.logged_in:
    render_login_page()
    st.stop()

# --- FUNCIONES AUXILIARES ---
def calculate_points_and_commission(items_selected: List[str], has_insurance: bool, has_accessories: bool, rules: Dict) -> tuple:
    """Calcula puntos y comisión basado en items seleccionados"""
    points = sum(rules.get(item, 0) for item in items_selected)
    commission = 0
    if has_insurance:
        commission += rules.get("Seguro", 1500)
    if has_accessories:
        commission += rules.get("Accesorio", 1000)
    return points, commission

def get_default_value(options: List[str], summary_list: List[str]) -> str:
    """Obtiene el valor por defecto basado en el resumen"""
    return next((i for i in options if i in summary_list), options[0])

def render_metric_card(label: str, value: int, target: int):
    """Renderiza una tarjeta de métrica consistente"""
    st.metric(label, f"{value}", f"Meta: {target}")

def render_navigation():
    """Renderiza la navegación lateral"""
    st.sidebar.title("🛠️ Sales Manager")
    st.sidebar.caption(f"👤 {st.session_state.username}")
    st.sidebar.markdown("---")
    
    nav_options = ["Dashboard", "Registrar Venta", "Historial", "Configuración"]
    for opt in nav_options:
        is_active = st.session_state.menu_option == opt
        if st.sidebar.button(
            opt, 
            key=f"nav_{opt}", 
            help=f"Ir a {opt}", 
            use_container_width=True, 
            type="primary" if is_active else "secondary"
        ):
            st.session_state.menu_option = opt
            st.session_state.editing_sale = None
            st.session_state.editing_seller = None
            st.rerun()
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# --- SECCIÓN: REGISTRAR VENTA ---
def render_sale_form():
    is_edit = st.session_state.editing_sale is not None
    st.header("📝 Editar Venta" if is_edit else "📝 Nueva Venta")
    
    sellers_df = db.get_sellers()
    rules = db.get_rules_dict()
    
    # Cargar datos si es edición
    sale_data = db.get_sale_by_id(st.session_state.editing_sale) if is_edit else {}
    
    if sellers_df.empty:
        st.warning("⚠️ No hay vendedores activos. Por favor, agregue uno en Configuración.")
        return
    
    with st.form("main_form", clear_on_submit=False):
        # Información General
        st.subheader("👤 Información General")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            seller_id = st.selectbox(
                "Vendedor", 
                options=sellers_df['id'].tolist(), 
                index=sellers_df['id'].tolist().index(sale_data['seller_id']) if is_edit else 0,
                format_func=lambda x: sellers_df[sellers_df['id']==x]['name'].values[0]
            )
        with col2:
            customer = st.text_input("Nombre del Cliente", value=sale_data.get('customer_name', ""))
        with col3:
            customer_rut = st.text_input("RUT del Cliente", value=sale_data.get('customer_rut', ""))
        with col4:
            default_date = datetime.strptime(sale_data['date'], "%Y-%m-%d") if is_edit else datetime.now()
            sale_date = st.date_input("Fecha", default_date)
        
        st.divider()
        
        # Telefonía
        st.subheader("📱 Telefonía y Líneas")
        summary_list = sale_data.get('category_summary', "").split(", ") if is_edit else []
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            tipo_porta = st.selectbox(
                "Portabilidad", 
                PRODUCT_OPTIONS['porta'], 
                index=PRODUCT_OPTIONS['porta'].index(get_default_value(PRODUCT_OPTIONS['porta'], summary_list))
            )
        with col2:
            tipo_post = st.selectbox(
                "Postpago", 
                PRODUCT_OPTIONS['post'], 
                index=PRODUCT_OPTIONS['post'].index(get_default_value(PRODUCT_OPTIONS['post'], summary_list))
            )
        with col3:
            num_tel = st.text_input("Número de Teléfono", value=sale_data.get('phone_number', ""))
        with col4:
            iccid_val = st.text_input("ICCID / Serie SIM", value=sale_data.get('iccid', ""))
        
        tipo_extra = st.selectbox(
            "Otros Planes / Servicios", 
            PRODUCT_OPTIONS['extra'], 
            index=PRODUCT_OPTIONS['extra'].index(get_default_value(PRODUCT_OPTIONS['extra'], summary_list))
        )
        
        st.divider()
        
        # Equipos
        st.subheader("📱 Equipos y Seguros")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_equipo = st.selectbox(
                "Tipo Venta Equipo", 
                PRODUCT_OPTIONS['equipo'], 
                index=PRODUCT_OPTIONS['equipo'].index(get_default_value(PRODUCT_OPTIONS['equipo'], summary_list))
            )
        with col2:
            device_name = st.text_input("Modelo del Equipo", value=sale_data.get('device_name', ""))
        with col3:
            imei_val = st.text_input("IMEI", value=sale_data.get('imei', ""))
        
        ins_check = st.checkbox("¿Incluye Seguro?", value=bool(sale_data.get('has_insurance', 0)))
        acc_check = st.checkbox("¿Incluye Accesorios?", value=bool(sale_data.get('has_accessories', 0)))
        
        # Campos de accesorios (solo visibles si se marca el checkbox)
        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            acc_name = st.text_input("Nombre del Accesorio", value=sale_data.get('accessory_name', ""), 
                                     disabled=not acc_check, placeholder="Ej: Funda, Cargador, etc.")
        with col_acc2:
            acc_code = st.text_input("Código del Accesorio", value=sale_data.get('accessory_code', ""), 
                                    disabled=not acc_check, placeholder="Ej: ACC-001")
        
        st.divider()
        
        # Fibra
        st.subheader("🌐 Fibra Óptica")
        col1, col2, col3 = st.columns([1, 2, 2])
        
        with col1:
            fibra_check = st.selectbox(
                "Venta Fibra", 
                PRODUCT_OPTIONS['fibra'], 
                index=PRODUCT_OPTIONS['fibra'].index("Fibra" if "Fibra" in summary_list else "No aplica")
            )
        with col2:
            fib_plan = st.text_input("Plan Fibra", value=sale_data.get('fiber_plan', ""))
        with col3:
            fib_addr = st.text_input("Dirección Instalación", value=sale_data.get('fiber_address', ""))
        
        st.divider()
        
        # Pago
        st.subheader("💳 Pago y Documento")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            doc_type = st.selectbox("Documento", PRODUCT_OPTIONS['doc'], 
                                   index=PRODUCT_OPTIONS['doc'].index(sale_data.get('doc_type', "Boleta")))
        with col2:
            doc_number = st.text_input("N° Documento", value=sale_data.get('doc_number', ""))
        with col3:
            payment_method = st.selectbox("Método de Pago", PRODUCT_OPTIONS['payment'], 
                                         index=PRODUCT_OPTIONS['payment'].index(sale_data.get('payment_method', "Efectivo")))
        with col4:
            amount = st.number_input("Monto Total ($)", min_value=0.0, step=500.0, 
                                    value=float(sale_data.get('total_amount', 0.0)))
        
        # SOLO mostrar estado si estamos editando
        sale_status = None
        if is_edit:
            st.divider()
            st.subheader("📊 Estado de la Venta")
            sale_status = st.selectbox(
                "Estado", 
                PRODUCT_OPTIONS['status'], 
                index=PRODUCT_OPTIONS['status'].index(sale_data.get('status', "Aprobada")),
                help="Cambia el estado de la venta entre Aprobada o Rechazada"
            )
        
        # Botones
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit = st.form_submit_button("💾 ACTUALIZAR VENTA" if is_edit else "💾 GUARDAR VENTA", use_container_width=True)
        
        with col_btn2:
            if is_edit:
                cancel = st.form_submit_button("❌ CANCELAR", use_container_width=True)
                if cancel:
                    st.session_state.editing_sale = None
                    st.session_state.menu_option = "Historial"
                    st.rerun()
        
        if submit:
            if not customer or not doc_number:
                st.error("Nombre de Cliente y Número de Documento son obligatorios.")
            else:
                # Calcular puntos y comisión
                items_sel = [i for i in [tipo_porta, tipo_post, tipo_extra, tipo_equipo, fibra_check] 
                           if i != "No aplica"]
                points, commission = calculate_points_and_commission(items_sel, ins_check, acc_check, rules)
                summary = ", ".join(items_sel)
                
                # Preparar datos
                sale_dict = {
                    'date': sale_date.strftime("%Y-%m-%d"),
                    'seller_id': seller_id,
                    'customer_name': customer,
                    'customer_rut': customer_rut,
                    'phone_number': num_tel,
                    'iccid': iccid_val,
                    'total_amount': amount,
                    'total_points': points,
                    'total_commission': commission,
                    'category_summary': summary,
                    'device_name': device_name,
                    'imei': imei_val,
                    'has_insurance': 1 if ins_check else 0,
                    'has_accessories': 1 if acc_check else 0,
                    'accessory_name': acc_name if acc_check else "",
                    'accessory_code': acc_code if acc_check else "",
                    'fiber_plan': fib_plan,
                    'fiber_address': fib_addr,
                    'doc_type': doc_type,
                    'doc_number': doc_number,
                    'payment_method': payment_method,
                    'status': sale_status if is_edit else 'Aprobada'  # Solo usar sale_status si es edición
                }
                
                with st.status("Procesando...", expanded=True) as status:
                    time.sleep(0.5)
                    db.save_sale(sale_dict, st.session_state.editing_sale)
                    time.sleep(0.5)
                    status.update(label="¡Listo!", state="complete", expanded=False)
                
                st.session_state.editing_sale = None
                st.session_state.menu_option = "Dashboard"
                st.rerun()

# --- SECCIÓN: DASHBOARD ---
def render_dashboard():
    st.header("📊 Resumen de Metas")
    
    now = datetime.now()
    col1, col2 = st.columns(2)
    
    with col1:
        month = st.selectbox("Mes", range(1, 13), index=now.month - 1)
    with col2:
        year_range = [now.year - 1, now.year, now.year + 1, now.year + 2]
        year = st.selectbox("Año", year_range, index=year_range.index(now.year))
    
    conn = db.get_connection()
    
    # Totales globales
    query_total = f'''
        SELECT 
            COALESCE(SUM(total_points), 0) as tp, 
            COALESCE(SUM(CASE WHEN category_summary LIKE '%Postpago%' THEN 1 ELSE 0 END), 0) as vp,
            COALESCE(SUM(CASE WHEN category_summary LIKE '%Portabilidad%' THEN 1 ELSE 0 END), 0) as vpt,
            COALESCE(SUM(CASE WHEN category_summary LIKE '%Fibra%' THEN 1 ELSE 0 END), 0) as vf,
            COALESCE(SUM(has_insurance), 0) as vs, 
            COALESCE(SUM(CASE WHEN category_summary LIKE '%Renovación%' THEN 1 ELSE 0 END), 0) as vr,
            COALESCE(SUM(CASE WHEN category_summary LIKE '%Wom Go%' THEN 1 ELSE 0 END), 0) as vw
        FROM sales 
        WHERE strftime('%m', date) = '{month:02}' AND strftime('%Y', date) = '{year}' AND status = 'Aprobada'
    '''
    res = pd.read_sql_query(query_total, conn).iloc[0]
    meta_g = pd.read_sql_query(f"SELECT * FROM targets WHERE seller_id=0 AND month={month} AND year={year}", conn)
    
    if not meta_g.empty:
        m = meta_g.iloc[0]
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Puntos", int(res['tp']), m['target_points'])
        with col2:
            render_metric_card("Postpago", int(res['vp']), m['target_postpago'])
        with col3:
            porta_real_pct = (res['vpt'] / res['vp'] * 100) if res['vp'] > 0 else 0
            st.metric("Portabilidad %", f"{porta_real_pct:.1f}%", f"Meta: {m['target_porta_pct']}%")
        with col4:
            render_metric_card("Fibra", int(res['vf']), m['target_fibra'])
        
        st.divider()
        
        # Métricas secundarias
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Seguros", int(res['vs']), m['target_seguro'])
        with col2:
            render_metric_card("Renovaciones", int(res['vr']), m['target_renovacion'])
        with col3:
            render_metric_card("Wom Go", int(res['vw']), m['target_womgo'])
    else:
        st.info(f"Configura las metas de {month}/{year} en la sección de Configuración para ver el progreso.")
    
    st.divider()
    st.subheader("👤 Rendimiento por Vendedor")
    
    # Query optimizada con un solo JOIN
    df_ind = pd.read_sql_query(f'''
        SELECT 
            s.name as Vendedor, 
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
        LEFT JOIN sales v ON s.id = v.seller_id 
            AND v.status = 'Aprobada' 
            AND strftime('%m', v.date) = '{month:02}' 
            AND strftime('%Y', v.date) = '{year}'
        LEFT JOIN targets t ON s.id = t.seller_id AND t.month = {month} AND t.year = {year}
        WHERE s.active = 1 
        GROUP BY s.id
    ''', conn)
    
    for _, row in df_ind.iterrows():
        with st.container(border=True):
            meta_pts = row['Meta'] if row['Meta'] > 0 else 1
            prog_val = row['Pts'] / meta_pts
            prog = min(prog_val, 1.0)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"**{row['Vendedor']}**")
            with col2:
                st.markdown(
                    f"<p style='text-align:right; color:#2563eb;'><b>{prog_val*100:.1f}% de la meta</b></p>", 
                    unsafe_allow_html=True
                )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"Puntos: {int(row['Pts'])} / {int(row['Meta'])}")
                st.progress(prog)
            with col2:
                st.caption(f"Postpagos: {int(row['v_post'])}/{int(row['m_post'])} | Fibra: {int(row['v_fibra'])}/{int(row['m_fibra'])}")
                st.caption(f"Seguros: {int(row['v_seguro'])}/{int(row['m_seguro'])} | Reno: {int(row['v_reno'])}/{int(row['m_reno'])}")
    
    conn.close()

# --- SECCIÓN: HISTORIAL ---
def render_history():
    st.header("📋 Historial de Ventas")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        filter_date = st.date_input("Filtrar por Fecha", datetime.now())
    with col2:
        sellers_df = db.get_sellers(only_active=False)
        seller_list = ["Todos"] + sellers_df['name'].tolist()
        filter_seller = st.selectbox("Filtrar por Vendedor", seller_list)
    
    conn = db.get_connection()
    
    # Query dinámica
    query_hist = f'''
        SELECT 
            v.id, v.date, s.name as Vendedor, v.customer_name as Cliente, 
            v.phone_number, v.total_points as Pts, v.status, v.category_summary as Resumen
        FROM sales v 
        JOIN sellers s ON v.seller_id = s.id 
        WHERE v.date = '{filter_date}'
    '''
    
    if filter_seller != "Todos":
        query_hist += f" AND s.name = '{filter_seller}'"
    
    df_hist = pd.read_sql_query(query_hist, conn)
    conn.close()
    
    if df_hist.empty:
        st.info("Sin ventas registradas con los filtros seleccionados.")
    else:
        for _, row in df_hist.iterrows():
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**Cliente:** {row['Cliente']}")
                    status_emoji = "✅" if row['status'] == "Aprobada" else "❌"
                    st.caption(f"{status_emoji} {row['status']}")
                with col2:
                    st.write(f"**Vendedor:** {row['Vendedor']}")
                with col3:
                    st.metric("Puntos", row['Pts'])
                with col4:
                    if st.button("✏️ Editar", key=f"edit_{row['id']}", use_container_width=True):
                        st.session_state.editing_sale = row['id']
                        st.session_state.menu_option = "Registrar Venta"
                        st.rerun()
                
                st.caption(f"📦 Servicios: {row['Resumen']}")

# --- SECCIÓN: CONFIGURACIÓN ---
def render_config():
    st.header("⚙️ Configuración del Sistema")
    
    tab1, tab2, tab3 = st.tabs(["👥 Vendedores", "🎯 Metas Mensuales", "💎 Reglas de Puntos"])
    
    with tab1:
        render_sellers_config()
    
    with tab2:
        render_targets_config()
    
    with tab3:
        render_rules_config()

def render_sellers_config():
    """Configuración de vendedores con funciones de crear, editar y desactivar"""
    st.subheader("Gestión de Vendedores")
    
    sellers_all = db.get_sellers(only_active=False)
    
    # Mostrar vendedores existentes
    for _, s in sellers_all.iterrows():
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                if st.session_state.editing_seller == s['id']:
                    # Modo edición
                    new_name = st.text_input(
                        "Nombre", 
                        value=s['name'], 
                        key=f"edit_name_{s['id']}",
                        label_visibility="collapsed"
                    )
                else:
                    # Modo vista
                    status_badge = "🟢 Activo" if s['active'] else "🔴 Inactivo"
                    st.write(f"**{s['name']}** - {status_badge}")
            
            with col2:
                if st.session_state.editing_seller == s['id']:
                    # Botón guardar
                    if st.button("💾", key=f"save_{s['id']}", help="Guardar cambios"):
                        if db.update_seller(s['id'], new_name):
                            st.session_state.editing_seller = None
                            st.success("Vendedor actualizado")
                            time.sleep(0.5)
                            st.rerun()
                else:
                    # Botón editar
                    if st.button("✏️", key=f"edit_{s['id']}", help="Editar vendedor"):
                        st.session_state.editing_seller = s['id']
                        st.rerun()
            
            with col3:
                if st.session_state.editing_seller == s['id']:
                    # Botón cancelar
                    if st.button("❌", key=f"cancel_{s['id']}", help="Cancelar"):
                        st.session_state.editing_seller = None
                        st.rerun()
                else:
                    # Botón activar/desactivar
                    toggle_text = "🔴" if s['active'] else "🟢"
                    toggle_help = "Desactivar" if s['active'] else "Activar"
                    if st.button(toggle_text, key=f"toggle_{s['id']}", help=toggle_help):
                        if db.toggle_seller_status(s['id']):
                            st.success(f"Vendedor {'desactivado' if s['active'] else 'activado'}")
                            time.sleep(0.5)
                            st.rerun()
            
            with col4:
                # Información adicional
                if not (st.session_state.editing_seller == s['id']):
                    with st.popover("ℹ️"):
                        st.caption(f"**Creado:** {s.get('created_at', 'N/A')[:10]}")
                        if s.get('updated_at'):
                            st.caption(f"**Actualizado:** {s['updated_at'][:10]}")
    
    st.divider()
    
    # Formulario para agregar nuevo vendedor
    st.subheader("➕ Agregar Nuevo Vendedor")
    with st.form("add_seller", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_name = st.text_input("Nombre del Vendedor", placeholder="Ej: Juan Pérez")
        with col2:
            submit = st.form_submit_button("➕ Agregar", use_container_width=True)
        
        if submit and new_name:
            if db.add_seller(new_name):
                st.success(f"✅ Vendedor '{new_name}' agregado exitosamente")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Error al agregar vendedor")

def render_targets_config():
    """Configuración de metas"""
    now = datetime.now()
    
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Mes", range(1, 13), index=now.month - 1, key="cfg_month")
    with col2:
        year = st.number_input("Año", value=now.year, key="cfg_year")
    
    conn = db.get_connection()
    cur = conn.cursor()
    
    # Meta Global
    st.subheader("🏬 Meta Global de Tienda")
    cur.execute("SELECT * FROM targets WHERE seller_id=0 AND month=? AND year=?", (month, year))
    global_target = cur.fetchone()
    
    with st.form("global_targets"):
        v = global_target if global_target else [0] * 11
        
        col1, col2, col3, col4 = st.columns(4)
        g_pts = col1.number_input("Puntos", value=v[4], min_value=0)
        g_post = col2.number_input("Postpago", value=v[5], min_value=0)
        g_fib = col3.number_input("Fibra", value=v[7], min_value=0)
        g_pct = col4.number_input("% Porta", value=float(v[6]), min_value=0.0, max_value=100.0)
        
        col1, col2, col3 = st.columns(3)
        g_seg = col1.number_input("Seguros", value=v[8], min_value=0)
        g_ren = col2.number_input("Renovaciones", value=v[9], min_value=0)
        g_wom = col3.number_input("Wom Go", value=v[10], min_value=0)
        
        if st.form_submit_button("💾 Guardar Meta Global", use_container_width=True):
            cur.execute('''
                INSERT INTO targets (seller_id, month, year, target_points, target_postpago, 
                    target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
                VALUES (0,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(seller_id, month, year) DO UPDATE SET
                    target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
                    target_porta_pct=excluded.target_porta_pct, target_fibra=excluded.target_fibra,
                    target_seguro=excluded.target_seguro, target_renovacion=excluded.target_renovacion, 
                    target_womgo=excluded.target_womgo
            ''', (month, year, g_pts, g_post, g_pct, g_fib, g_seg, g_ren, g_wom))
            conn.commit()
            st.success("✅ Meta Global guardada exitosamente")
    
    st.divider()
    
    # Metas Individuales
    st.subheader("👤 Metas Individuales")
    active_sellers = db.get_sellers()
    
    if not active_sellers.empty:
        if st.button("🪄 Distribuir Meta Global entre Vendedores Activos"):
            num_sellers = len(active_sellers)
            for _, seller in active_sellers.iterrows():
                cur.execute('''
                    INSERT INTO targets (seller_id, month, year, target_points, target_postpago, 
                        target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(seller_id, month, year) DO UPDATE SET
                        target_points=excluded.target_points, target_postpago=excluded.target_postpago, 
                        target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro, 
                        target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
                ''', (seller['id'], month, year, g_pts//num_sellers, g_post//num_sellers, 
                     g_pct, g_fib//num_sellers, g_seg//num_sellers, g_ren//num_sellers, g_wom//num_sellers))
            conn.commit()
            st.success("✅ Metas distribuidas exitosamente")
            st.rerun()
        
        st.divider()
        
        selected_seller = st.selectbox("Editar meta individual para:", active_sellers['name'].tolist())
        seller_id = active_sellers[active_sellers['name'] == selected_seller]['id'].values[0]
        
        cur.execute("SELECT * FROM targets WHERE seller_id=? AND month=? AND year=?", (seller_id, month, year))
        seller_target = cur.fetchone()
        
        with st.form("individual_target"):
            sv = seller_target if seller_target else [0] * 11
            
            col1, col2, col3, col4 = st.columns(4)
            si_pts = col1.number_input("Puntos", value=sv[4], min_value=0)
            si_post = col2.number_input("Postpago", value=sv[5], min_value=0)
            si_fib = col3.number_input("Fibra", value=sv[7], min_value=0)
            si_pct = col4.number_input("% Porta", value=float(sv[6]), min_value=0.0, max_value=100.0)
            
            col1, col2, col3 = st.columns(3)
            si_seg = col1.number_input("Seguros", value=sv[8], min_value=0)
            si_ren = col2.number_input("Renovación", value=sv[9], min_value=0)
            si_wom = col3.number_input("Wom Go", value=sv[10], min_value=0)
            
            if st.form_submit_button("💾 Guardar Meta Individual", use_container_width=True):
                cur.execute('''
                    INSERT INTO targets (seller_id, month, year, target_points, target_postpago, 
                        target_porta_pct, target_fibra, target_seguro, target_renovacion, target_womgo)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(seller_id, month, year) DO UPDATE SET 
                        target_points=excluded.target_points, target_postpago=excluded.target_postpago,
                        target_fibra=excluded.target_fibra, target_seguro=excluded.target_seguro,
                        target_renovacion=excluded.target_renovacion, target_womgo=excluded.target_womgo
                ''', (seller_id, month, year, si_pts, si_post, si_pct, si_fib, si_seg, si_ren, si_wom))
                conn.commit()
                st.success("✅ Meta Individual actualizada exitosamente")
    
    conn.close()

def render_rules_config():
    """Configuración de reglas de puntos"""
    st.subheader("Valores de Puntos por Producto")
    
    conn = db.get_connection()
    df_rules = pd.read_sql_query("SELECT * FROM point_rules ORDER BY type, item_name", conn)
    
    with st.form("edit_rules"):
        st.write("Ajusta los valores de puntos y comisiones:")
        
        for idx, row in df_rules.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{row['item_name']}**")
            with col2:
                st.caption(f"Tipo: {row['type']}")
            with col3:
                new_val = st.number_input(
                    "Valor", 
                    value=float(row['value']), 
                    key=f"rule_{row['id']}", 
                    min_value=0.0,
                    label_visibility="collapsed"
                )
                df_rules.at[idx, 'value'] = new_val
        
        if st.form_submit_button("💾 Actualizar Todas las Reglas", use_container_width=True):
            cur = conn.cursor()
            for _, r in df_rules.iterrows():
                cur.execute("UPDATE point_rules SET value = ? WHERE id = ?", (r['value'], r['id']))
            conn.commit()
            st.success("✅ Reglas actualizadas correctamente")
    
    conn.close()

# --- NAVEGACIÓN Y RENDERIZADO PRINCIPAL ---
render_navigation()

choice = st.session_state.menu_option

if choice == "Registrar Venta":
    render_sale_form()
elif choice == "Dashboard":
    render_dashboard()
elif choice == "Historial":
    render_history()
elif choice == "Configuración":
    render_config()
