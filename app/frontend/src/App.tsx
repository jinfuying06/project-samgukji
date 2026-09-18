import { useState } from "react";
import { EventOverview } from "./screens/EventOverview";
import { PersonComparison } from "./screens/PersonComparison";
import { ScoreBreakdown } from "./screens/ScoreBreakdown";
import { AskAI } from "./screens/AskAI";
import { Quest } from "./screens/Quest";
import { Quiz } from "./screens/Quiz";

type Screen =
  | { name: "overview" }
  | { name: "comparison"; personId: string; personName: string }
  | { name: "score"; personId?: string }
  | { name: "ask" }
  | { name: "quest" }
  | { name: "quiz" };

const EVENT_ID = "event.chibi";

/**
 * Minimal state-based screen switcher — no router library needed for a 6-screen
 * single-event vertical slice (app/architecture/system.md: no unjustified complexity).
 */
export function App() {
  const [screen, setScreen] = useState<Screen>({ name: "overview" });

  return (
    <main className="tkaf-app">
      <header className="app-header">
        <span className="app-title">TKAF</span>
        <span className="app-subtitle">삼국지 데이터 아카이브 · 적벽대전</span>
      </header>
      <nav aria-label="화면 이동" className="app-nav">
        <button
          type="button"
          className={screen.name === "overview" ? "active" : undefined}
          aria-current={screen.name === "overview" ? "page" : undefined}
          onClick={() => setScreen({ name: "overview" })}
        >
          사건 개요
        </button>
        <button
          type="button"
          className={screen.name === "score" ? "active" : undefined}
          aria-current={screen.name === "score" ? "page" : undefined}
          onClick={() => setScreen({ name: "score" })}
        >
          점수 분해
        </button>
        <button
          type="button"
          className={screen.name === "ask" ? "active" : undefined}
          aria-current={screen.name === "ask" ? "page" : undefined}
          onClick={() => setScreen({ name: "ask" })}
        >
          AI 질문
        </button>
      </nav>
      <div className="app-screen">

      {screen.name === "overview" && (
        <EventOverview
          eventId={EVENT_ID}
          onSelectPerson={(personId) => setScreen({ name: "comparison", personId, personName: personId })}
          onStartQuest={() => setScreen({ name: "quest" })}
        />
      )}
      {screen.name === "comparison" && (
        <PersonComparison
          personId={screen.personId}
          personName={screen.personName}
          onAskAI={() => setScreen({ name: "ask" })}
        />
      )}
      {screen.name === "score" && <ScoreBreakdown eventId={EVENT_ID} personId={screen.personId} />}
      {screen.name === "ask" && <AskAI eventId={EVENT_ID} />}
      {screen.name === "quest" && <Quest onOpenEvidence={() => undefined} onComplete={() => setScreen({ name: "quiz" })} />}
      {screen.name === "quiz" && <Quiz />}
      </div>
    </main>
  );
}
