# Review notes

Version 1.1, 8 November 2026. These notes record what changed from the Version 1.0 manuscript of 7 November 2026, and what remains unresolved. The source used for this revision was the author's PDF. No Word original was required.

## What the revision does not claim

The paper still specifies a runtime contract and an evaluation protocol. It does not report an implementation of that protocol, a machine-checked proof, a benchmark result, or a performance improvement. Propositions 1 and 2 remain conditional. The proof sketches remain sketches. The experiments in Section 9 remain proposed. The paper does not claim to have invented swarms, durable execution, goal preservation, or verification-aware planning.

## Manuscript corrections

The Version 1.0 PDF drew Equations 5–7 with implication and universal-quantifier symbols in the text layer, but the rendered glyphs were missing. Version 1.1 restores those symbols. Equation 4 keeps the disjoint union, and the star stays on the discharge set. Equation 5 keeps the revision subscript. Equations 6 and 7 still quantify over a selected snapshot and decision time without a second revision index. A sentence in Section 6.2 states that convention so the missing subscript is not mistaken for a broken glyph.

Section 3.1 now names each component of Equations 1 and 2. The superscript is the contract version. The subscript is the committed runtime revision.

One sentence in the introduction states that an accepted obligation is not a proof of user intent, and that snapshot acceptance is not mission closure. Those distinctions were already in Sections 3.1, 5.2, and 6.1.

One sentence in Section 3.2 states that applicability fails when the selected artifact, a declared dependency, the acceptance policy, or a relevant external condition no longer matches. That sentence uses only the conditions already stated in Sections 3.2 and 5.2.

One sentence in Section 9.3 states that a larger budget, a weaker contract, or a success-only metric is not an improvement under the protocol.

The Version 1.0 PDF contained captions for Figures 1 and 2 and blank drawings. Version 1.1 supplies schematic drawings that follow those captions. They are illustrations, not experimental traces, and not recovered original artwork. Table 2 is one table with a repeating header, so the Version 1.0 header fragment does not reappear after Table 3.

## Reference and source checks

Reference access dates for living documentation remain 7 November 2026. Where a source was opened again, the note says so.

- van Lamsweerde 2001 is cited by DOI 10.1109/ISRE.2001.948567. Page numbers were not in the original and were not added.
- Tomašev, Franklin, and Osindero, arXiv:2602.11865v1, is cited at https://arxiv.org/abs/2602.11865.
- Xu, Zhang, Mitra, and Hruschka, EACL 2026, pages 7528–7546, DOI 10.18653/v1/2026.eacl-long.353, is cited with the anthology paper, the megagonlabs/veriMAP code, and preprint arXiv:2510.17109.
- Shen and coauthors, arXiv:2610.39193v1, remains prior art. The preprint is still not treated as an independently inspected public implementation or benchmark.
- Ciliberto, Rudi, and Tassi, arXiv:2610.28484v1. The program page was recorded on 7 November 2026 as describing mechanization and code as forthcoming. That page was not opened again for this revision.
- LangGraph persistence and the Microsoft Agent Framework Durable Extension keep the 7 November 2026 access dates. Crash durability for LangGraph still depends on the storage backend.
- AgentLedger is cited for durable execution, a tool ledger, evidence, replay, and policy. The prose does not add lease or fencing mechanics beyond that description.
- OpenWOP. The Version 1.0 sentence attributed an optional standing-goal capability by that flag name. This revision does not treat that name as a separately checked feature. It retains child-run dispatch, together with interruption, replay, and idempotency, and it still separates published interoperability evidence from independent ecosystem adoption.
- Codex Supervisor was reconfirmed at commit 87844d8396f4af73c2be2df6728131f07be62a73 on 8 November 2026. The README at that revision says a product write opens bounded verification debt, a later observed successful validation clears it, and a confirmed completion claim requires a current final-regression certificate. The original access date remains 7 November 2026. The paper uses that repository's wording rather than a looser paraphrase.
- FlowMemory's Obligation Membrane. The paraphrase "changed root constraints" is replaced by the repository's term "rootfield drift." The component remains a local prototype. The cited document is `docs/OBLIGATION_MEMBRANE.md` in FlowmemoryAI/flowmemory-uniswap-v4-hooks.
- Gray and Cheriton, SOSP 1989, pages 202–210, DOI 10.1145/74850.74870. The pages and proceedings DOI were checked against the published bibliographic record for that symposium. The SIGOPS Operating Systems Review reprint uses a different DOI and is not the one cited here.
- Pegasus controller and broker. Both commit objects exist: development `c581ed9bf079c5923b34004d02ad82dbd183fb82` (2026-11-07) and main `6e389d3fe43315918ef29e515d42bcc643acd6fb` (2026-11-03). The 7 November 2026 comparison base remains main at that commit. On 8 November 2026 the same objects were re-read. The controller file is `integrations/agent_control.py` and the broker file is `integrations/adaptive_tools.py`, both at the development commit. This was not a new diff against main and not an inspection of a newer tree or of an installed binary.

The controller re-reading supports these narrower statements, which replace the Version 1.0 wording:

- Four spawns were counted in a parent turn, and another spawn was then refused.
- A slot was returned for a timed-out, failed, stopped, interrupted, or incomplete run, and was not returned for a finished run. The user-facing refusal string mentions only timed-out or failed runs. The paper follows the release function, which also returns stopped, interrupted, and incomplete runs.
- Queue admission checked whether any run occupied the shared model slot. It did not partition capacity by endpoint.
- A further continuation was refused when the recorded continuation index reached 2.
- Ownership checks used the parent process identifier and chat identifier. Provider release also checked the execution identifier and continuation index. The Version 1.0 phrase "exact parent process and chat turn" was slightly stronger than those fields.

The broker re-reading supports mediated authorized leaf operations, recorded uncertain outcomes, and refusal of nested dispatch and delegation wrappers including `pegasus_agents`, `delegate_task`, and related tool-call names.

The public repository that holds this paper does not include the Pegasus application. The commit URLs are in the references with full hashes. If that application repository is private, a public reader may be unable to open those URLs. The hashes in the reference text are the inspection record.

## Unresolved limitations

- The continuity kernel, ownership epochs, evidence invalidation, and verification-aware admission policy are specified, not implemented or measured.
- Propositions 1 and 2 are conditional. They are not model-checked proofs, and they do not establish that a natural-language request was formalized correctly.
- Semantic soundness still depends on sound checkers, sound refinements, and satisfied assumptions. Heuristic checks remain policy application rather than semantic truth.
- Declared dependency tracking can miss a material input or invalidate too much. External state without a stable version is unsolved.
- Exactly-once external effects still require downstream support. A lease expiry still does not prove that an external process has stopped. A portable checkpoint still does not carry opaque provider reasoning.
- The scheduling estimates are estimates in one declared unit. They are not a bound on the number of agents.
- No fair comparison has been run. Matched budgets, the same contract, held-out checks, and all outcome categories are protocol requirements, not reported findings.
- The Proof-Carrying Contracts code status was not rechecked after 7 November 2026.
- The AgentLedger lease and fencing behavior was not re-specified from a fresh reading of that repository.
- Main commit `6e389d3` was confirmed to exist. It was not re-diffed on 8 November 2026.
- Gray and Cheriton pages were confirmed from the symposium bibliography, not from a scan of the proceedings PDF.
