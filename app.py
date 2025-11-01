import os
import random
import string
import datetime as dt
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# ------------------------
# Basic setup
# ------------------------
st.set_page_config(page_title="Telecom Chatbot (Streamlit + Groq)", page_icon="📶", layout="centered")

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL") or st.secrets.get("GROQ_MODEL", "llama-3.1-8b-instant")

if not API_KEY:
    st.error("Falta GROQ_API_KEY en .env o en st.secrets. Agrega tu clave y recarga.")
    st.stop()

client = Groq(api_key=API_KEY)

# ------------------------
# Utilidades
# ------------------------
def fmt_soles(v):
    try:
        return f"S/ {float(v):.2f}"
    except:
        return str(v)

def fmt_gb(v):
    try:
        return f"{float(v):.1f} GB"
    except:
        return str(v)

def ticket_code():
    return "SOP-" + dt.datetime.now().strftime("%Y%m%d") + "-" + "".join(random.choices(string.digits, k=5))

# ------------------------
# Usuarios permitidos (DNI -> perfil con datos variables)
# ------------------------
USERS = {
    # Carlos
    "72862246": {
        "name": "Carlos Ugaz",
        "plan": "Plan Pro 65",
        "internet": "300 Mbps",
        "billing": {"amount": 62.90},
        "cycle_day": 30,
        "mobile": {"minutes_used": 120, "minutes_total": 300,
                   "data_used_gb": 3.2, "data_total_gb": 10,
                   "sms_used": 50, "sms_total": 200},
        "fixed": {"down_used_gb": 120, "down_total_gb": 500,
                  "up_used_gb": 30, "up_total_gb": 200,
                  "speed": "150 Mbps"},
    },
    # María
    "78624524": {
        "name": "María Fernanda Rojas",
        "plan": "Plan Smart 29",
        "internet": "200 Mbps",
        "billing": {"amount": 49.90},
        "cycle_day": 30,
        "mobile": {"minutes_used": 80, "minutes_total": 200,
                   "data_used_gb": 4.5, "data_total_gb": 15,
                   "sms_used": 20, "sms_total": 100},
        "fixed": {"down_used_gb": 95, "down_total_gb": 400,
                  "up_used_gb": 18, "up_total_gb": 150,
                  "speed": "200 Mbps"},
    },
    # José
    "76552356": {
        "name": "José Luis Quispe",
        "plan": "Plan Max 45",
        "internet": "150 Mbps",
        "billing": {"amount": 79.50},
        "cycle_day": 30,
        "mobile": {"minutes_used": 220, "minutes_total": 400,
                   "data_used_gb": 12.0, "data_total_gb": 50,
                   "sms_used": 150, "sms_total": 500},
        "fixed": {"down_used_gb": 210, "down_total_gb": 600,
                  "up_used_gb": 40, "up_total_gb": 250,
                  "speed": "150 Mbps"},
    },
    # Ana
    "12456943": {
        "name": "Ana Lucía Paredes",
        "plan": "Plan Smart 29",
        "internet": "100 Mbps",
        "billing": {"amount": 55.00},
        "cycle_day": 30,
        "mobile": {"minutes_used": 150, "minutes_total": 250,
                   "data_used_gb": 5.8, "data_total_gb": 20,
                   "sms_used": 65, "sms_total": 200},
        "fixed": {"down_used_gb": 180, "down_total_gb": 350,
                  "up_used_gb": 25, "up_total_gb": 120,
                  "speed": "100 Mbps"},
    },
    # Luis
    "18963245": {
        "name": "Luis Alberto Salazar",
        "plan": "Plan Pro 65",
        "internet": "300 Mbps",
        "billing": {"amount": 95.80},
        "cycle_day": 30,
        "mobile": {"minutes_used": 310, "minutes_total": 600,
                   "data_used_gb": 38.6, "data_total_gb": 120,
                   "sms_used": 220, "sms_total": 1000},
        "fixed": {"down_used_gb": 320, "down_total_gb": 1000,
                  "up_used_gb": 70, "up_total_gb": 400,
                  "speed": "300 Mbps"},
    },
}

