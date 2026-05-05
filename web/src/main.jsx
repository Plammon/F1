import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const CALENDAR = [
  {
    track: "Albert Park",
    round: 1,
    event: "Australian Grand Prix",
    type: "Street/Hybrid",
    dna: "Medium-Speed / Flowing",
  },
  {
    track: "Shanghai",
    round: 2,
    event: "Chinese Grand Prix",
    type: "Permanent",
    dna: "Front-Limited / Technical",
  },
  {
    track: "Suzuka",
    round: 3,
    event: "Japanese Grand Prix",
    type: "Permanent",
    dna: "High-Speed-Flowing / Technical",
  },
  {
    track: "Miami",
    round: 4,
    event: "Miami Grand Prix",
    type: "Street/Hybrid",
    dna: "Traction / Long Straights",
  },
  {
    track: "Montreal",
    round: 5,
    event: "Canadian Grand Prix",
    type: "Street/Hybrid",
    dna: "Stop-and-Go / Heavy Braking",
  },
  {
    track: "Monaco",
    round: 6,
    event: "Monaco Grand Prix",
    type: "Street",
    dna: "Low-Speed / Max-Downforce",
  },
  {
    track: "Barcelona-Catalunya",
    round: 7,
    event: "Barcelona-Catalunya Grand Prix",
    type: "Permanent",
    dna: "Aerodynamic-Efficiency",
  },
  {
    track: "Red Bull Ring",
    round: 8,
    event: "Austrian Grand Prix",
    type: "Permanent",
    dna: "Power-Unit / Elevation-Changes",
  },
  {
    track: "Silverstone",
    round: 9,
    event: "British Grand Prix",
    type: "Permanent",
    dna: "Ultra-High-Speed / Aero-Load",
  },
  {
    track: "Spa",
    round: 10,
    event: "Belgian Grand Prix",
    type: "Permanent",
    dna: "Power-Unit / Long-Straights",
  },
  {
    track: "Hungaroring",
    round: 11,
    event: "Hungarian Grand Prix",
    type: "Permanent",
    dna: "High-Downforce / Slow-Speed",
  },
  {
    track: "Zandvoort",
    round: 12,
    event: "Dutch Grand Prix",
    type: "Permanent",
    dna: "High-Downforce / Banking",
  },
  {
    track: "Monza",
    round: 13,
    event: "Italian Grand Prix",
    type: "Permanent",
    dna: "Top-Speed / Ultra-Low-Drag",
  },
  {
    track: "Madrid",
    round: 14,
    event: "Spanish Grand Prix",
    type: "Street/Hybrid",
    dna: "Mixed / Flowing-Esses",
    note: "Madrid is new for 2026, so the model uses the historical Spanish GP as its nearest GP proxy.",
  },
  {
    track: "Baku",
    round: 15,
    event: "Azerbaijan Grand Prix",
    type: "Street",
    dna: "Top-Speed / 90-Degree-Turns",
  },
  {
    track: "Singapore",
    round: 16,
    event: "Singapore Grand Prix",
    type: "Street",
    dna: "Traction / Humidity / Slow-Speed",
  },
  {
    track: "COTA",
    round: 17,
    event: "United States Grand Prix",
    type: "Permanent",
    dna: "Mixed / Flowing-Esses",
  },
  {
    track: "Mexico City",
    round: 18,
    event: "Mexico City Grand Prix",
    type: "Permanent",
    dna: "High-Altitude / Low-Air-Density",
  },
  {
    track: "Interlagos",
    round: 19,
    event: "Sao Paulo Grand Prix",
    type: "Permanent",
    dna: "Elevation / Mixed / Short-Lap",
  },
  {
    track: "Las Vegas",
    round: 20,
    event: "Las Vegas Grand Prix",
    type: "Street",
    dna: "Top-Speed / Low-Tire-Temp",
  },
  {
    track: "Lusail",
    round: 21,
    event: "Qatar Grand Prix",
    type: "Permanent",
    dna: "High-Speed / High-G-Force",
  },
  {
    track: "Yas Marina",
    round: 22,
    event: "Abu Dhabi Grand Prix",
    type: "Permanent",
    dna: "Traction / Technical / Slow-Exit",
  },
];

const TEAM_COLORS = {
  Mercedes: "#00a19b",
  McLaren: "#ff8000",
  Ferrari: "#e80020",
  "Red Bull Racing": "#3864ff",
  Alpine: "#0090ff",
  Audi: "#9aa3aa",
  "Racing Bulls": "#6692ff",
  Haas: "#b6babd",
  Williams: "#00a3e0",
  "Aston Martin": "#006f62",
  Cadillac: "#b9975b",
};

