# License policy

SoundBench is a public research-tool repository. Repository placement and
exclusion from product builds do not remove dependency or distribution license
obligations.

## Repository default

SoundBench currently grants no blanket license across every future tool. Each
tool must include its own `LICENSE` before production code is committed. Files
outside a separately licensed tool remain under their authors' default rights
until the repository owner records a broader license.

## Tool review

Before adopting a direct dependency, record in the tool's
`THIRD_PARTY_NOTICES.md`:

- package name, resolved version, and authoritative source;
- declared license and license-text location;
- how the dependency is used and whether it is linked, imported, invoked as a
  separate process, or used only during development;
- redistribution, attribution, source-offer, network-use, patent, data, model,
  or commercial-use obligations; and
- the decision and any required notices or source links.

Review relevant transitive dependencies as part of the locked environment.

## Decision rules

- Permissive open-source dependencies are normally acceptable when their notice
  and attribution requirements are satisfied.
- Copyleft, source-available, noncommercial, research-only, proprietary, data,
  and model licenses require an explicit tool-local compatibility decision.
- Public distribution must satisfy the selected tool license and every
  applicable dependency obligation.
- A tool with broader obligations must remain isolated from tools or product
  code whose license is incompatible with those obligations.
- Missing, unclear, contradictory, or unsatisfied terms are a stop condition.

This policy is engineering governance, not legal advice. Escalate material
uncertainty to the repository owner and qualified counsel when appropriate.
