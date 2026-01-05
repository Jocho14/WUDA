import os

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


def configure_monitoring(app, db_engine=None):

    # Nazwa serwisu widoczna w prometeuszu
    resource = Resource(
        attributes={
            SERVICE_NAME: "monitor-wudy"
        }
    )

    # Na jakim endpointcie sa dostepne metryki
    otlp_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://localhost:4317"
    )

    # Konfiguracja sledzenia 
    tracer_provider = TracerProvider(resource=resource)

    trace_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        insecure=True
    )

    tracer_provider.add_span_processor(
        BatchSpanProcessor(trace_exporter)
    )

    trace.set_tracer_provider(tracer_provider)

    # Konfiguracja pobierania metryk, ustawiamy co ile maja byc zczytywane itp.
    metric_reader = PeriodicExportingMetricReader(
        exporter=OTLPMetricExporter(
            endpoint=otlp_endpoint,
            insecure=True
        ),
        export_interval_millis=15_000
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader]
    )

    metrics.set_meter_provider(meter_provider)

    # Konfiguracja dla requestów
    FlaskInstrumentor().instrument_app(app)

    # konfiguracja dla Bazy Danych (o ile podana)
    if db_engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=db_engine)