const MODE_OPTIONS = [
  { value: "qualifying", label: "Qualifying" },
  { value: "race", label: "Race" },
];

const WEATHER_OPTIONS = [
  { value: "0", label: "Dry" },
  { value: "1", label: "Wet" },
];

const VIEW_OPTIONS = [
  { value: "ranking", label: "Ranking" },
  { value: "probabilities", label: "Win %" },
];

function App() {
  const [track, setTrack] = useState(CALENDAR[0].track);
  const [mode, setMode] = useState("qualifying");
  const [rain, setRain] = useState("0");
  const [view, setView] = useState("ranking");
  const [prediction, setPrediction] = useState(null);
  const [status, setStatus] = useState("checking");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const predictionRequestId = useRef(0);

  const activeEvent = useMemo(
    () => CALENDAR.find((item) => item.track === track) ?? CALENDAR[0],
    [track],
  );

  useEffect(() => {
    let ignore = false;

    fetch("/health", { headers: { Accept: "application/json" } })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Health check returned ${response.status}`);
        }
        return response.json();
      })
      .then(() => {
        if (!ignore) {
          setStatus("online");
        }
      })
      .catch(() => {
        if (!ignore) {
          setStatus("offline");
        }
      });

    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    loadPrediction({ track, mode, rain, view }, { signal: controller.signal });

    return () => controller.abort();
  }, [track, mode, rain, view]);

  function loadPrediction(scenario, { signal } = {}) {
    const requestId = predictionRequestId.current + 1;
    predictionRequestId.current = requestId;
    const params = new URLSearchParams(scenario);

    setLoading(true);
    setError("");
    setPrediction(null);

    return fetch(`/api/predict?${params.toString()}`, {
      method: "GET",
      signal,
      headers: { Accept: "application/json" },
    })
      .then((response) =>
        response.json().then((payload) => {
          if (!response.ok) {
            throw new Error(payload.detail || payload.error || `Prediction request returned ${response.status}`);
          }
          return payload;
        }),
      )
      .then((payload) => {
        if (requestId !== predictionRequestId.current) {
          return;
        }
        setPrediction(payload);
        setLoading(false);
      })
      .catch((requestError) => {
        if (requestError.name === "AbortError" || requestId !== predictionRequestId.current) {
          return;
        }
        setPrediction(null);
        setError(`Prediction data could not be loaded. ${requestError.message}`);
        setLoading(false);
      });
  }

  function handleUpdateData() {
    loadPrediction({ track, mode, rain, view });
  }

  const rows = prediction?.results ?? [];
  const leader = rows[0];
  const runnerUp = rows[1];
  const generatedAt = prediction?.generated_at_utc
    ? formatDate(prediction.generated_at_utc)
    : "Waiting for API";
  const statusLabel =
    status === "online" ? "API online" : status === "offline" ? "API offline" : "Checking API";
  const sessionLabel = mode === "qualifying" ? "Qualifying" : "Race";
  const weatherLabel = rain === "1" ? "Wet" : "Dry";
  const outputLabel = view === "ranking" ? "Classification" : "Win probability";

  return (
    <main className="race-console">
      <div className="ambient-track" aria-hidden="true" />
      <header className="global-header">
        <div className="brand-lockup">
          <span className="brand-mark">
            <span>F1</span>
          </span>
          <div>
            <p className="eyebrow">Race intelligence dashboard</p>
            <h1>F1 2026 Prediction Center</h1>
            <p className="header-subtitle">
              Round {padRound(activeEvent.round)} / {activeEvent.event}
            </p>
          </div>
        </div>

        <div className="header-telemetry" aria-label="Application status">
          <StatusPill label={statusLabel} tone={status} />
          <DataBadge label="Calendar" value="22 rounds" />
          <DataBadge label="Generated" value={generatedAt} />
        </div>
      </header>

      <section className="console-layout" aria-label="Prediction console">
        <aside className="schedule-panel panel-section" aria-label="2026 Formula 1 calendar">
          <SectionHeading eyebrow="Calendar" title="2026 rounds" meta={`${CALENDAR.length}`} />
          <CalendarRail track={track} onSelect={setTrack} />
        </aside>

        <section className="prediction-stage panel-section" aria-live="polite">
          <div className="scenario-toolbar" aria-label="Prediction controls">
            <label className="field track-field">
              <span>Grand Prix</span>
              <select value={track} onChange={(event) => setTrack(event.target.value)}>
                {CALENDAR.map((item) => (
                  <option key={item.track} value={item.track}>
                    R{padRound(item.round)} - {item.event} ({item.track})
                  </option>
                ))}
              </select>
            </label>

            <SegmentedControl
              label="Session"
              options={MODE_OPTIONS}
              value={mode}
              onChange={setMode}
            />

            <SegmentedControl
              label="Weather"
              options={WEATHER_OPTIONS}
              value={rain}
              onChange={setRain}
            />

            <SegmentedControl
              label="Output"
              options={VIEW_OPTIONS}
              value={view}
              onChange={setView}
            />

            <div className="field update-field">
              <span>Data</span>
              <button
                type="button"
                className="update-data-button"
                onClick={handleUpdateData}
                disabled={loading}
                aria-label="Reload prediction data"
              >
                {loading ? "Loading" : "Reload data"}
              </button>
            </div>
          </div>

          <div className="stage-overview">
            <div className="event-visual">
              <img
                className="event-image"
                src="/background.png"
                alt=""
                onError={(event) => {
                  event.currentTarget.hidden = true;
                }}
              />
              <div className="visual-shade" />
              <div className="visual-grid" aria-hidden="true" />
              <div className="visual-copy">
                <span>Round {padRound(activeEvent.round)}</span>
                <h2>{activeEvent.track}</h2>
                <div className="visual-meta" aria-label="Circuit characteristics">
                  <span>{activeEvent.type}</span>
                  <span>{activeEvent.dna}</span>
                </div>
              </div>
              <div className="visual-readout" style={{ "--team-color": teamColor(leader?.team) }}>
                <span>Predicted P1</span>
                <strong>{leader?.driver ?? "Waiting"}</strong>
                <small>{leader?.team ?? "No result yet"}</small>
                <em>{leader ? formatPrimaryMetric(leader, view) : outputLabel}</em>
              </div>
            </div>

            <KeyMetrics
              leader={leader}
              runnerUp={runnerUp}
              rowCount={rows.length}
              view={view}
            />
          </div>

          <div className="results-heading">
            <div>
              <p className="eyebrow">{outputLabel}</p>
              <h3>{sessionLabel} / {weatherLabel}</h3>
            </div>
            <span>{rows.length} entries</span>
          </div>

          <ResultsArea loading={loading} error={error} rows={rows} view={view} />
        </section>

        <aside className="insight-panel panel-section" aria-label="Scenario context">
          <SectionHeading eyebrow="Scenario" title="Race setup" meta={weatherLabel} />

          <dl className="detail-list">
            <div>
              <dt>Event</dt>
              <dd>{activeEvent.event}</dd>
            </div>
            <div>
              <dt>Circuit type</dt>
              <dd>{activeEvent.type}</dd>
            </div>
            <div>
              <dt>Model DNA</dt>
              <dd>{activeEvent.dna}</dd>
            </div>
            <div>
              <dt>Output</dt>
              <dd>{outputLabel}</dd>
            </div>
          </dl>

          {activeEvent.note ? <p className="event-note">{activeEvent.note}</p> : null}

          <TopThree rows={rows} view={view} loading={loading} />
        </aside>
      </section>
    </main>
  );
}

function SectionHeading({ eyebrow, title, meta }) {
  return (
    <div className="section-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
      </div>
      {meta ? <span>{meta}</span> : null}
    </div>
  );
}

function StatusPill({ label, tone }) {
  return (
    <span className={`status-pill status-${tone}`}>
      <span aria-hidden="true" />
      {label}
    </span>
  );
}

function DataBadge({ label, value }) {
  return (
    <span className="data-badge">
      <small>{label}</small>
      <strong>{value}</strong>
    </span>
  );
}

function SegmentedControl({ label, options, value, onChange }) {
  return (
    <div className="field">
      <span>{label}</span>
      <div
        className="segmented"
        role="group"
        aria-label={label}
        style={{
          "--segments": options.length,
          "--active-offset": `${Math.max(
            0,
            options.findIndex((option) => option.value === value),
          ) * 100}%`,
        }}
      >
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            className={value === option.value ? "is-active" : ""}
            aria-pressed={value === option.value}
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function CalendarRail({ track, onSelect }) {
  return (
    <div className="schedule-list">
      {CALENDAR.map((item) => (
        <button
          key={item.track}
          type="button"
          className={track === item.track ? "is-selected" : ""}
          onClick={() => onSelect(item.track)}
          title={`${item.event} - ${item.track}`}
          style={{ "--round-progress": `${(item.round / CALENDAR.length) * 100}%` }}
        >
          <span>R{padRound(item.round)}</span>
          <strong>{item.track}</strong>
          <small>{item.event}</small>
        </button>
      ))}
    </div>
  );
}

function KeyMetrics({ leader, runnerUp, rowCount, view }) {
  const metricLabel = view === "ranking" ? "AI score" : "Win chance";

  return (
    <div className="key-metrics">
      <MetricTile
        label="Predicted P1"
        value={leader?.driver ?? "No driver"}
        detail={leader?.team ?? "No team"}
        team={leader?.team}
      />
      <MetricTile
        label="Closest challenger"
        value={runnerUp?.driver ?? "No driver"}
        detail={runnerUp?.team ?? "No team"}
        team={runnerUp?.team}
      />
      <MetricTile
        label={metricLabel}
        value={leader ? formatPrimaryMetric(leader, view) : "No result"}
        detail={`${rowCount} ranked entries`}
        team={leader?.team}
      />
    </div>
  );
}

function MetricTile({ label, value, detail, team }) {
  return (
    <div className="metric-tile" style={{ "--team-color": teamColor(team) }}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function ResultsArea({ loading, error, rows, view }) {
  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (rows.length === 0) {
    return <EmptyState />;
  }

  return <PredictionRows rows={rows} view={view} />;
}

function PredictionRows({ rows, view }) {
  const isProbability = view === "probabilities";

  return (
    <div
      className={`results-grid ${isProbability ? "probability-grid" : ""}`}
      role="table"
      aria-label={isProbability ? "Win probability ranking" : "Predicted classification"}
    >
      <div className="result-row result-head" role="row">
        <span role="columnheader">Pos</span>
        <span role="columnheader">Driver</span>
        <span role="columnheader">Team</span>
        <span role="columnheader">{isProbability ? "Win probability" : "AI score"}</span>
      </div>

      {rows.map((row, index) => (
        <div
          className="result-row"
          role="row"
          key={`${row.rank}-${row.driver}`}
          style={{
            "--team-color": teamColor(row.team),
            "--bar-width": `${normalizeWidth(row.width ?? row.probability)}%`,
            "--row-index": index,
          }}
        >
          <span className="position-cell" role="cell">
            <span>{row.rank}</span>
          </span>
          <span className="driver-cell" role="cell">
            <strong>{row.driver}</strong>
            <small>{row.team}</small>
          </span>
          <span className="team-cell" role="cell">
            <span aria-hidden="true" />
            {row.team}
          </span>
          <span className={isProbability ? "metric-cell metric-with-bar" : "metric-cell"} role="cell">
            {isProbability ? (
              <>
                <span className="probability-track" aria-hidden="true">
                  <span />
                </span>
                <strong>{row.probability}%</strong>
              </>
            ) : (
              <strong>{row.score}</strong>
            )}
          </span>
        </div>
      ))}
    </div>
  );
}

function TopThree({ rows, view, loading }) {
  const leaders = rows.slice(0, 3);

  return (
    <div className="top-three">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">Lead pack</p>
          <h2>Top 3</h2>
        </div>
      </div>

      {loading ? (
        <div className="mini-state">Loading</div>
      ) : leaders.length === 0 ? (
        <div className="mini-state">No entries</div>
      ) : (
        <div className="top-three-list">
          {leaders.map((row, index) => (
            <div
              className="top-three-row"
              key={`${row.rank}-${row.driver}`}
              style={{ "--team-color": teamColor(row.team), "--row-index": index }}
            >
              <span>{row.rank}</span>
              <div>
                <strong>{row.driver}</strong>
                <small>{row.team}</small>
              </div>
              <em>{formatPrimaryMetric(row, view)}</em>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function LoadingState() {
  return (
    <div className="state-block">
      <span className="loader-bars" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
      <strong>Loading prediction</strong>
      <span>Fetching the selected Grand Prix scenario.</span>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="state-block">
      <strong>No prediction rows returned</strong>
      <span>Try another session, weather condition, or output view.</span>
    </div>
  );
}

function ErrorState({ message }) {
  return (
    <div className="state-block state-error">
      <strong>Prediction unavailable</strong>
      <span>{message}</span>
    </div>
  );
}

function teamColor(team) {
  return TEAM_COLORS[team] ?? "#242832";
}

function normalizeWidth(value) {
  const numeric = Number.parseFloat(value);

  if (!Number.isFinite(numeric)) {
    return 0;
  }

  return Math.max(0, Math.min(100, numeric));
}

function padRound(round) {
  return String(round).padStart(2, "0");
}

function formatPrimaryMetric(row, view) {
  if (view === "probabilities") {
    return `${row.probability}%`;
  }
  return row.score;
}

function formatDate(value) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(date);
}

createRoot(document.getElementById("root")).render(<App />);
