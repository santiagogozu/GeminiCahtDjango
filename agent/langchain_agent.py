import os
import datetime
from typing import Optional
import requests
from dotenv import load_dotenv

from langchain.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

load_dotenv()

# === Funciones Tool ===


def get_physicochemical_report(report_id: str) -> dict:
    base_url = os.getenv("PHYSICOCHEMICAL_API")
    if not base_url:
        raise ValueError(f"La variable de entorno '{base_url}' no está definida.")
    if not report_id.strip():
        return "Entrada vacía. Por favor, proporcione el ID de un reporte."
    report_id = report_id.strip().strip('"').strip("'").upper()
    try:
        url = f"{base_url}/{report_id}/reporte"
        response = requests.get(url)
        print(response)
        response.raise_for_status()
        return {
            "report_id": report_id,
            "url": url,
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(
            f"No se pudo encontrar el reporte fisicoquímico con el código {report_id}. Error: {e}"
        )
    except ValueError as e:
        return str(e)


def get_document(titulo: Optional[str] = None, año: Optional[int] = None) -> dict:
    base_url = os.getenv("DOCUMENT_API")
    if not base_url:
        raise ValueError(f"La variable de entorno '{base_url}' no está definida.")

    params = {}
    if titulo:
        titulo = titulo.strip().strip('"').strip("'")
    params = {"search": titulo} if titulo else {}

    if año:
        params["search"] = año

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        documentos = data.get("values", [])
        return {
            "resultados": documentos,
        }
    except requests.exceptions.RequestException as e:
        return f"Error al buscar documentos: {e}"


def get_hydrobiological_report(report_id: Optional[str] = None) -> str:
    base_url = os.getenv("HYDROBIOLOGICAL_API")
    if not base_url:
        raise ValueError(f"La variable de entorno '{base_url}' no está definida.")
    if not report_id:
        return "Entrada vacía. Por favor, proporcione el nombre de un reporte."
    report_id = report_id.strip().strip('"').strip("'").upper()
    url = f"{base_url}/{report_id}/reporte"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {
            "report_id": report_id,
            "url": url,
        }

    except requests.exceptions.RequestException as e:
        raise ValueError(
            f"No se pudo encontrar el reporte hidrobiológico con el código {report_id}."
        )


def get_todays_date() -> str:
    today = datetime.datetime.now()
    day_name = today.strftime("%A")
    date_string = today.strftime("%Y-%m-%d")
    return f"Hoy es {day_name}, {date_string}"


# === Herramientas para LangChain ===

get_document_tool = StructuredTool.from_function(
    func=get_document,
    name="buscar_documentos_func",
    description="Busca documentos por título y opcionalmente por año. Ejemplo: Calidad del aire, año 2023.",
)

get_physicochemical_report_tool = StructuredTool.from_function(
    func=get_physicochemical_report,
    name="descargar_reporte_fisicoquimicos",
    description="Devuelve el enlace de descarga del reporte físico-químico dado el nombre.",
)

get_hydrobiological_report_tool = StructuredTool.from_function(
    func=get_hydrobiological_report,
    name="descargar_reporte_hidrobiologico",
    description="Devuelve el enlace de descarga del reporte hidrobiológico desde la API de Piragua usando un código.",
)

get_todays_date_tool = StructuredTool.from_function(
    func=get_todays_date,
    name="obtener_fecha_hoy",
    description="Devuelve la fecha y el día actual para tener como base para calculos de tiempo.",
)

tools = [
    get_document_tool,
    get_physicochemical_report_tool,
    get_hydrobiological_report_tool,
    get_todays_date_tool,
]

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    api_key=os.getenv("GENAI_API_KEY"),
    temperature=0.3,
)

llm_with_tools = llm.bind_tools(tools)

tool_list = {
    "descargar_reporte_hidrobiologico": get_hydrobiological_report_tool,
    "buscar_documentos_func": get_document_tool,
    "descargar_reporte_fisicoquimicos": get_physicochemical_report_tool,
    "obtener_fecha_hoy": get_todays_date_tool,
}

system_message = SystemMessage(
    content="Eres un asistente útil que siempre responde en español, sin mencionar que se usan herramientas. Siempre incluye los enlaces cuando estén disponibles."
)


# === Función principal para usar desde la API ===


def process_query(query: str) -> str:
    try:
        messages = [system_message, HumanMessage(content=query)]

        for _ in range(3):  # máximo 3 ciclos de invocación
            ai_message = llm_with_tools.invoke(messages)
            # print("Mensaje recibido:", ai_message)
            messages.append(ai_message)

            if not ai_message.tool_calls:
                return ai_message.content

            # Ejecutar herramientas
            for tool_call in ai_message.tool_calls:
                tool_name = tool_call["name"].lower()
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                selected_tool = tool_list.get(tool_name)
                if selected_tool:
                    tool_output = selected_tool.invoke(tool_args)
                    # print(f"[{tool_name}] output:", tool_output)
                    messages.append(
                        ToolMessage(content=str(tool_output), tool_call_id=tool_id)
                    )
                else:
                    return f"⚠️ Herramienta no encontrada: {tool_name}"

        # # 🔁 Generar mensaje final después de que se procesan los tools
        final_message = llm_with_tools.invoke(messages)
        print("Mensaje final generado:", final_message)
        return final_message.content

    except Exception as e:
        return f"Error al ejecutar el agente: {str(e)}"
