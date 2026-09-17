# Arquitectura de Sistema — Diagramas C4 de The Playbook

Este documento contiene la especificación arquitectónica del sistema **The Playbook** siguiendo el modelo **C4** (Contexto, Contenedores, Componentes y Despliegue/Secuencia). 

> 💡 **Nota de renderizado:** Los diagramas utilizan sintaxis `flowchart` de **Mermaid.js** con cajas estilizadas y saltos de línea explícitos para garantizar que en **Mermaid Live Editor**, **VS Code** y **GitHub** se vean alineados, nítidos y sin solapamiento de texto.

---

## 1. Nivel 1: Diagrama de Contexto del Sistema (System Context)

El diagrama de contexto muestra el sistema **The Playbook** en el centro, sus usuarios principales y la interacción con fuentes de datos e infraestructura de IA.

```mermaid
flowchart TB
    subgraph USERS["👥 Usuarios del Sistema"]
        U1["<b>Aficionado / Analista Amateur</b><br/><i>(Usuario Principal)</i><br/>Consulta predicciones 1X2/OU/BTTS,<br/>explicaciones RAG y audita el track record."]
        U2["<b>Administrador / Equipo</b><br/><i>(DevOps / MLOps)</i><br/>Supervisa experimentos en MLflow,<br/>scrapers y salud del pipeline RAG."]
    end

    subgraph SYSTEM["⚽ Sistema Central"]
        P["<b>THE PLAYBOOK</b><br/><i>(Sistema Inteligente)</i><br/>Predice partidos, genera explicaciones<br/>en lenguaje natural (sin fuga temporal)<br/>y publica su historial auditable."]
    end

    subgraph EXTERNAL["🌐 Sistemas & Datos Externos"]
        E1["<b>APIs Operativas</b><br/><i>(API-Football / football-data.org)</i><br/>Fixtures, alineaciones y datos en vivo."]
        E2["<b>Datasets Históricos</b><br/><i>(Football-Data.co.uk / Kaggle DB)</i><br/>Resultados, eventos y cuotas multi-década."]
        E3["<b>AWS Bedrock</b><br/><i>(Claude LLM + Titan Embeddings V2)</i><br/>Converse API e Inferencia Vectorial."]
        E4["<b>Noticias & RSS Deportivos</b><br/><i>(Medios de Prensa)</i><br/>Contexto noticioso pre-partido."]
    end

    U1 -->|Consulta predicciones y explicaciones| P
    U2 -->|Supervisa métricas y experimentos| P

    P -->|1. Fetch de fixture operativo| E1
    P -->|2. Ingestión batch de datos históricos| E2
    P -->|3. Invocación de Embeddings y LLM| E3
    P -->|4. Scraping de contexto pre-partido| E4

    %% Estilos de Nodos
    style USERS fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#FFF
    style SYSTEM fill:#0F172A,stroke:#3B82F6,stroke-width:3px,color:#FFF
    style EXTERNAL fill:#1F2937,stroke:#64748B,stroke-width:2px,color:#FFF

    style U1 fill:#1D4ED8,stroke:#93C5FD,stroke-width:1px,color:#FFF
    style U2 fill:#1E40AF,stroke:#93C5FD,stroke-width:1px,color:#FFF
    style P fill:#0284C7,stroke:#38BDF8,stroke-width:2px,color:#FFF
    style E1 fill:#374151,stroke:#9CA3AF,color:#FFF
    style E2 fill:#374151,stroke:#9CA3AF,color:#FFF
    style E3 fill:#374151,stroke:#9CA3AF,color:#FFF
    style E4 fill:#374151,stroke:#9CA3AF,color:#FFF
```

---

## 2. Nivel 2: Diagrama de Contenedores (Container Diagram)

Describe la distribución de responsabilidades en procesos y servicios independientes para garantizar la separación de tareas intensivas (ML/RAG) respecto al API servidor HTTP.

