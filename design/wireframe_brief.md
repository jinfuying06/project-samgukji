# Wireframe Brief

## Information hierarchy

1. `[Primary decision/result]`
2. `[Supporting evidence and uncertainty]`
3. `[Recommended next action]`
4. `[Methods, provenance, limitations]`

## Screen S-001

- User goal: `[TBD]`
- Entry/exit: `[TBD]`
- Primary content: `[TBD]`
- Primary action: `[TBD]`
- Secondary actions: `[TBD]`
- Trust cues: source, run time, population, uncertainty, limitations

### States

| State | Trigger | Content | Available action |
| --- | --- | --- | --- |
| Loading | request active | skeleton + plain status | cancel if supported |
| Empty | no eligible data | reason + requirements | return/upload/connect |
| Partial | incomplete result | available data + warning | retry/details |
| Error | failed request | safe summary + trace ID | retry/support |
| Stale | old result | timestamp + stale label | refresh |
| Refused | unsafe/unsupported | reason category | revise request/human review |