def llm_reply(messages, temperature=0.3):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error al llamar al LLM: `{e}`"

# ------------------------
# Tabs
# ------------------------
st.title("📶 Chatbot de Atención al Cliente — Telco Demo")
st.caption("Demo educativa en Streamlit + Groq. No usa datos reales.")

tab_menu, tab_free = st.tabs(["🗺️ Menú guiado (flujo)", "💬 Asistente libre (LLM)"])

# ========================================================================
# TAB 1: MENU GUIADO (FLOWCHART)
# ========================================================================
with tab_menu:
    # Initialize session state
    if "flow" not in st.session_state:
        st.session_state.flow = {
            "step": 0,
            "dni": "",
            "phone": "",
            "option": None,
            "suboption": None,
            "profile": None,   # perfil del usuario autenticado
            "history": [],     # chat bubbles
        }

    def push(role, text):
        st.session_state.flow["history"].append({"role": role, "content": text})
        with st.chat_message(role):
            st.markdown(text)

    st.write("Este flujo replica un **chatbot de telco** con pasos: saludo → identificación → validación → menú → atención → cierre.")

    # Render chat bubbles from history
    for msg in st.session_state.flow["history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    step = st.session_state.flow["step"]

    # 0) Inicio / Saludo
    if step == 0:
        greeting = "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
        if not st.session_state.flow["history"]:
            push("assistant", greeting)
        if st.button("Iniciar identificación"):
            st.session_state.flow["step"] = 1
            st.rerun()

    # 1) Identificación de usuario
    elif step == 1:
        push("assistant", "Por favor, indícame tu **DNI** y **número de teléfono** para continuar.")
        dni = st.text_input("DNI", value=st.session_state.flow["dni"], key="dni_input")
        phone = st.text_input("Teléfono", value=st.session_state.flow["phone"], key="phone_input")

        colA, colB = st.columns(2)
        if colA.button("Enviar datos"):
            st.session_state.flow["dni"] = dni.strip()
            st.session_state.flow["phone"] = phone.strip()
            push("user", f"DNI: {st.session_state.flow['dni']} · Teléfono: {st.session_state.flow['phone']}")
            st.session_state.flow["step"] = 2
            st.rerun()
        if colB.button("Cancelar"):
            push("user", "Cancelar.")
            st.session_state.flow["step"] = 0
            st.rerun()

    # 2) Validación con whitelist
    elif step == 2:
        dni = st.session_state.flow["dni"]
        phone = st.session_state.flow["phone"]

        phone_ok = phone and phone.replace("+", "").replace("-", "").isdigit()
        dni_ok = dni and dni in USERS

        if dni_ok and phone_ok:
            profile = USERS[dni]
            st.session_state.flow["profile"] = profile
            push("assistant", f"✅ Datos validados. Bienvenido/a, **{profile['name']}**.")
            st.session_state.flow["step"] = 3
            st.rerun()
        else:
            push(
                "assistant",
                "❌ No pudimos autenticarte con los datos ingresados. "
                "Por seguridad, finalizamos la atención. Si crees que es un error, comunícate con un agente."
            )
            st.session_state.flow["step"] = 6  # finalizar
            st.rerun()

    # 3) Menú Principal
    elif step == 3:
        profile = st.session_state.flow.get("profile", {})
        push("assistant", f"Cliente: **{profile.get('name','')}** — Plan actual: **{profile.get('plan','N/D')}**.")
        push("assistant", "Selecciona una opción:\n\n1) **Saldo/Consumo**\n2) **Pagos/Factura**\n3) **Planes/Paquetes**\n4) **Problemas Técnicos**\n5) **Hablar con un Agente**")
        options = {
            "1) Saldo/Consumo": 1,
            "2) Pagos/Factura": 2,
            "3) Planes/Paquetes": 3,
            "4) Problemas Técnicos": 4,
            "5) Hablar con un Agente": 5,
        }
        choice = st.radio("Menú Principal", list(options.keys()), label_visibility="collapsed")
        if st.button("Continuar ▶️"):
            st.session_state.flow["option"] = options[choice]
            push("user", f"Selecciono la opción {options[choice]}.")
            st.session_state.flow["step"] = 4
            st.rerun()

    # 4) Ramas de atención
    elif step == 4:
        opt = st.session_state.flow["option"]
        profile = st.session_state.flow.get("profile", {})

        # Opción 1: Saldo/Consumo
        if opt == 1:
            push("assistant", "¿Deseas ver **Saldo/Consumo Móvil** o **Consumo/Detalles de Internet**?")
            sub = st.radio("Elige una vista", ["Saldo/Consumo Móvil", "Consumo/Detalles Internet"])
            if st.button("Mostrar"):
                push("user", sub)
                if sub == "Saldo/Consumo Móvil":
                    m = profile.get("mobile", {})
                    msg = (
                        f"📱 **Saldo móvil** (Plan actual: **{profile.get('plan','N/D')}**)\n\n"
                        f"- Minutos: {m.get('minutes_used',0)}/{m.get('minutes_total','-')}\n"
                        f"- Datos: {fmt_gb(m.get('data_used_gb',0))} / {fmt_gb(m.get('data_total_gb','-'))}\n"
                        f"- SMS: {m.get('sms_used',0)}/{m.get('sms_total','-')}\n"
                        f"- Fecha de corte: {profile.get('cycle_day',30)} del mes\n"
                    )
                else:
                    f = profile.get("fixed", {})
                    msg = (
                        f"🌐 **Consumo Internet Fijo** (Velocidad actual: **{profile.get('internet','N/D')}**)\n\n"
                        f"- Descarga: {fmt_gb(f.get('down_used_gb',0))} / {fmt_gb(f.get('down_total_gb','-'))}\n"
                        f"- Subida: {fmt_gb(f.get('up_used_gb',0))} / {fmt_gb(f.get('up_total_gb','-'))}\n"
                        f"- Velocidad contratada: {f.get('speed', profile.get('internet','N/D'))}\n"
                        f"- Fecha de corte: {profile.get('cycle_day',30)} del mes\n"
                    )
                push("assistant", msg)
                st.session_state.flow["step"] = 5
                st.rerun()

        # Opción 2: Pagos/Factura
        elif opt == 2:
            amount = profile.get("billing", {}).get("amount", 0)
            msg = (
                "🧾 **Detalle de Facturación**\n\n"
                f"- Cliente: **{profile.get('name','')}**\n"
                f"- Monto a pagar: **{fmt_soles(amount)}**\n"
                "- Vencimiento: **" + (dt.date.today() + dt.timedelta(days=7)).strftime("%d/%m/%Y") + "**\n"
                "- Medio de pago: *enlace de ejemplo* (no transaccional)\n"
            )
            push("assistant", msg)
            st.session_state.flow["step"] = 5
            st.rerun()

        # Opción 3: Planes/Paquetes
        elif opt == 3:
            push("assistant", f"Tu plan móvil actual es **{profile.get('plan','N/D')}** y tu internet es **{profile.get('internet','N/D')}**.")
            push("assistant", "¿Qué te interesa gestionar?")
            sub = st.radio("Submenú", ["Planes Móviles", "Paquetes Internet"])
            if st.button("Ver opciones"):
                push("user", sub)
                if sub == "Planes Móviles":
                    plans = [
                        "- **Plan Smart 29**: 15 GB + ilimitado en redes sociales",
                        "- **Plan Max 45**: 50 GB + minutos/sms ilimitados",
                        "- **Plan Pro 65**: 120 GB + roaming LATAM",
                    ]
                    push("assistant", "Opciones disponibles:\n" + "\n".join(plans) + "\n\nUsa el botón para *cambiar/contratar* (simulado).")
                else:
                    bundles = [
                        "- **Paquete +5 GB** por 7 días",
                        "- **Paquete +20 GB** por 30 días",
                        "- **Mejora de velocidad** a 300 Mbps",
                        f"- **Tu velocidad actual**: {profile.get('internet','N/D')}",
                    ]
                    push("assistant", "Paquetes disponibles:\n" + "\n".join(bundles) + "\n\nUsa el botón para *contratar* (simulado).")
                st.session_state.flow["step"] = 5
                st.rerun()

        # Opción 4: Problemas Técnicos
        elif opt == 4:
            push("assistant", "Describe tu caso: **Problema Fijo (Diagnóstico básico)** o **Problema Móvil (Cobertura en zona)**.")
            sub = st.radio("Tipo de incidencia", ["Problema Fijo — Diagnóstico (ping básico)", "Problema Móvil — Verificar cobertura"])
            if st.button("Ejecutar diagnóstico"):
                push("user", sub)
                if "Fijo" in sub:
                    diag = (
                        "🔧 Diagnóstico básico sugerido:\n"
                        "1) Reinicia tu router (apágalo 20s y vuelve a encender).\n"
                        "2) Verifica que los cables estén firmes.\n"
                        "3) Prueba con cable directo al router.\n"
                        "Si persiste, generamos un ticket para soporte técnico."
                    )
                    push("assistant", diag)
                else:
                    cov = (
                        "📍 Verificación de cobertura (simulada): tu zona aparece *sin incidencias reportadas*.\n"
                        "Si sigues con problemas de señal, podemos escalar a soporte."
                    )
                    push("assistant", cov)
                if st.button("Generar ticket de soporte"):
                    code = ticket_code()
                    push("assistant", f"✅ Ticket generado: **{code}**. Te contactaremos por SMS/WhatsApp.")
                st.session_state.flow["step"] = 5
                st.rerun()

        # Opción 5: Hablar con un agente
        elif opt == 5:
            push("assistant", "👥 Enseguida te transfiero con un **agente humano**. Tiempo de espera estimado: *breve* (simulado).")
            st.session_state.flow["step"] = 5
            st.rerun()

    # 5) Cierre / ¿Algo más?
    elif step == 5:
        push("assistant", "¿Requieres algo más? Si eliges **Sí**, te regreso al Menú Principal; si eliges **No**, finalizamos.")
        choice = st.radio("¿Algo más?", ["Sí", "No"])
        col1, col2 = st.columns(2)
        if col1.button("Continuar"):
            if choice == "Sí":
                st.session_state.flow["step"] = 3
            else:
                st.session_state.flow["step"] = 6
            st.rerun()
        if col2.button("Reiniciar flujo"):
            st.session_state.flow = {"step": 0, "dni": "", "phone": "", "option": None, "suboption": None, "profile": None, "history": []}
            st.rerun()

    # 6) Fin
    elif step == 6:
        push("assistant", "¡Gracias por comunicarte! Fue un gusto ayudarte. 🙌")
        if st.button("Empezar de nuevo"):
            st.session_state.flow = {"step": 0, "dni": "", "phone": "", "option": None, "suboption": None, "profile": None, "history": []}
            st.rerun()

# ========================================================================
# TAB 2: ASISTENTE LIBRE (LLM)
# ========================================================================
with tab_free:
    if "free_history" not in st.session_state:
        st.session_state.free_history = []

    SYSTEM_PROMPT = (
        "Eres un asistente de soporte para una empresa de telecomunicaciones. "
        "Responde de forma amable, concisa y útil; si el usuario comparte datos personales, "
        "protéjelos. Si te piden operaciones que requieren sistemas internos, aclara que es una demo."
    )

    for m in st.session_state.free_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    user_msg = st.chat_input("Escribe tu consulta…")
    if user_msg:
        st.session_state.free_history.append({"role": "user", "content": user_msg})
        with st.chat_message("user"):
            st.markdown(user_msg)

        messages = [{"role":"system","content": SYSTEM_PROMPT}]
        messages.extend(st.session_state.free_history)
        answer = llm_reply(messages)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.free_history.append({"role": "assistant", "content": answer})

st.sidebar.subheader("⚙️ Configuración")
st.sidebar.write(f"Modelo LLM: `{MODEL}`")
