# Data Access Policy

This document describes how each registered source may be accessed. **Do not bypass authentication, robots restrictions, paywalls, or access controls.**

Configuration flags and credentials belong in `.env` (see `.env.example`).

## Source priority (retrieval ranking)

1. Indian government regulations/guidelines  
2. National Centre for Seismology (NCS)  
3. Ministry of Home Affairs (MHA)  
4. NDMA  
5. NIDM  
6. NDRF  
7. Geological Survey of India  
8. IMD  
9. Census of India  
10. State governments  
11. Official historical reports  
12. Peer-reviewed academic research  
13. Other sources  

## Registered sources

| Source ID | Authority | Data type | Access method | Auth | Permission | Update | Local path |
|-----------|-----------|-----------|---------------|------|------------|--------|------------|
| `ncs_earthquake_archive` | NCS | Structured events | Official site / manual CSV | No | No | Daily | `data/raw/ncs/{date}/` |
| `nidm_earthquake_guidelines` | NIDM | PDF/HTML guidelines | Manual or URL-triggered | No | No | As published | `data/raw/nidm/` |
| `ndma_ndmp` | NDMA | Plans, policies | Manual | No | No | As published | `data/raw/ndma/` |
| `mha_disaster_management` | MHA | Reports, SDRF/NDRF guidance | Manual | No | No | As published | `data/raw/mha/` |
| `ndrf_operation_reports` | NDRF | Operation reports | Manual | No | No | As published | `data/raw/ndrf/` |
| `ndrr_reserve_stocks` | NDRR | Reserve quantities | Manual | No | No | As published | `data/raw/ndrr/` |
| `idrn_resources` | IDRN | Equipment availability | Manual; verify public use | No | **Yes** | Unknown | `data/raw/idrn/` |
| `gsi_bhukosh` | GSI | Geology/seismic | Manual / Bhukosh portal | No | No | As published | `data/raw/gsi/` |
| `census_india` | Census | Demographics | Manual official tables | No | No | Decadal | `data/raw/census/` |
| `imd_weather` | IMD | Weather/climate | Manual; API if licensed | API key optional | No | Daily | `data/raw/imd/` |
| `survey_of_india` | SoI | Terrain/admin geography | Manual | No | **May require** | As published | `data/raw/survey_of_india/` |
| `bhuvan_isro` | ISRO | DEM/satellite | Bhuvan registration | Registration | **Yes** | As published | `data/raw/bhuvan/` |
| `ncrb_casualties` | NCRB | Casualty statistics | Manual | No | No | Annual | `data/raw/ncrb/` |
| `state_sdmps` | States | SDMPs, relief manuals | Manual per state | No | No | As published | `data/raw/state/{state}/` |
| `historical_earthquake_reports` | Mixed | Case reports | Manual | No | No | As published | `data/raw/historical_reports/` |

## Ingestion modes

- **Mode A — Automatic**: HTTP download when an official endpoint is configured in the source adapter and `download_method` is `api` or `url_download`.
- **Mode B — Manual snapshot**: Place CSV/PDF/JSON under `data/raw/{source_id}/` or dated subfolders; run `POST /data/sync/{source_id}`.
- **Mode C — URL-based document ingestion**: Register URL in document metadata; trigger download via sync when explicitly enabled for that document.

## Provenance

Every raw file is stored under `data/raw/{source}/{YYYY-MM-DD}/` with:

- Original filename  
- `metadata.json`: source URL, download timestamp, SHA-256 checksum, authority, license notes  

Processed normalized outputs go to `data/processed/`. Previous versions are retained in `data_versions` (database).

## NCS note

An official public REST API for all NCS fields is **not assumed**. The `ncs` adapter attempts configurable URL download when `NCS_EVENTS_URL` is set in `.env`; otherwise use manual CSV/JSON export placed in `data/raw/ncs/`.

## Training data (WOA-BP)

Population model training files are **not bundled**. Set `WOA_BP_TRAINING_DATA_PATH` to a CSV you provide with documented features and target. Without training data, the model runs in `not_trained` mode and population must be **reported** or **unknown**.
