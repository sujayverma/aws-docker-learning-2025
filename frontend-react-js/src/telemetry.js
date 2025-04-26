// src/telemetry.js
import { WebTracerProvider } from "@opentelemetry/sdk-trace-web";
import { ConsoleSpanExporter, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { FetchInstrumentation } from "@opentelemetry/instrumentation-fetch";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { trace } from "@opentelemetry/api";

const provider = new WebTracerProvider();

// Optional Console Exporter for debugging
provider.addSpanProcessor(new SimpleSpanProcessor(new ConsoleSpanExporter()));

// Honeycomb Exporter
const exporter = new OTLPTraceExporter({
  url: "https://api.honeycomb.io:443", // Honeycomb OTLP HTTP endpoint
  headers: {
    "x-honeycomb-team": "x-honeycomb-team=CN7b7RcLDWxrHoYsroasRC", // your Honeycomb API key
    "x-honeycomb-dataset": "frontend-react-js", // You can give it a dataset name
  },
});

provider.addSpanProcessor(new SimpleSpanProcessor(exporter));

// Instrument fetch API (React uses fetch under the hood)
registerInstrumentations({
  instrumentations: [new FetchInstrumentation({})],
});

provider.register();



export const tracer = trace.getTracer("frontend-react");