```mermaid
flowchart TB
    USER["👤 <b>Usuario Web</b><br/><i>(Navegador Desktop / Mobile)</i>"]

    subgraph APP["🏰 Boundary: The Playbook System"]
        FE["🎨 <b>Frontend Web App</b><br/><i>Next.js 15 + TypeScript + Recharts</i><br/>Interfaz SSR/Client y Dashboards"]
        API["⚡ <b>Backend REST API</b><br/><i>FastAPI + Python 3.12 + Async SQLAlchemy</i><br/>Endpoints REST síncronos ligeros"]
        
        subgraph ASYNC["⚙️ Procesamiento Asíncrono"]
            WORKERS["👷 <b>Celery Workers & Beat</b><br/><i>Python 3.12 + Celery</i><br/>Scraping, Reindexado RAG, Entrenamiento ML"]
        end

        subgraph DATASTORE["💾 Almacenamiento & Caché"]
            DB[("🗄️ <b>PostgreSQL 16 + pgvector</b><br/>Tablas Relacionales + Embeddings")]
            REDIS[("⚡ <b>Redis 7</b><br/>Broker Celery + Caché de Explicaciones")]
            MLFLOW[("📊 <b>MLflow Store</b><br/>Métricas & Pesos de Ensamble ML")]
        end
    end

    subgraph EXT["🌐 Servicios Cloud & Externos"]
        BEDROCK["☁️ <b>AWS Bedrock Runtime</b><br/>Claude LLM + Titan Embeddings V2"]
        APIS["⚽ <b>API-Football / External RSS</b><br/>Fixtures & Noticias"]
    end

    USER -->|HTTPS / Navega UI| FE
    FE -->|Requests JSON REST| API
    
    API -->|Queries SQL Async| DB
    API -->|Caché Key-Value| REDIS
    API -->|Encola tareas asíncronas| REDIS

    WORKERS -->|Consume tareas de la cola| REDIS
    WORKERS -->|Persiste datos y vectores| DB
    WORKERS -->|Registra corridas de modelos| MLFLOW
    WORKERS -->|Fetch de fixtures y noticias| APIS
    WORKERS -->|Embeddings Titan V2 & Claude| BEDROCK
    API -.->|Fallback RAG directo| BEDROCK

    %% Estilos de Nodos
    style APP fill:#0F172A,stroke:#38BDF8,stroke-width:2px,color:#FFF
    style ASYNC fill:#1E293B,stroke:#F59E0B,stroke-width:1px,color:#FFF
    style DATASTORE fill:#1E293B,stroke:#10B981,stroke-width:1px,color:#FFF
    style EXT fill:#1E1B4B,stroke:#818CF8,stroke-width:1px,color:#FFF

    style USER fill:#2563EB,stroke:#60A5FA,color:#FFF
    style FE fill:#0284C7,stroke:#38BDF8,color:#FFF
    style API fill:#0D9488,stroke:#2DD4BF,color:#FFF
    style WORKERS fill:#D97706,stroke:#FBBF24,color:#FFF
    style DB fill:#059669,stroke:#34D399,color:#FFF
    style REDIS fill:#DC2626,stroke:#FCA5A5,color:#FFF
    style MLFLOW fill:#7C3AED,stroke:#C4B5FD,color:#FFF
    style BEDROCK fill:#4C1D95,stroke:#A78BFA,color:#FFF
    style APIS fill:#374151,stroke:#9CA3AF,color:#FFF
```

---

## 3. Nivel 3: Diagramas de Componentes (Component Diagrams)

### 3.1 Componentes del Backend API (`backend/app`)

