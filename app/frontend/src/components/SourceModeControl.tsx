import type { SourceLayer } from "../api/types";

export type SourceModeValue = SourceLayer | "비교" | "게임";

const LAYER_LABEL: Record<SourceModeValue, string> = {
  HISTORY_BASE: "정사",
  HISTORY_ANNOTATION: "정사 주석",
  ROMANCE: "연의",
  LATER_INTERPRETATION: "연구·해석",
  GAME_DATA: "게임",
  비교: "비교",
  게임: "게임",
};

export interface SourceModeOption {
  value: SourceModeValue;
  disabled?: boolean;
  disabledReason?: string;
}

interface Props {
  options: SourceModeOption[];
  value: SourceModeValue;
  onChange: (value: SourceModeValue) => void;
  label?: string;
}

/**
 * design/component_spec.md `SourceModeControl`: roving-tabindex radiogroup, disabled options
 * stay focusable so their reason is reachable via aria-describedby, never color-only.
 */
export function SourceModeControl({ options, value, onChange, label = "출처 모드" }: Props) {
  return (
    <div role="radiogroup" aria-label={label} className="source-mode-control">
      {options.map((opt) => {
        const selected = opt.value === value;
        const describedBy = opt.disabled ? `smc-reason-${opt.value}` : undefined;
        return (
          <div key={opt.value} className="source-mode-option-wrap">
            <button
              type="button"
              role="radio"
              aria-checked={selected}
              aria-describedby={describedBy}
              disabled={false}
              aria-disabled={opt.disabled || undefined}
              tabIndex={selected ? 0 : -1}
              className={`source-mode-pill layer-${opt.value}${selected ? " selected" : ""}${
                opt.disabled ? " disabled" : ""
              }`}
              onClick={() => {
                if (!opt.disabled) onChange(opt.value);
              }}
              onKeyDown={(e) => {
                const idx = options.findIndex((o) => o.value === opt.value);
                if (e.key === "ArrowRight" || e.key === "ArrowDown") {
                  e.preventDefault();
                  const next = options[(idx + 1) % options.length];
                  onChange(next.disabled ? value : next.value);
                } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
                  e.preventDefault();
                  const prev = options[(idx - 1 + options.length) % options.length];
                  onChange(prev.disabled ? value : prev.value);
                }
              }}
            >
              {LAYER_LABEL[opt.value]}
            </button>
            {opt.disabled && opt.disabledReason && (
              <span id={`smc-reason-${opt.value}`} className="source-mode-reason" role="note">
                {opt.disabledReason}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
