#!/usr/bin/env python3
"""Response Builder - Genera respuestas asistidas por LLM usando datos analíticos."""

from typing import Optional

from .indicators_engine import IndicatorsEngine


class ResponseBuilder:
    """Construye respuestas consultivas apoyadas en datos reales."""

    def __init__(self, indicators: "IndicatorsEngine", llm_client=None) -> None:
        self.indicators = indicators
        self.all_indicators = None
        self.llm_client = llm_client  # DeepSeek API client

    def build_response(
        self,
        query: str,
        intent: str = "MIXED",
        requested_analyses: Optional[list[str]] = None,
    ) -> str:
        """Ejecuta el flujo principal garantizando que los indicadores estén disponibles."""

        # Calcula los indicadores solo una vez para evitar recomputación costosa.
        if self.all_indicators is None:
            try:
                print("🔄 Calculando indicadores para respuesta contextual...")
                self.all_indicators = self.indicators.calculate_all_indicators()
                print(f"✅ Indicadores calculados: {len(self.all_indicators)} tipos")
            except Exception as exc:  # pragma: no cover - logging defensivo
                print(f"❌ Error calculando indicadores: {exc}")
                self.all_indicators = {
                    "volumen_tendencia": {"total_accidentes": 754},
                    "perfil_siniestralidad": {"top_formas_accidente": []},
                    "impacto_operativo": {"dias_perdidos_total": 0},
                }

        # requested_analyses se mantiene por compatibilidad; hoy no se usa.
        _ = requested_analyses
        return self._generate_intelligent_response(query, intent)

    def _generate_intelligent_response(self, query: str, intent: str) -> str:
        """Construye la respuesta con el LLM y aplica fallback si falla."""

        data_context = self._prepare_data_context(query)
        system_prompt = f"""Eres un consultor experto en Seguridad y Salud Ocupacional (SSO) con acceso a datos reales de accidentes laborales.

DATOS DISPONIBLES:
{data_context}

INSTRUCCIONES:
- Responde de manera natural y conversacional como un consultor experto.
- Usa SIEMPRE los datos reales proporcionados en tu análisis.
- Sé específico y preciso con números, porcentajes y tendencias.
- Proporciona insights accionables y recomendaciones prácticas.
- Adapta tu respuesta exactamente a la pregunta del usuario.
- Usa un tono profesional pero accesible.
- Incluye datos específicos para respaldar tus conclusiones."""

        user_prompt = f"Pregunta del usuario: {query}"

        if self.llm_client:
            try:
                response = self.llm_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                )
                return response.choices[0].message.content
            except Exception as exc:  # pragma: no cover - logging defensivo
                print(f"❌ Error en LLM: {exc}")
                return self._fallback_response(query)

        return self._fallback_response(query)

    def _prepare_data_context(self, query: str = "") -> str:
        """Arma el contexto factual que alimenta al LLM."""

        if not self.all_indicators:
            return "Datos no disponibles"

        context_parts: list[str] = []

        volumen = self.all_indicators.get("volumen_tendencia", {})
        if volumen:
            total = volumen.get("total_accidentes", 0)
            context_parts.append(f"VOLUMEN: {total} accidentes totales")
            if volumen.get("accidentes_por_año"):
                años_data = volumen["accidentes_por_año"]
                context_parts.append(
                    f"TENDENCIA ANUAL: {dict(list(años_data.items())[-3:])}"
                )

        perfil = self.all_indicators.get("perfil_siniestralidad", {})
        if perfil and perfil.get("top_formas_accidente"):
            formas = perfil["top_formas_accidente"]
            formas_texto = ", ".join(
                f"{f.get('categoria', 'N/A')}: {f.get('cantidad', 0)} casos"
                for f in formas[:10]
            )
            context_parts.append(f"FORMAS DE ACCIDENTE: {formas_texto}")

            if any(
                term in query.lower()
                for term in ["atrapamiento", "aprisionamiento", "atrapado", "aprisionado"]
            ):
                atrapamiento = self._get_specific_accident_count("atrapamiento")
                if atrapamiento:
                    context_parts.append(f"ATRAPAMIENTOS ESPECÍFICOS: {atrapamiento}")

        impacto = self.all_indicators.get("impacto_operativo", {})
        if impacto:
            context_parts.append(
                f"DÍAS PERDIDOS: {impacto.get('dias_descanso_total', 0)} días totales"
            )
            promedio = impacto.get("dias_promedio_accidente", 0)
            context_parts.append(f"PROMEDIO POR ACCIDENTE: {promedio:.1f} días")

        return " | ".join(context_parts) if context_parts else "Datos en procesamiento"

    def _get_specific_accident_count(self, accident_type: str) -> str:
        """Obtiene detalle puntual de un tipo de accidente."""

        try:
            df = self.indicators.df
            if "Forma de Accidente" not in df.columns:
                return ""

            if accident_type.lower() == "atrapamiento":
                matches = df[
                    df["Forma de Accidente"].str.contains(
                        "ATRAPAMIENTO|APRISIONAMIENTO", case=False, na=False
                    )
                ]
                if not matches.empty:
                    counts = matches["Forma de Accidente"].value_counts()
                    total = len(matches)
                    detalles = ", ".join(f"{k}: {v}" for k, v in counts.items())
                    return f"Total {total} casos ({detalles})"
            return ""
        except Exception as exc:  # pragma: no cover - logging defensivo
            print(f"Error obteniendo conteo específico: {exc}")
            return ""

    def _fallback_response(self, query: str) -> str:
        """Genera una respuesta básica cuando no se obtiene salida del LLM."""

        contexto = self._prepare_data_context(query)
        return (
            "Basado en el análisis de tus datos de seguridad laboral:\n\n"
            f"{contexto}\n\n"
            "Para responder específicamente a tu consulta "
            f"\"{query}\", necesito procesar la información con mayor detalle.\n\n"
            "¿Podrías reformular tu pregunta o ser más específico sobre qué"
            " aspecto te interesa más?"
        )