```mermaid
flowchart TB
    subgraph ROUTERS["📡 Capa de Routers (FastAPI)"]
        R1["<b>Match Router</b><br/>GET /matches"]
        R2["<b>Prediction Router</b><br/>GET /predictions"]
        R3["<b>Track Record Router</b><br/>GET /track-record"]
    end

    subgraph SERVICES["🧠 Capa de Servicios de Negocio"]
        S1["<b>Match Service</b><br/>Filtro y orden de partidos"]
        S2["<b>Prediction Service</b><br/>Orquesta probabilidades y badges"]
        S3["<b>Explanation Service</b><br/>Orquesta RAG e integración Bedrock"]
        S4["<b>Track Record Service</b><br/>Cálculo de métricas de precisión"]
    end

    subgraph INFRA_COMP["🔧 Componentes de Infraestructura"]
        DB_SESS["<b>Async Session Manager</b><br/>SQLAlchemy 2.0 Async"]
        BEDROCK_C["<b>Bedrock Client</b><br/>Boto3 Converse API"]
        REDIS_C["<b>Redis Cache Adapter</b><br/>Gestor de expiración (TTL)"]
    end

    DB[("🗄️ PostgreSQL + pgvector")]
    REDIS[("⚡ Redis Cache")]
    BEDROCK["☁️ AWS Bedrock API"]

    R1 --> S1
    R2 --> S2
    R3 --> S4

    S2 --> S3
    S2 --> REDIS_C
    S3 --> REDIS_C

    S1 --> DB_SESS
    S2 --> DB_SESS
    S4 --> DB_SESS
    S3 --> DB_SESS
    S3 --> BEDROCK_C

    DB_SESS --> DB
    REDIS_C --> REDIS
    BEDROCK_C --> BEDROCK

    %% Estilos
    style ROUTERS fill:#1E293B,stroke:#38BDF8,color:#FFF
    style SERVICES fill:#0F172A,stroke:#3B82F6,color:#FFF
    style INFRA_COMP fill:#1E293B,stroke:#10B981,color:#FFF
    
    style R1 fill:#0284C7,color:#FFF
    style R2 fill:#0284C7,color:#FFF
    style R3 fill:#0284C7,color:#FFF

    style S1 fill:#0D9488,color:#FFF
    style S2 fill:#0D9488,color:#FFF
    style S3 fill:#0D9488,color:#FFF
    style S4 fill:#0D9488,color:#FFF
```

---

### 3.2 Componentes del Subsistema de ML (`backend/ml`)

```mermaid
flowchart TB
    subgraph DATA_PREP["📥 Preparación de Datos & Features"]
        LOADER["<b>Data Loader</b><br/>Carga CSV Football-Data / Kaggle"]
        FENG["<b>Feature Extractor</b><br/>Métricas EWM, forma, H2H y descanso"]
    end

    subgraph MODELS["🤖 Modelos del Ensamble"]
        DC["<b>Dixon-Coles Model</b><br/>Prior estadístico Poisson bivariado"]
        XGB["<b>XGBoost Classifier</b><br/>Modelo ML no lineal de features"]
        ENS["<b>Ensemble Engine</b><br/>Promedio ponderado por Log-Loss"]
    end

    subgraph EVAL["📊 Evaluación & Explicabilidad"]
        SHAP_COMP["<b>SHAP Explainer</b><br/>TreeExplainer sobre XGBoost"]
        EVALUATOR["<b>Model Evaluator</b><br/>Log-Loss, Brier Score y Backtesting"]
        MLFLOW_C["<b>MLflow Tracker</b><br/>Registro de experimentos"]
    end

    DB[("🗄️ PostgreSQL")]
    MLFLOW_S[("📊 MLflow Server")]

    LOADER --> FENG
    FENG --> DC
    FENG --> XGB

    DC -->|Prior 1X2 / OU| ENS
    XGB -->|Probabilidades ML| ENS

    ENS --> EVALUATOR
    XGB --> SHAP_COMP
    EVALUATOR --> MLFLOW_C
    ENS --> DB
    MLFLOW_C --> MLFLOW_S

    %% Estilos
    style DATA_PREP fill:#1E293B,stroke:#38BDF8,color:#FFF
    style MODELS fill:#0F172A,stroke:#F59E0B,color:#FFF
    style EVAL fill:#1E293B,stroke:#10B981,color:#FFF

    style DC fill:#D97706,color:#FFF
    style XGB fill:#D97706,color:#FFF
    style ENS fill:#B45309,color:#FFF
```

---

### 3.3 Componentes del Subsistema RAG (`backend/rag`)

```mermaid
flowchart TB
    subgraph INGESTION["📰 Ingestión & Vectorización"]
        SCRAPER["<b>News Scraper</b><br/>Crawling de noticias pre-partido"]
        CHUNKER["<b>Article Chunker</b><br/>Chunks ~500 tokens / 15% overlap"]
        TITAN["<b>Titan Embedder</b><br/>Embeddings V2 de 1024d"]
    end

    subgraph RETRIEVAL_GEN["🔍 Retrieval & Generación Temporal"]
        RETRIEVER["<b>Temporal Retriever</b><br/>Búsqueda vectorial con<br/>WHERE fecha_noticia < kickoff"]
        CLAUDE_GEN["<b>Claude Generator</b><br/>Prompting estructurado con Converse API"]
        CACHE_MGR["<b>Explanation Cache</b><br/>Almacenamiento en Redis (TTL 24h)"]
    end

    PGVECTOR[("🗄️ pgvector (PostgreSQL)")]
    REDIS[("⚡ Redis Cache")]
    BEDROCK["☁️ AWS Bedrock"]

    SCRAPER --> CHUNKER
    CHUNKER --> TITAN
    TITAN --> PGVECTOR

    RETRIEVER -->|Vector Query| PGVECTOR
    RETRIEVER -->|Evidencia pre-partido| CLAUDE_GEN
    CLAUDE_GEN --> BEDROCK
    CLAUDE_GEN --> CACHE_MGR
    CACHE_MGR --> REDIS

    %% Estilos
    style INGESTION fill:#1E293B,stroke:#38BDF8,color:#FFF
    style RETRIEVAL_GEN fill:#0F172A,stroke:#A78BFA,color:#FFF

    style SCRAPER fill:#0284C7,color:#FFF
    style CHUNKER fill:#0284C7,color:#FFF
    style TITAN fill:#4C1D95,color:#FFF

    style RETRIEVER fill:#7C3AED,color:#FFF
    style CLAUDE_GEN fill:#6D28D9,color:#FFF
    style CACHE_MGR fill:#DC2626,color:#FFF
```

---

## 4. Nivel 4: Despliegue y Flujo de Datos Temporal (Deployment & Data Flow)

### 4.1 Diagrama de Despliegue (Deployment Diagram)

```mermaid
flowchart TB
    subgraph VERCEL["☁️ Vercel Cloud Platform"]
        NEXT["🎨 <b>Next.js Frontend Container</b><br/>Renderizado SSR / Edge Client"]
    end

    subgraph CLOUD_HOST["🐳 Host de Aplicación (Docker Engine / ECS Fargate)"]
        subgraph CONT_API["Contenedor FastAPI"]
            API_PROC["⚡ <b>FastAPI Process</b><br/>Port 8000"]
        end

        subgraph CONT_WORKER["Contenedor Celery Worker"]
            WORKER_PROC["👷 <b>Celery Worker Process</b>"]
        end

        subgraph CONT_BEAT["Contenedor Celery Beat"]
            BEAT_PROC["⏰ <b>Celery Beat Scheduler</b>"]
        end

        subgraph CONT_DB["Contenedor PostgreSQL"]
            PG_ENGINE[("🗄️ <b>PostgreSQL 16 + pgvector</b><br/>Port 5432")]
        end

        subgraph CONT_REDIS["Contenedor Redis"]
            REDIS_ENGINE[("⚡ <b>Redis 7</b><br/>Port 6379")]
        end
    end

    subgraph AWS["☁️ AWS Cloud Services"]
        BEDROCK_SRV["🧠 <b>AWS Bedrock Runtime</b><br/>Claude & Titan V2"]
    end

    NEXT -->|HTTPS REST| API_PROC
    API_PROC -->|Async SQL| PG_ENGINE
    API_PROC -->|Caché & Task Push| REDIS_ENGINE
    
    WORKER_PROC -->|Task Pull| REDIS_ENGINE
    WORKER_PROC -->|Bulk Reads/Writes| PG_ENGINE
    BEAT_PROC -->|Cron Triggers| REDIS_ENGINE
    
    WORKER_PROC -->|Boto3 / IAM Auth| BEDROCK_SRV
    API_PROC -->|Converse API| BEDROCK_SRV

    %% Estilos
    style VERCEL fill:#1E293B,stroke:#38BDF8,color:#FFF
    style CLOUD_HOST fill:#0F172A,stroke:#10B981,color:#FFF
    style AWS fill:#1E1B4B,stroke:#818CF8,color:#FFF

    style NEXT fill:#0284C7,color:#FFF
    style API_PROC fill:#0D9488,color:#FFF
    style WORKER_PROC fill:#D97706,color:#FFF
    style BEAT_PROC fill:#B45309,color:#FFF
    style PG_ENGINE fill:#059669,color:#FFF
    style REDIS_ENGINE fill:#DC2626,color:#FFF
    style BEDROCK_SRV fill:#4C1D95,color:#FFF
```

---

### 4.2 Diagrama de Secuencia: Flujo Temporal Honesto de RAG

Garantía estricta de que **ninguna evidencia posterior al kickoff del partido ingresa al LLM**.

```mermaid
sequenceDiagram
    autonumber
    actor User as Usuario Web
    participant FE as Frontend Next.js
    participant API as FastAPI Backend
    participant Cache as Redis Cache
    participant DB as PostgreSQL (pgvector)
    participant Bedrock as AWS Bedrock (Claude)

    User->>FE: Solicita detalle y explicación del Partido X
    FE->>API: GET /api/v1/predictions/{match_id}/explanation
    API->>Cache: GET exp:{match_id}
    
    alt Explicación encontrada en Caché
        Cache-->>API: Retorna Explicación JSON (Cache Hit)
        API-->>FE: 200 OK (Explicación entregada)
        FE-->>User: Muestra explicación en lenguaje natural
    else Caché Miss (Generación RAG)
        Cache-->>API: null (Cache Miss)
        API->>DB: SELECT kickoff_time FROM partidos WHERE id = match_id
        DB-->>API: Retorna fecha_kickoff = "2026-09-20 18:00:00"
        
        Note over API,DB: RESTRICCIÓN OBLIGATORIA DE SEGURIDAD TEMPORAL<br/>WHERE fecha_publicacion < fecha_kickoff
        API->>DB: Query vectorial pgvector con filtro temporal (fecha_noticia < kickoff_time)
        DB-->>API: Retorna top-K noticias relevantes pre-partido
        
        alt Evidencia encontrada
            API->>Bedrock: Invocación Converse API (Prompt + Evidencia pre-partido)
            Bedrock-->>API: Explicación estructurada citando fuentes reales
        else Sin evidencia pre-partido suficiente
            Note over API,Bedrock: Regla de Fallback Transparente
            API->>Bedrock: Invocación Converse API indicando falta de evidencia específica
            Bedrock-->>API: Declaración explícita de ausencia de contexto noticioso
        end
        
        API->>Cache: SET exp:{match_id} (TTL 24h)
        API-->>FE: 200 OK (Explicación generada)
        FE-->>User: Muestra explicación honesta y auditable
    end
```

---

## 5. Resumen de Decisiones Clave de Arquitectura (ADR Summary)

| ID ADR | Título | Decisión / Razón |
|---|---|---|
| [ADR 0001](adr/0001-badge-confianza-calibrado.md) | Badge de Confianza Calibrado | El nivel de confianza (Alta/Media/Baja) se obtiene de la precisión histórica real calibrada en ese rango de probabilidad (backtesting cronológico), **nunca** de la distancia a una distribución uniforme (33/33/33). |
| Spec §4 | Aislamiento de Procesos | Ningún job pesado de reentrenamiento de ML o reindexado RAG se ejecuta en el proceso HTTP de FastAPI. Todo se canaliza mediante Celery Workers independientes. |
| Spec §5.1 | AWS Bedrock Standalone | Claude vía Converse API y Amazon Titan Text Embeddings V2 están centralizados en AWS Bedrock con autenticación gestionada mediante roles IAM. |
| Spec §6.4 | Ensamble Ponderado | Combinación de la distribución prior de Dixon-Coles con el modelo XGBoost mediante promedio ponderado ajustado por log-loss en validación cronológica. |
| Spec §7.3 | Filtro Temporal en Retrieval RAG | Restricción estricta a nivel de query (`fecha_noticia < fecha_kickoff`) para evitar fugas de información posterior al resultado. |
